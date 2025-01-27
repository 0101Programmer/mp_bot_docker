import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from django.conf import settings

from asgiref.sync import sync_to_async

# Импорт Django-моделей
from .models import User as UserModel, Appeal, CommissionInfo, Notification, AdminRequest
API_TOKEN = settings.TELEGRAM_API_TOKEN
bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

FILE_DIR = "uploads/"
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "123456789")


# ----------- Вспомогательные sync_to_async функции для ORM ------------

@sync_to_async
def upsert_user(user_id, username):
    """update_or_create для модели User (синхронный вызов)."""
    return UserModel.objects.update_or_create(
        user_id=user_id,
        defaults={'username': username}
    )

@sync_to_async
def create_admin_request(user_obj, admin_position):
    """Создать AdminRequest, если нет активной заявки."""
    existing_request = AdminRequest.objects.filter(user=user_obj, status='pending').first()
    if existing_request:
        return existing_request
    return AdminRequest.objects.create(
        user=user_obj,
        admin_position=admin_position
    )

@sync_to_async
def get_user_by_id(user_id):
    """ Получить пользователя по user_id. """
    return UserModel.objects.get(user_id=user_id)

@sync_to_async
def get_user_or_none(user_id):
    """ Получить пользователя или None (через .filter(...).first()). """
    return UserModel.objects.filter(user_id=user_id).first()

@sync_to_async
def create_appeal(user_obj, commission_id, text, contact=None, file_path=None):
    """ Создать Appeal. """
    return Appeal.objects.create(
        user=user_obj,
        commission_id=commission_id,
        appeal_text=text,
        contact_info=contact,
        file_path=file_path
    )

@sync_to_async
def get_appeals_by_user(user_obj):
    return list(Appeal.objects.filter(user=user_obj))

@sync_to_async
def get_commissions_list():
    return list(CommissionInfo.objects.values_list('name', flat=True))

@sync_to_async
def get_commission_by_name(name):
    return CommissionInfo.objects.get(name=name)

@sync_to_async
def get_notification_unsent():
    """ Возвращает список неотправленных Notification. """
    return list(Notification.objects.select_related('appeal', 'user').filter(sent=False))

@sync_to_async
def mark_notification_sent(notification):
    notification.sent = True
    notification.save()

@sync_to_async
def create_notification_for_appeal(appeal, new_status):
    """Создаём новую нотификацию (для admin_change_status)."""
    return Notification.objects.create(
        user=appeal.user,
        appeal=appeal,
        status=new_status
    )

@sync_to_async
def get_appeal_by_id(appeal_id):
    return Appeal.objects.get(pk=appeal_id)

@sync_to_async
def save_appeal_status(appeal, new_status):
    appeal.status = new_status
    appeal.save()

@sync_to_async
def get_all_appeals():
    return list(Appeal.objects.select_related('user', 'commission').all())

# ----------------------------------------------------------------------

class Form(StatesGroup):
    select_commission = State()
    contact_info = State()
    write_appeal = State()
    attach_file = State()
    view_commission_info = State()
    admin_change_status = State()
    admin_position = State()  # Новое состояние для должности администратора


# ----------------- /start ----------------- #
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    # Сохраним/обновим пользователя в БД (sync_to_async)
    user_obj, created = await upsert_user(user_id, username)

    # Обновляем имя и фамилию пользователя
    user_obj.first_name = first_name
    user_obj.last_name = last_name
    await sync_to_async(user_obj.save)()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Написать обращение")
    markup.add("Описание комиссий")
    markup.add("Отследить статус обращения")
    await message.reply(
        "Привет! Добро пожаловать в чат-бот молодежного парламента. "
        "Пожалуйста, выберите действие.",
        reply_markup=markup
    )

# ----------------- Написать обращение ----------------- #
@dp.message_handler(lambda message: message.text == "Написать обращение")
async def ask_commission(message: types.Message):
    commissions = await get_commissions_list()  # sync_to_async
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for commission_name in commissions:
        markup.add(commission_name)
    await Form.select_commission.set()
    await message.reply("Выберите комиссию:", reply_markup=markup)


