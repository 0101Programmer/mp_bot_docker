from django.urls import path

from telegram_bot.api_views.tg_frontend_redirect import redirect_to_frontend
from telegram_bot.api_views.get_user_data import UserDataView

urlpatterns = [
    path('get_user_data/<str:token>/', UserDataView.as_view(), name='user_data'),
    path('frontend_redirect_url/<str:token>/', redirect_to_frontend, name='redirect_to_frontend'),
]