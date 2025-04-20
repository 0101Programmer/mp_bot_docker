from decouple import config
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

FRONTEND_CORS_ORIGIN = config('FRONTEND_CORS_ORIGIN')


# @csrf_exempt
# def redirect_to_frontend(request):
#     return HttpResponse(f"""
#         <!DOCTYPE html>
#         <html lang="en">
#         <head>
#             <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             <title>Telegram Mini App</title>
#             <script src="https://telegram.org/js/telegram-web-app.js"></script>
#         </head>
#         <body>
#             <h1>Welcome to My Telegram Mini App</h1>
#             <div id="user-info"></div>
#             <script>
#                 function initializeApp() {{
#                     const initData = Telegram.WebApp.initData;
#                     const user = Telegram.WebApp.initDataUnsafe.user;
#
#                     if (user) {{
#                         document.getElementById("user-info").innerText = "Hello, User " + user.id + "!";
#                     }} else {{
#                         document.getElementById("user-info").innerText = "User data not found.";
#                     }}
#                 }}
#
#                 window.onload = initializeApp;
#             </script>
#         </body>
#         </html>
#     """)

@csrf_exempt
def redirect_to_frontend(request):
    return HttpResponse(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Redirecting...</title>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
        </head>
        <body>
            <h1>Redirecting to frontend...</h1>
            <div id="status">Loading...</div>
            <script>
                function redirectToFrontend() {{
                    // Проверяем доступность Telegram WebApp
                    if (!Telegram || !Telegram.WebApp) {{
                        document.getElementById("status").innerText = "Telegram WebApp not available.";
                        return;
                    }}

                    // Получаем initData
                    const initData = Telegram.WebApp.initData;
                    const user = Telegram.WebApp.initDataUnsafe.user;

                    if (!user) {{
                        document.getElementById("status").innerText = "User data not found.";
                        return;
                    }}

                    // Формируем URL для редиректа на фронтенд
                    const frontendUrl = "{FRONTEND_CORS_ORIGIN}";
                    const queryParams = new URLSearchParams({{ initData: JSON.stringify(Telegram.WebApp.initDataUnsafe) }});
                    const fullUrl = `${{frontendUrl}}?${{queryParams.toString()}}`;

                    // Выполняем редирект
                    window.location.href = fullUrl;
                }}

                // Инициализация при загрузке страницы
                window.onload = redirectToFrontend;
            </script>
        </body>
        </html>
    """)