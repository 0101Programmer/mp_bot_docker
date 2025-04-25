from django.urls import path

from telegram_bot import views
from telegram_bot.api_views.admin.admin_requests.get_update_delete_admin_requests import AdminRequestListView, \
    UpdateAdminRequestStatusView, DeleteAdminRequestView
from telegram_bot.api_views.admin.appeals.get_update_delete_appeal import AppealListForAdminView, \
    DeleteAppealForAdminView, \
    UpdateAppealStatusView
from telegram_bot.api_views.admin.commissions.create_commission import CreateCommissionView
from telegram_bot.api_views.admin.commissions.delete_commission import DeleteCommissionView
from telegram_bot.api_views.admin.commissions.get_commissions import CommissionListView
from telegram_bot.api_views.admin.commissions.get_update_commission import CommissionDetailView, UpdateCommissionView
from telegram_bot.api_views.admin.users.delete_user import DeleteUserView
from telegram_bot.api_views.service.file_downloader import DownloadFileView
from telegram_bot.api_views.service.get_user_data import UserDataView
from telegram_bot.api_views.user.admin_requests.get_admin_requests import CheckPendingRejectedAcceptedRequest
from telegram_bot.api_views.user.admin_requests.sent_admin_request import SentAdminRequest
from telegram_bot.api_views.user.appeals.appeal_create import CreateAppealView
from telegram_bot.api_views.user.appeals.appeal_delete import DeleteAppealView
from telegram_bot.api_views.user.appeals.get_appeals import AppealListView

urlpatterns = [
    # api для сервисного взаимодействия с пользователем
    path('api/v1/service/get_user_data/', UserDataView.as_view(), name='user_data'),

    # api для сервисного взаимодействия с фронтендом
    path('api/v1/service/download/<int:appeal_id>/', DownloadFileView.as_view(), name='download_file'),

    # api для взаимодействия с пользователем (для администратора)
    path('api/v1/admin/delete_user/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),

    # api обращений для пользователя
    path('api/v1/user/appeals/', AppealListView.as_view(), name='appeal-list'),
    path('api/v1/user/appeal/<int:appeal_id>/delete/', DeleteAppealView.as_view(), name='delete_appeal'),
    path('api/v1/user/appeal_create/', CreateAppealView.as_view(), name='create_appeal'),

    # api запросов на получение прав администратора (для пользователя)
    path('api/v1/user/admin-request/', SentAdminRequest.as_view(), name='sent_admin_request'),
    path('api/v1/user/admin-request/check-pending-rejected-accepted/<str:user_id>/', CheckPendingRejectedAcceptedRequest.as_view(), name='check_pending_rejected_request'),

    # api обращений (для администратора)
    path('api/v1/admin/appeals/', AppealListForAdminView.as_view(), name='admin-appeal-list'),
    path('api/v1/admin/update_appeal_status/<int:appeal_id>/', UpdateAppealStatusView.as_view(), name='admin-update-appeal-status'),
    path('api/v1/admin/delete_appeal/<int:appeal_id>/', DeleteAppealForAdminView.as_view(), name='admin-delete-appeal'),

    # api комиссий
    path('api/v1/service/commissions/', CommissionListView.as_view(), name='commission-list'),
    path('api/v1/admin/create_commission/', CreateCommissionView.as_view(), name='create-commission'),
    path('api/v1/admin/delete_commission/<int:commission_id>/', DeleteCommissionView.as_view(), name='delete-commission'),
    path('api/v1/service/commission_detail/<int:commission_id>/', CommissionDetailView.as_view(), name='commission-detail'),
    path('api/v1/admin/update_commission/<int:commission_id>/', UpdateCommissionView.as_view(), name='update-commission'),

    # api запросов на получение прав администратора (для администратора)
    path('api/v1/admin/admin_requests/', AdminRequestListView.as_view(), name='admin-request-list'),
    path('api/v1/admin/update_admin_request_status/<int:request_id>/', UpdateAdminRequestStatusView.as_view(),
         name='update-admin-request-status'),
    path('api/v1/admin/delete_admin_request/<int:request_id>/', DeleteAdminRequestView.as_view(), name='delete-admin-request'),
]