from django.urls import path
from . import apis


urlpatterns = [
    path('lot/<int:id>/bid/', apis.BidListApi.as_view(), name='api_lot_bid_list'),
    path('lot/<int:id>/', apis.LotDetailApi.as_view(), name='api_lot_detail'),

    path('lot/announcements/', apis.AnnouncementsApi.as_view(), name='api-lot-announcements'),
    path('lot/results/', apis.ResultsApi.as_view(), name='api-lot-results'),
    path('lot/results_2/', apis.ResultsApi_v2.as_view(), name='api-lot-results-2'),
    path('lot/<int:id>/files/download/', apis.LotFilesDownloadApi.as_view(), name='api-lot-files-download'),
]
