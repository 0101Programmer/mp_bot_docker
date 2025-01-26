import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from django.conf import settings

# Импорт Django-моделей
from .models import User as UserModel, Appeal, CommissionInfo, Notification

API_TOKEN = settings.TELEGRAM_API_TOKEN

FILE_DIR = 'uploads/'
  # Укажите Telegram ID администратора

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


# Определение состояний
class Form(StatesGroup):
    select_commission = State()
    contact_info = State()
    write_appeal = State()
    attach_file = State()
    view_commission_info = State()
    admin_change_status = State()


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else 'N/A'
    
    # Сохраним/обновим пользователя в БД
    user_obj, created = UserModel.objects.update_or_create(
        user_id=user_id,
        defaults={'username': username}
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Написать обращение")
    markup.add("Описание комиссий")
    markup.add("Отследить статус обращения")
    await message.reply("Привет! Добро пожаловать в чат-бот молодежного парламента. Пожалуйста, выберите действие.", reply_markup=markup)


# Обработка выбора написать обращение
@dp.message_handler(lambda message: message.text == "Написать обращение")
async def ask_commission(message: types.Message):
    commissions = CommissionInfo.objects.all().values_list('name', flat=True)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for commission_name in commissions:
        markup.add(commission_name)

    await Form.select_commission.set()
    await message.reply("Выберите комиссию:", reply_markup=markup)


# Обработка выбора комиссии
@dp.message_handler(state=Form.select_commission)
async def select_commission(message: types.Message, state: FSMContext):
    commission_name = message.text
    try:
        commission = CommissionInfo.objects.get(name=commission_name)
        await state.update_data(commission_id=commission.id)
        await Form.next()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Оставить контактную информацию", "Анонимное обращение")
        await message.reply("Хотите ли вы оставить контактную информацию (номер телефона/адрес эл.почты)?", reply_markup=markup)
    except CommissionInfo.DoesNotExist:
        await message.reply("Пожалуйста, выберите комиссию из предложенного списка.")


# Обработка контактной информации
@dp.message_handler(lambda message: message.text in ["Оставить контактную информацию", "Анонимное обращение"], state=Form.contact_info)
async def process_contact_info_choice(message: types.Message, state: FSMContext):
    if message.text == "Анонимное обращение":
        await state.update_data(contact_info=None)
        await Form.next()
        await message.reply("Напишите ваше обращение:")
    else:
        await message.reply("Пожалуйста, введите вашу контактную информацию (номер телефона или адрес эл.почты).")


# Сохранение контактной информации и переход к написанию обращения
@dp.message_handler(state=Form.contact_info)
async def process_contact_info(message: types.Message, state: FSMContext):
    contact_info = message.text
    await state.update_data(contact_info=contact_info)
    await Form.next()
    await message.reply("Напишите ваше обращение:")


# Обработка написания обращения
@dp.message_handler(state=Form.write_appeal)
async def write_appeal(message: types.Message, state: FSMContext):
    appeal_text = message.text
    await state.update_data(appeal_text=appeal_text)
    # Переходим на шаг прикрепления файла
    await Form.next()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Пропустить")
    await message.reply("Прикрепите файл, если необходимо, или нажмите 'Пропустить'", reply_markup=markup)


# Обработка прикрепления файла
@dp.message_handler(content_types=['document', 'photo'], state=Form.attach_file)
async def process_file_upload(message: types.Message, state: FSMContext):
    # Забираем данные из стейта
    user_data = await state.get_data()
    user_id = message.from_user.id

    # Гарантируем, что директория для файлов существует
    if not os.path.exists(FILE_DIR):
        os.makedirs(FILE_DIR)

    # Скачиваем файл
    if message.content_type == 'document':
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_name = message.document.file_name
    else:  # photo
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        file_name = f"{file_id}.jpg"

    local_path = os.path.join(FILE_DIR, file_name)
    await bot.download_file(file_path, local_path)

    # Сохраняем обращение в БД
    user_obj = UserModel.objects.get(user_id=user_id)
    appeal = Appeal.objects.create(
        user=user_obj,
        commission_id=user_data['commission_id'],
        appeal_text=user_data['appeal_text'],
        contact_info=user_data.get('contact_info'),
        file_path=local_path
    )

    await state.finish()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Отследить статус обращения")
    markup.add("Написать новое обращение")
    markup.add("Описание комиссий")
    await message.reply("Ваше обращение зарегистрировано. Вы можете отслеживать его статус или написать новое обращение.", reply_markup=markup)


# Обработка пропуска прикрепления файла
@dp.message_handler(lambda message: message.text == "Пропустить", state=Form.attach_file)
async def skip_file_upload(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id

    user_obj = UserModel.objects.get(user_id=user_id)
    appeal = Appeal.objects.create(
        user=user_obj,
        commission_id=user_data['commission_id'],
        appeal_text=user_data['appeal_text'],
        contact_info=user_data.get('contact_info')
    )

    await state.finish()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Отследить статус обращения")
    markup.add("Написать новое обращение")
    markup.add("Описание комиссий")
    await message.reply("Ваше обращение зарегистрировано. Вы можете отслеживать его статус или написать новое обращение.", reply_markup=markup)


# Обработчик для отслеживания статуса обращения
@dp.message_handler(lambda message: message.text == "Отследить статус обращения")
async def track_appeal_status(message: types.Message):
    user_id = message.from_user.id
    user_obj = UserModel.objects.filter(user_id=user_id).first()
    if not user_obj:
        await message.reply("У вас нет зарегистрированных обращений.")
        return
    appeals = Appeal.objects.filter(user=user_obj)
    if appeals.exists():
        response = "Ваши обращения:\n"
        for appeal in appeals:
            response += f"Обращение: {appeal.appeal_text}, Статус: {appeal.status}\n"
        await message.reply(response)
    else:
        await message.reply("У вас нет зарегистрированных обращений.")


# Обработчик для написания нового обращения
@dp.message_handler(lambda message: message.text == "Написать новое обращение")
async def new_appeal(message: types.Message):
    commissions = CommissionInfo.objects.all().values_list('name', flat=True)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for commission_name in commissions:
        markup.add(commission_name)

    await Form.select_commission.set()
    await message.reply("Выберите комиссию:", reply_markup=markup)


# Обработчик для описания комиссий
@dp.message_handler(lambda message: message.text == "Описание комиссий")
async def show_commissions(message: types.Message):
    commissions = CommissionInfo.objects.all().values_list('name', flat=True)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for commission_name in commissions:
        markup.add(commission_name)
    markup.add("Назад")
    
    await Form.view_commission_info.set()
    await message.reply("Выберите комиссию для получения информации:", reply_markup=markup)


# Обработка выбора комиссии для просмотра информации
@dp.message_handler(state=Form.view_commission_info)
async def view_commission_info(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Написать обращение")
        markup.add("Описание комиссий")
        markup.add("Отследить статус обращения")
        await state.finish()
        await message.reply("Вы вернулись в главное меню.", reply_markup=markup)
    else:
        commission_name = message.text
        try:
            commission = CommissionInfo.objects.get(name=commission_name)
            await message.reply(commission.description)
        except CommissionInfo.DoesNotExist:
            await message.reply("Пожалуйста, выберите комиссию из предложенного списка.")


import asyncio
from asgiref.sync import sync_to_async

# 1) Оборачиваем работу с ORM в sync_to_async:

@sync_to_async
def get_unsent_notifications():
    # Можно добавить select_related, чтобы не вызывать лишних запросов, если нужно.
    return list(Notification.objects.select_related('appeal', 'user').filter(sent=False))

@sync_to_async
def mark_notification_sent(notification):
    notification.sent = True
    notification.save()

async def send_notifications():
    while True:
        # Вызываем синхронную ORM-функцию через await
        notifications = await get_unsent_notifications()

        for notification in notifications:
            appeal_message = notification.appeal.appeal_text
            user_id = notification.user.user_id
            # bot.send_message — асинхронный вызов, поэтому можно await-ить напрямую
            await bot.send_message(
                user_id,
                f"Статус вашего обращения '{appeal_message}' изменился на: {notification.status}"
            )
            # Снова синхронная операция ORM => обёртка sync_to_async
            await mark_notification_sent(notification)

        # Ждём 60 секунд перед следующей проверкой
        await asyncio.sleep(60)

# Команда для просмотра списка обращений (админ)
@dp.message_handler(commands=['admin_appeals'])
async def admin_appeals(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        await message.reply("У вас нет прав для выполнения этой команды.")
        return
    
    appeals = Appeal.objects.select_related('user', 'commission').all()
    if appeals.exists():
        response = "Список обращений:\n"
        for a in appeals:
            response += (
                f"ID: {a.id}, Пользователь: {a.user.username}, "
                f"Комиссия: {a.commission.name if a.commission else 'N/A'}, "
                f"Обращение: {a.appeal_text}, Статус: {a.status}\n"
            )
        await message.reply(response)
    else:
        await message.reply("Нет зарегистрированных обращений.")


# Команда для изменения статуса обращения (админ)
@dp.message_handler(commands=['admin_change_status'])
async def admin_change_status_start(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        await message.reply("У вас нет прав для выполнения этой команды.")
        return
    
    await Form.admin_change_status.set()
    await message.reply("Введите ID обращения и новый статус в формате: ID, новый статус")


@dp.message_handler(state=Form.admin_change_status)
async def admin_change_status(message: types.Message, state: FSMContext):
    try:
        appeal_id, new_status = message.text.split(',', 1)
        appeal_id = appeal_id.strip()
        new_status = new_status.strip()

        appeal = Appeal.objects.get(pk=appeal_id)
        appeal.status = new_status
        appeal.save()

        # Создаём новую нотификацию для пользователя
        Notification.objects.create(
            user=appeal.user,
            appeal=appeal,
            status=new_status
        )

        await state.finish()
        await message.reply(f"Статус обращения с ID {appeal_id} изменен на: {new_status}")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")
