from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from telegram_bot.api_views.appeal_create import CreateAppealView
from telegram_bot.api_views.appeal_delete import DeleteAppealView
from telegram_bot.api_views.comissions.get_comissions import CommissionListView
from telegram_bot.api_views.file_downloader import DownloadFileView
from telegram_bot.api_views.get_appeals import AppealListView
from telegram_bot.api_views.logout_endpoint import LogoutView
from telegram_bot.api_views.tg_frontend_redirect import redirect_to_frontend
from telegram_bot.api_views.get_user_data import UserDataView

urlpatterns = [
    path('get_user_data/<str:token>/', UserDataView.as_view(), name='user_data'),
    path('frontend_redirect_url/<str:token>/', redirect_to_frontend, name='redirect_to_frontend'),
    path('appeals/', AppealListView.as_view(), name='appeal-list'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('download/<int:appeal_id>/', DownloadFileView.as_view(), name='download_file'),
    path('appeal/<int:appeal_id>/delete/', DeleteAppealView.as_view(), name='delete_appeal'),
    path('appeal_create/', CreateAppealView.as_view(), name='create_appeal'),
    path('commissions/', CommissionListView.as_view(), name='commission-list'),

]

# Добавляем маршрут для медиафайлов (только в режиме разработки)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)