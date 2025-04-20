from django.shortcuts import render

# Create your views here.

# tgbot/views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_page(request, username):
    return HttpResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Личный кабинет</title>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    text-align: center;
                }}
                h1 {{ color: #0088cc; }}
            </style>
        </head>
        <body>
            <h1>Привет, {username}!</h1>
            <p>Это ваш личный кабинет на локальном сервере.</p>
            <script>
                const tg = window.Telegram.WebApp;
                tg.expand();
                tg.BackButton.show();
                tg.BackButton.onClick(() => tg.close());
            </script>
        </body>
        </html>
    """)