@dp.message_handler(state=Form.select_commission)
async def select_commission(message: types.Message, state: FSMContext):
    commission_name = message.text
    try:
        commission = await get_commission_by_name(commission_name)  # sync_to_async
        await state.update_data(commission_id=commission.id)
        await Form.next()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Оставить контактную информацию", "Анонимное обращение")
        await message.reply(
            "Хотите ли вы оставить контактную информацию (номер телефона/адрес эл.почты)?",
            reply_markup=markup
        )
    except CommissionInfo.DoesNotExist:
        await message.reply("Пожалуйста, выберите комиссию из предложенного списка.")


@dp.message_handler(
    lambda message: message.text in ["Оставить контактную информацию", "Анонимное обращение"],
    state=Form.contact_info
)
async def process_contact_info_choice(message: types.Message, state: FSMContext):
    if message.text == "Анонимное обращение":
        await state.update_data(contact_info=None)
        await Form.next()
        await message.reply("Напишите ваше обращение:")
    else:
        await message.reply("Пожалуйста, введите вашу контактную информацию (номер телефона или адрес эл.почты).")


@dp.message_handler(state=Form.contact_info)
async def process_contact_info(message: types.Message, state: FSMContext):
    contact_info = message.text
    await state.update_data(contact_info=contact_info)
    await Form.next()
    await message.reply("Напишите ваше обращение:")


@dp.message_handler(state=Form.write_appeal)
async def write_appeal(message: types.Message, state: FSMContext):
    appeal_text = message.text
    await state.update_data(appeal_text=appeal_text)
    # Переходим на шаг прикрепления файла
    await Form.next()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Пропустить")
    await message.reply(
        "Прикрепите файл, если необходимо, или нажмите 'Пропустить'",
        reply_markup=markup
    )


@dp.message_handler(content_types=['document', 'photo'], state=Form.attach_file)
async def process_file_upload(message: types.Message, state: FSMContext):
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
    user_obj = await get_user_by_id(user_id)  # sync_to_async
    appeal = await create_appeal(
        user_obj,
        user_data['commission_id'],
        user_data['appeal_text'],
        user_data.get('contact_info'),
        local_path
    )

    await state.finish()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Отследить статус обращения")
    markup.add("Написать новое обращение")
    markup.add("Описание комиссий")
    await message.reply(
        "Ваше обращение зарегистрировано. Вы можете отслеживать его статус или написать новое обращение.",
        reply_markup=markup
    )


