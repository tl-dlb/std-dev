from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from standard.models import Lot, Bid

from datetime import datetime
from datetime import timedelta
from django.utils import timezone

import os
from io import BytesIO
from zipfile import ZipFile
from django.http import HttpResponse
from django.conf import settings
from .serializers import LotListSerializer



class BidListApi(APIView):  
    class ListSerializer(serializers.ModelSerializer):
        mine = serializers.SerializerMethodField()
        best = serializers.SerializerMethodField()
        company_name = serializers.SerializerMethodField()
        def get_mine(self, obj):
            return True if obj.application.company.id == self.context['company_id'] else False
        def get_best(self, obj):
            return True if obj.id == self.context['best_bid_id'] else False
        def get_company_name(self, obj):
            return obj.application.company.name if self.context['visible'] else None
            
        class Meta:
            model = Bid
            fields = ('id', 'sum', 'created_at', 'mine', 'best', 'company_name')

    def get(self, request, id):
        lot = get_object_or_404(Lot, pk=id)
        bids = Bid.objects.filter(lot=lot).exclude(application__status='WITHDRAWN').order_by('-created_at').all()
        if lot.type == 'AUCTION_DOWN':
            best_bid = bids.order_by('sum', 'created_at').first()
        elif lot.type == 'AUCTION_UP':
            best_bid = bids.order_by('-sum', 'created_at').first()

        user     = self.request.user
        company  = user.profile.company
        operator = user.groups.filter(name='operator').exists()
        creator  = lot.company == company
        visible  = operator or creator

        serializer = self.ListSerializer(bids, context={
            'visible': visible,
            'company_id': None if operator else company.id,
            'best_bid_id': best_bid.id if best_bid else 0,
        }, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class LotDetailApi(APIView):  
    class DetailSerializer(serializers.ModelSerializer):
        bidding_begin_unix = serializers.SerializerMethodField()
        def get_bidding_begin_unix(self, obj):
            return obj.bidding_begin.timestamp()
        bidding_end_unix = serializers.SerializerMethodField()
        def get_bidding_end_unix(self, obj):
            return obj.bidding_end.timestamp()
        class Meta:
            model = Lot
            fields = ('id', 'bidding_begin', 'bidding_end', 'bidding_begin_unix', 'bidding_end_unix')

    def get(self, request, id):
        lot = get_object_or_404(Lot, pk=id)
        if lot.status == 'BIDDING':
            serializer = self.DetailSerializer(lot)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)


class AnnouncementsApi(APIView):  
    def get(self, request):
        lots = Lot.objects.filter(Q(status='PUBLISHED') | Q(status='SUBMISSION') | Q(status='ADMISSION') | Q(status='ADMITTED')).order_by('-bidding_begin').all()
        serializer = LotListSerializer(lots, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ResultsApi(APIView):  
    def get(self, request):
        lots = Lot.objects.filter(Q(status='COMPLETED') | Q(status='NOT_COMPLETED') | Q(status='CANCELLED')).order_by('-bidding_begin').all()
        serializer = LotListSerializer(lots, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class ResultsApi_v2(APIView):  
    def get(self, request):
        lots = Lot.objects.filter(Q(status='COMPLETED') | Q(status='NOT_COMPLETED') | Q(status='CANCELLED')).order_by('-bidding_begin').all()
        if request.GET.get('bbg'):
            bid_bg = datetime.strptime(request.GET.get('bbg'), "%d.%m.%Y").date()
            lots = lots.filter(bidding_begin__gte=bid_bg)
        
        if request.GET.get('bbl'):
            bid_bl = datetime.strptime(request.GET.get('bbl'), "%d.%m.%Y").date()+timedelta(days=1)
            lots = lots.filter(bidding_begin__lte=bid_bl)

        serializer = LotListSerializer(lots, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

        

class LotFilesDownloadApi(APIView):
    def get(self, request, id):   
        lot = get_object_or_404(Lot, pk=id) 
        files = lot.files.all()
        if files.count() > 0:
            in_memory = BytesIO()
            zip = ZipFile(in_memory, 'a')
                
            os.chdir(os.path.join(settings.MEDIA_ROOT, 'storage'))
            for file in files:
                zip.write(os.path.basename(file.field.path), file.name.replace('/', '_'))
            
            # fix for Linux zip files read in Windows
            for file in zip.filelist:
                file.create_system = 0    
                
            zip.close()

            response = HttpResponse()
            response["Content-Disposition"] = "attachment; filename=documents.zip"
            
            in_memory.seek(0)    
            response.write(in_memory.read())
            
            return response
        return Response(status=status.HTTP_404_NOT_FOUND)