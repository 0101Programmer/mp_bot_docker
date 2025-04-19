import os
import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.core.files import File

from .utils import PHONE_PATTERN, EMAIL_PATTERN, MIN_TXT_LENGTH, MAX_TXT_LENGTH, save_appeal_to_db, MAX_FILE_SIZE, \
    AppealForm
from ...models import CommissionInfo
from ...tools.main_logger import logger

router = Router()


# Обработчик текста "Написать обращение"
@router.message(F.text == "Написать обращение")
async def start_appeal_form(message: Message, state: FSMContext, user=None):
    """
    Обработчик для кнопки "Написать обращение".
    :param user: Пользователь, полученный из middleware
    """
    try:
        # Получаем все комиссии из базы данных
        commissions = await sync_to_async(list)(CommissionInfo.objects.all())

        if commissions:
            # Создаем inline-клавиатуру с кнопками для каждой комиссии
            builder = InlineKeyboardBuilder()
            for commission in commissions:
                builder.button(text=commission.name, callback_data=f"appeal_commission:{commission.id}")
            builder.adjust(1)  # Каждая кнопка на новой строке

            # Отправляем сообщение с inline-клавиатурой
            await message.answer(
                "Выберите комиссию:", reply_markup=builder.as_markup()
            )
            # Устанавливаем состояние выбора комиссии
            await state.set_state(AppealForm.choosing_commission)
        else:
            await message.answer("Список комиссий пуст.")

    except Exception as e:
        logger.error(f"Ошибка при старте формы обращения: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора комиссии при написании обращения
@router.callback_query(AppealForm.choosing_commission, F.data.startswith("appeal_commission:"))
async def process_commission_choice(callback_query: CallbackQuery, state: FSMContext):
    try:
        # Извлекаем ID комиссии из callback_data
        commission_id = int(callback_query.data.split(":")[1])
        await state.update_data(commission_id=commission_id)

        # Создаем inline-клавиатуру для выбора контактов
        builder = InlineKeyboardBuilder()
        builder.button(text="Оставить контактную информацию", callback_data="contact:yes")
        builder.button(text="Анонимное обращение", callback_data="contact:no")
        builder.adjust(1)

        # Отправляем сообщение с inline-клавиатурой
        await callback_query.message.edit_text(
            "Хотите оставить контактную информацию?", reply_markup=builder.as_markup()
        )
        # Устанавливаем состояние выбора контактов
        await state.set_state(AppealForm.choosing_contact_option)

    except Exception as e:
        logger.error(f"Ошибка при выборе комиссии: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора контактов
@router.callback_query(AppealForm.choosing_contact_option, F.data.startswith("contact:"))
async def process_contact_choice(callback_query: CallbackQuery, state: FSMContext):
    try:
        contact_option = callback_query.data.split(":")[1]
        await state.update_data(contact_option=contact_option)

        if contact_option == "yes":
            await callback_query.message.edit_text("Введите ваш номер телефона или email:")
            await state.set_state(AppealForm.entering_contact_info)
        else:
            await callback_query.message.edit_text("Напишите ваше обращение:")
            await state.set_state(AppealForm.writing_appeal)

    except Exception as e:
        logger.error(f"Ошибка при выборе контактов: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


# Обработчик ввода контактной информации
@router.message(AppealForm.entering_contact_info)
async def process_contact_info(message: Message, state: FSMContext):
    try:
        contact_info = message.text.strip()

        # Проверяем, соответствует ли ввод паттерну email или номера телефона
        if re.match(EMAIL_PATTERN, contact_info) or re.match(PHONE_PATTERN, contact_info):
            # Сохраняем контактную информацию в состояние
            await state.update_data(contact_info=contact_info)

            # Переходим к следующему состоянию
            await message.answer("Напишите ваше обращение:")
            await state.set_state(AppealForm.writing_appeal)
        else:
            # Создаем inline-клавиатуру с кнопкой "Оставить анонимное обращение"
            builder = InlineKeyboardBuilder()
            builder.button(text="Оставить анонимное обращение", callback_data="anonymous_appeal")
            builder.adjust(1)

            # Отправляем сообщение с инструкцией
            await message.answer(
                "Контактная информация некорректна. Пожалуйста, введите email или российский номер телефона в международном формате (+7XXXXXXXXXX).",
                reply_markup=builder.as_markup()
            )

    except Exception as e:
        logger.error(f"Ошибка при вводе контактной информации: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик inline-кнопки "Оставить анонимное обращение"
@router.callback_query(AppealForm.entering_contact_info, F.data == "anonymous_appeal")
async def skip_contact_info(callback_query: CallbackQuery, state: FSMContext):
    try:
        # Очищаем контактную информацию (оставляем её пустой)
        await state.update_data(contact_info=None)

        # Переходим к следующему состоянию
        await callback_query.message.edit_text("Напишите ваше обращение:")
        await state.set_state(AppealForm.writing_appeal)

    except Exception as e:
        logger.error(f"Ошибка при пропуске контактной информации: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик написания обращения
@router.message(AppealForm.writing_appeal)
async def process_appeal_text(message: Message, state: FSMContext):
    try:
        # Получаем текст обращения
        appeal_text = message.text

        # Проверяем длину текста
        if len(appeal_text) < MIN_TXT_LENGTH:
            await message.answer(
                "Обращение слишком короткое. Пожалуйста, напишите более подробное обращение (минимум 100 символов)."
            )
            return
        elif len(appeal_text) > MAX_TXT_LENGTH:
            await message.answer(
                "Обращение слишком длинное. Пожалуйста, сократите текст до 300 символов."
            )
            return

        # Сохраняем текст обращения в состояние
        await state.update_data(appeal_text=appeal_text)

        # Создаем inline-клавиатуру для прикрепления файла
        builder = InlineKeyboardBuilder()
        builder.button(text="Прикрепить файл", callback_data="file:attach")
        builder.button(text="Пропустить", callback_data="file:skip")
        builder.adjust(1)

        # Отправляем сообщение с inline-клавиатурой
        await message.answer("Хотите прикрепить файл?", reply_markup=builder.as_markup())

        # Переходим к следующему состоянию
        await state.set_state(AppealForm.attaching_file)

    except Exception as e:
        logger.error(f"Ошибка при написании обращения: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора прикрепления файла
@router.callback_query(AppealForm.attaching_file, F.data.startswith("file:"))
async def process_file_choice(callback_query: CallbackQuery, state: FSMContext):
    try:
        file_option = callback_query.data.split(":")[1]

        if file_option == "attach":
            await callback_query.message.edit_text("Пришлите фото или документ:")
            await state.set_state(AppealForm.attaching_file)
        else:
            # Сохраняем данные в базу данных
            data = await state.get_data()
            await save_appeal_to_db(data, callback_query.from_user.id)
            await callback_query.message.edit_text("Ваше обращение успешно отправлено!")
            await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при выборе файла: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


# Обработчик текстовых сообщений в состоянии "Прикрепление файла"
@router.message(AppealForm.attaching_file, F.text)
async def handle_invalid_file(message: Message):
    try:
        # Создаем inline-клавиатуру с кнопкой "Пропустить загрузку файла"
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Пропустить загрузку файла", callback_data="skip_file")]
            ]
        )

        # Отправляем сообщение с инструкцией
        await message.answer(
            "Некорректный формат файла. Пожалуйста, отправьте фото или документ.",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке текстового сообщения: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")


# Обработчик загрузки файла
@router.message(AppealForm.attaching_file, F.photo | F.document)
async def process_file_upload(message: Message, state: FSMContext):
    try:
        # Определяем тип файла (фото или документ)
        if message.photo:
            # Получаем информацию о фото
            file_id = message.photo[-1].file_id
            file_info = await message.bot.get_file(file_id)
            file_size = message.photo[-1].file_size  # Размер фото в байтах
            file_extension = ".jpg"  # Фото всегда сохраняем как .jpg
            original_file_name = f"{message.from_user.id}_photo{file_extension}"

        elif message.document:
            # Получаем информацию о документе
            file_id = message.document.file_id
            file_info = await message.bot.get_file(file_id)
            file_size = message.document.file_size  # Размер документа в байтах
            original_file_name = message.document.file_name

        else:
            await message.answer("Пожалуйста, отправьте фото или документ.")
            return

        # Проверяем размер файла
        if file_size > MAX_FILE_SIZE:
            await message.answer(
                f"Размер файла слишком большой. Максимальный допустимый размер: {MAX_FILE_SIZE // (1024 * 1024)} MB."
            )
            return

        # Путь к временной папке
        temp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(temp_dir, exist_ok=True)  # Создаем папку tmp, если её нет

        # Полный путь к временному файлу
        temp_file_path = os.path.join(temp_dir, original_file_name)

        # Скачиваем файл во временную папку
        await message.bot.download_file(file_info.file_path, temp_file_path)

        # Открываем временный файл для загрузки через Django
        with open(temp_file_path, 'rb') as f:
            django_file = File(f)
            # Сохраняем данные в базу данных
            data = await state.get_data()
            await save_appeal_to_db(data, message.from_user.id, django_file, original_file_name)

        # Удаляем временный файл после использования
        os.remove(temp_file_path)

        # Отправляем сообщение об успешной отправке обращения
        await message.answer("Ваше обращение успешно отправлено!")
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при загрузке файла: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")


# Обработчик inline-кнопки "Пропустить загрузку файла"
@router.callback_query(AppealForm.attaching_file, F.data == "skip_file")
async def skip_file_upload(callback_query: CallbackQuery, state: FSMContext):
    try:
        # Сохраняем данные без файла
        data = await state.get_data()
        await save_appeal_to_db(data, callback_query.from_user.id)

        # Отправляем сообщение об успешной отправке обращения
        await callback_query.message.edit_text("Ваше обращение успешно отправлено!")
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при пропуске загрузки файла: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")