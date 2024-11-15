from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from standard.models import Lot
from company.models import Company
import json

from . import requests
from . import payloads


class PublishPostView(APIView):
    def get(self, request, uuid):
        lot = get_object_or_404(Lot, uuid=uuid)
        answer = requests.lot_publish(lot)
        # payload = payloads.get_publish_payload(lot)
        return Response(data=answer.json(), status=status.HTTP_200_OK)


class ResultPostView(APIView):
    def get(self, request, uuid):
        lot = get_object_or_404(Lot, uuid=uuid)
        answer = requests.lot_result(lot)
        # payload = payloads.get_result_payload(lot)
        return Response(data=answer.json(), status=status.HTTP_200_OK)


class CompanyPostView(APIView):
    def get(self, request, id):
        company = get_object_or_404(Company, pk=id)
        answer = requests.company_create(company)
        # payload = payloads.get_company_payload(company)
        return Response(data=answer.json(), status=status.HTTP_200_OK)