@dp.message_handler(lambda message: message.text == "Пропустить", state=Form.attach_file)
async def skip_file_upload(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id

    user_obj = await get_user_by_id(user_id)  # sync_to_async
    appeal = await create_appeal(
        user_obj,
        user_data['commission_id'],
        user_data['appeal_text'],
        user_data.get('contact_info'),
        file_path=None
    )

    await state.finish()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Отследить статус обращения")
    markup.add("Написать новое обращение")
    markup.add("Описание комиссий")
    await message.reply(
        "Ваше обращение зарегистрировано. "
        "Вы можете отслеживать его статус или написать новое обращение.",
        reply_markup=markup
    )


# ----------------- Отследить статус обращения ----------------- #
@dp.message_handler(lambda message: message.text == "Отследить статус обращения")
async def track_appeal_status(message: types.Message):
    user_id = message.from_user.id
    user_obj = await get_user_or_none(user_id)  # sync_to_async
    if not user_obj:
        await message.reply("У вас нет зарегистрированных обращений.")
        return

    appeals = await get_appeals_by_user(user_obj)  # sync_to_async
    if appeals:
        response = "Ваши обращения:\n"
        for appeal in appeals:
            response += f"Обращение: {appeal.appeal_text}, Статус: {appeal.status}\n"
        await message.reply(response)
    else:
        await message.reply("У вас нет зарегистрированных обращений.")


# ----------------- Написать новое обращение ----------------- #
@dp.message_handler(lambda message: message.text == "Написать новое обращение")
async def new_appeal(message: types.Message):
    commissions = await get_commissions_list()  # sync_to_async
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for commission_name in commissions:
        markup.add(commission_name)

    await Form.select_commission.set()
    await message.reply("Выберите комиссию:", reply_markup=markup)


# ----------------- Описание комиссий ----------------- #
@dp.message_handler(lambda message: message.text == "Описание комиссий")
async def show_commissions(message: types.Message):
    commissions = await get_commissions_list()  # sync_to_async
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for commission_name in commissions:
        markup.add(commission_name)
    markup.add("Назад")

    await Form.view_commission_info.set()
    await message.reply("Выберите комиссию для получения информации:", reply_markup=markup)


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
            commission = await get_commission_by_name(commission_name)  # sync_to_async
            await message.reply(commission.description)
        except CommissionInfo.DoesNotExist:
            await message.reply("Пожалуйста, выберите комиссию из предложенного списка.")


# ----------------- Фоновая задача отправки нотификаций ----------------- #
@sync_to_async
def create_notifications_list():
    """Вернуть список неотправленных Notification (альтернативный вариант)."""
    return list(Notification.objects.select_related('appeal', 'user').filter(sent=False))


async def send_notifications():
    while True:
        notifications = await get_notification_unsent()  # sync_to_async
        for notif in notifications:
            appeal_message = notif.appeal.appeal_text
            user_id = notif.user.user_id
            await bot.send_message(
                user_id,
                f"Статус вашего обращения '{appeal_message}' изменился на: {notif.status}"
            )
            await mark_notification_sent(notif)  # sync_to_async
        await asyncio.sleep(60)

# ----------------- Команды для админа ----------------- #
@dp.message_handler(commands=['register_admin'])
async def register_admin_command(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    # Создание или обновление пользователя в БД
    user_obj, created = await upsert_user(telegram_id, username)

    # Обновляем имя и фамилию пользователя
    user_obj.first_name = first_name
    user_obj.last_name = last_name
    await sync_to_async(user_obj.save)()

    # Проверка наличия уже активной заявки
    existing_request = await sync_to_async(lambda: AdminRequest.objects.filter(user=user_obj, status='pending').first())()
    if existing_request:
        await message.reply("У вас уже есть заявка на получение административных прав, ожидающая одобрения.")
        return

    # Запрос должности администратора
    await Form.admin_position.set()
    await message.reply("Пожалуйста, введите вашу должность для административных прав:")

@dp.message_handler(state=Form.admin_position)
async def process_admin_position(message: types.Message, state: FSMContext):
    admin_position = message.text.strip()
    if not admin_position:
        await message.reply("Должность не может быть пустой. Пожалуйста, введите вашу должность:")
        return

    telegram_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    # Получение пользователя из БД
    user_obj = await get_user_by_id(telegram_id)

    # Создание заявки на админку
    admin_request = await create_admin_request(user_obj, admin_position)

    await message.reply("Ваша заявка на получение административных прав отправлена и ожидает одобрения.")
    await state.finish()

@dp.message_handler(commands=['admin_appeals'])
async def admin_appeals(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        await message.reply("У вас нет прав для выполнения этой команды.")
        return

    appeals = await get_all_appeals()  # sync_to_async
    if appeals:
        response = "Список обращений:\n"
        for a in appeals:
            uname = a.user.username if a.user else "N/A"
            cname = a.commission.name if a.commission else "N/A"
            response += (
                f"ID: {a.id}, Пользователь: {uname}, "
                f"Комиссия: {cname}, "
                f"Обращение: {a.appeal_text}, Статус: {a.status}\n"
            )
        await message.reply(response)
    else:
        await message.reply("Нет зарегистрированных обращений.")


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

        # Получаем объект обращения
        appeal = await get_appeal_by_id(appeal_id)  # sync_to_async

        # Меняем статус
        await save_appeal_status(appeal, new_status)  # sync_to_async

        # Создаём новую нотификацию
        await create_notification_for_appeal(appeal, new_status)

        await state.finish()
        await message.reply(f"Статус обращения с ID {appeal_id} изменен на: {new_status}")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")

