from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from telegram_bot.api_views.appeal_create import CreateAppealView
from telegram_bot.api_views.appeal_delete import DeleteAppealView
from telegram_bot.api_views.appeals.get_update_delete_appeal import AppealListForAdminView, DeleteAppealForAdminView, \
    UpdateAppealStatusView
from telegram_bot.api_views.comissions.create_commission import CreateCommissionView
from telegram_bot.api_views.comissions.delete_commission import DeleteCommissionView
from telegram_bot.api_views.comissions.get_comissions import CommissionListView
from telegram_bot.api_views.comissions.get_update_commission import CommissionDetailView, UpdateCommissionView
from telegram_bot.api_views.file_downloader import DownloadFileView
from telegram_bot.api_views.get_appeals import AppealListView
from telegram_bot.api_views.logout_endpoint import LogoutView
from telegram_bot.api_views.tg_frontend_redirect import redirect_to_frontend
from telegram_bot.api_views.get_user_data import UserDataView
from telegram_bot.api_views.users.delete_user import DeleteUserView

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

    # api обращений для администратора
    path('admin/appeals/', AppealListForAdminView.as_view(), name='admin-appeal-list'),
    path('admin/update_appeal_status/<int:appeal_id>/', UpdateAppealStatusView.as_view(), name='admin-update-appeal-status'),
    path('admin/delete_appeal/<int:appeal_id>/', DeleteAppealForAdminView.as_view(), name='admin-delete-appeal'),

    # api комиссий
    path('commissions/', CommissionListView.as_view(), name='commission-list'),
    path('create_commission/', CreateCommissionView.as_view(), name='create-commission'),
    path('delete_commission/<int:commission_id>/', DeleteCommissionView.as_view(), name='delete-commission'),
    path('commission_detail/<int:commission_id>/', CommissionDetailView.as_view(), name='commission-detail'),
    path('update_commission/<int:commission_id>/', UpdateCommissionView.as_view(), name='update-commission'),

]

# Добавляем маршрут для медиафайлов (только в режиме разработки)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)