from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from telegram_bot.api_views.admin.admin_requests.get_update_delete_admin_requests import AdminRequestListView, \
    UpdateAdminRequestStatusView, DeleteAdminRequestView
from telegram_bot.api_views.appeal_create import CreateAppealView
from telegram_bot.api_views.appeal_delete import DeleteAppealView
from telegram_bot.api_views.admin.appeals.get_update_delete_appeal import AppealListForAdminView, DeleteAppealForAdminView, \
    UpdateAppealStatusView
from telegram_bot.api_views.admin.comissions.create_commission import CreateCommissionView
from telegram_bot.api_views.admin.comissions.delete_commission import DeleteCommissionView
from telegram_bot.api_views.admin.comissions.get_comissions import CommissionListView
from telegram_bot.api_views.admin.comissions.get_update_commission import CommissionDetailView, UpdateCommissionView
from telegram_bot.api_views.file_downloader import DownloadFileView
from telegram_bot.api_views.get_appeals import AppealListView
from telegram_bot.api_views.logout_endpoint import LogoutView
from telegram_bot.api_views.tg_frontend_redirect import redirect_to_frontend
from telegram_bot.api_views.get_user_data import UserDataView
from telegram_bot.api_views.admin.users.delete_user import DeleteUserView
from telegram_bot.api_views.user.get_admin_requests import CheckPendingRejectedAcceptedRequest
from telegram_bot.api_views.user.sent_admin_request import SentAdminRequest

urlpatterns = [
    # api для взаимодействия с пользователем
    path('get_user_data/<str:token>/', UserDataView.as_view(), name='user_data'),
    path('frontend_redirect_url/<str:token>/', redirect_to_frontend, name='redirect_to_frontend'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete_user/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),

    # api обращений для пользователя
    path('appeals/', AppealListView.as_view(), name='appeal-list'),
    path('appeal/<int:appeal_id>/delete/', DeleteAppealView.as_view(), name='delete_appeal'),
    path('appeal_create/', CreateAppealView.as_view(), name='create_appeal'),
    path('download/<int:appeal_id>/', DownloadFileView.as_view(), name='download_file'),

    # api запросов на получение прав администратора (для пользователя)
    path('api/v1/user/admin-request/', SentAdminRequest.as_view(), name='sent_admin_request'),
    path('api/v1/user/admin-request/check-pending-rejected-accepted/<str:user_id>/', CheckPendingRejectedAcceptedRequest.as_view(), name='check_pending_rejected_request'),

    # api обращений (для администратора)
    path('admin/appeals/', AppealListForAdminView.as_view(), name='admin-appeal-list'),
    path('admin/update_appeal_status/<int:appeal_id>/', UpdateAppealStatusView.as_view(), name='admin-update-appeal-status'),
    path('admin/delete_appeal/<int:appeal_id>/', DeleteAppealForAdminView.as_view(), name='admin-delete-appeal'),

    # api комиссий
    path('commissions/', CommissionListView.as_view(), name='commission-list'),
    path('create_commission/', CreateCommissionView.as_view(), name='create-commission'),
    path('delete_commission/<int:commission_id>/', DeleteCommissionView.as_view(), name='delete-commission'),
    path('commission_detail/<int:commission_id>/', CommissionDetailView.as_view(), name='commission-detail'),
    path('update_commission/<int:commission_id>/', UpdateCommissionView.as_view(), name='update-commission'),

    # api запросов на получение прав администратора (для администратора)
    path('api/v1/admin/admin_requests/', AdminRequestListView.as_view(), name='admin-request-list'),
    path('api/v1/admin/update_admin_request_status/<int:request_id>/', UpdateAdminRequestStatusView.as_view(),
         name='update-admin-request-status'),
    path('api/v1/admin/delete_admin_request/<int:request_id>/', DeleteAdminRequestView.as_view(), name='delete-admin-request'),

]

# Добавляем маршрут для медиафайлов (только в режиме разработки)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)