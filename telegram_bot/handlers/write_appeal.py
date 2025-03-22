from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
import logging
import os
from ..models import CommissionInfo, Appeal, User

logger = logging.getLogger(__name__)

# Функция для сохранения обращения в базу данных
async def save_appeal_to_db(data, telegram_id):
    user = await sync_to_async(User.objects.get)(telegram_id=telegram_id)
    commission = await sync_to_async(CommissionInfo.objects.get)(id=data["commission_id"])
    appeal = Appeal(
        user=user,
        commission=commission,
        appeal_text=data["appeal_text"],
        contact_info=data.get("contact_info"),
        file_path=data.get("file_path"),
        status="Новая"
    )
    await sync_to_async(appeal.save)()

# Создаем класс для хранения состояний
class AppealForm(StatesGroup):
    choosing_commission = State()  # Выбор комиссии
    choosing_contact_option = State()  # Выбор контактов или анонимности
    entering_contact_info = State()  # Ввод контактной информации
    writing_appeal = State()  # Написание обращения
    attaching_file = State()  # Прикрепление файла

router = Router()
# Обработчик текста "Написать обращение"
@router.message(F.text == "Написать обращение")
async def start_appeal_form(message: Message, state: FSMContext):
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
        contact_info = message.text
        await state.update_data(contact_info=contact_info)
        await message.answer("Напишите ваше обращение:")
        await state.set_state(AppealForm.writing_appeal)

    except Exception as e:
        logger.error(f"Ошибка при вводе контактной информации: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик написания обращения
@router.message(AppealForm.writing_appeal)
async def process_appeal_text(message: Message, state: FSMContext):
    try:
        appeal_text = message.text
        await state.update_data(appeal_text=appeal_text)

        # Создаем inline-клавиатуру для прикрепления файла
        builder = InlineKeyboardBuilder()
        builder.button(text="Прикрепить файл", callback_data="file:attach")
        builder.button(text="Пропустить", callback_data="file:skip")
        builder.adjust(1)

        await message.answer("Хотите прикрепить файл?", reply_markup=builder.as_markup())
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


# Обработчик загрузки файла
@router.message(AppealForm.attaching_file, F.photo | F.document)
async def process_file_upload(message: Message, state: FSMContext):
    try:
        # Инициализируем переменную file_path
        file_path = None

        # Сохраняем файл
        file_dir = "uploads/"
        os.makedirs(file_dir, exist_ok=True)

        if message.photo:
            file_id = message.photo[-1].file_id
            file = await message.bot.get_file(file_id)
            file_path = f"{file_dir}{file.file_id}.jpg"
            await message.bot.download_file(file.file_path, file_path)
        elif message.document:
            file_id = message.document.file_id
            file = await message.bot.get_file(file_id)
            file_path = f"{file_dir}{message.document.file_name}"
            await message.bot.download_file(file.file_path, file_path)

        # Проверяем, был ли загружен файл
        if file_path is None:
            await message.answer("Файл не был загружен. Пожалуйста, отправьте фото или документ.")
            return

        # Обновляем состояние с путём к файлу
        await state.update_data(file_path=file_path)

        # Сохраняем данные в базу данных
        data = await state.get_data()
        await save_appeal_to_db(data, message.from_user.id)
        await message.answer("Ваше обращение успешно отправлено!")
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при загрузке файла: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")