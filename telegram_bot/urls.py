from django.urls import path

from telegram_bot.api_views.tg_frontend_redirect import redirect_to_frontend
from telegram_bot.api_views.user_data import AccountView

urlpatterns = [
    path('account/<str:token>/', AccountView.as_view(), name='account'),
    path('frontend_redirect_url/<str:token>/', redirect_to_frontend, name='redirect_to_frontend'),
]