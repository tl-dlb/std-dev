from django.urls import path

from .views import (lot, position, application, bid, result, file, signature)

urlpatterns = [
    path('',                    lot.list,      name='lot_list'),
    path('create/',             lot.create,    name='lot_create'),
    path('<uuid:uuid>/',        lot.detail,    name='lot_detail'),
    path('<uuid:uuid>/edit/',      lot.edit,      name='lot_edit'),
    path('<uuid:uuid>/delete/',    lot.delete,    name='lot_delete'),

    path('<uuid:uuid>/publish/',   lot.publish,   name='lot_publish'),
    path('<uuid:uuid>/admit/',     lot.admit,     name='lot_admit'),
    path('<uuid:uuid>/summarize/', lot.summarize, name='lot_summarize'),
    path('<uuid:uuid>/cancel/',    lot.cancel,    name='lot_cancel'),
    path('<uuid:uuid>/revoke/',    lot.revoke,    name='lot_revoke'),
    # path('<uuid:uuid>/eoz_sent/', lot.eoz_sent,  name='lot_eoz_sent'),

    path('<uuid:uuid>/position/create/',              position.create, name='lot_position_create'),
    path('<uuid:uuid>/position/<int:pos_id>/edit/',   position.edit,   name='lot_position_edit'),

    path('<uuid:uuid>/file/upload/',               file.upload,       name='lot_file_upload'),
    path('<uuid:uuid>/file/<int:file_id>/delete/', file.delete,       name='lot_file_delete'),

    path('<uuid:uuid>/file/report/admission/', file.admission, name='lot_file_report_admission'),
    path('<uuid:uuid>/file/report/result/',    file.result,    name='lot_file_report_result'),
    path('<uuid:uuid>/file/report/progress/',    file.progress,    name='lot_file_report_progress'),
    
    path('<uuid:uuid>/application/create/',              application.create, name='lot_application_create'),
    path('<uuid:uuid>/application/<int:app_id>/delete/', application.delete, name='lot_application_delete'),
    path('<uuid:uuid>/application/<int:app_id>/admit/',  application.admit,  name='lot_application_admit'),
    path('<uuid:uuid>/application/<int:app_id>/reject/', application.reject, name='lot_application_reject'),

    path('<uuid:uuid>/bid/',        bid.list,   name='lot_bid_list'),
    path('<uuid:uuid>/bid/create/', bid.create, name='lot_bid_create'),

    path('<uuid:uuid>/result/create/',    result.create,    name='lot_result_create'),
    path('<uuid:uuid>/signature/create/', signature.create, name='lot_signature_create'),

    path('report/',  file.report, name='lot_file_report'),

    
]   