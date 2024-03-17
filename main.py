import datetime
import io
import logging
import sqlite3
import cv2
import qrcode
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import filters
from aiogram.utils import executor
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
from pyzbar.pyzbar import decode
from messages import START_MESSAGES, HELP_MESSAGES, BOTS_MESSAGES, PRIVACY_MESSAGES, \
    INSTRUCTIONS_MESSAGES, STICKER_RESPONSE, VOICE_RESPONSE, VIDEO_RESPONSE, \
    GREETING_MESSAGES, MAX_LENGTH_ERROR_MESSAGES

# Basic configuration for logging errors
logging.basicConfig(level=logging.ERROR)

# Defining SQLAlchemy Base
Base = declarative_base()

# Supported languages for the bot
SUPPORTED_LANGUAGES = ["🇬🇧 English", "🇷🇺 Русский", "🇵🇹 Português", "🇮🇩 Indonesia", "🇪🇸 Español", "🇺🇿 O'zbek tili"]

# Default language for users
DEFAULT_LANGUAGE = "🇬🇧 English"

# Inline keyboard markup for language selection
LANGUAGE_KEYBOARD = InlineKeyboardMarkup(row_width=2)

# Populating language keyboard
for lang_code in SUPPORTED_LANGUAGES:
    LANGUAGE_KEYBOARD.add(InlineKeyboardButton(text=lang_code, callback_data=f"set_language:{lang_code}"))

# Database URL
DATABASE_URL = "sqlite:///users.db"

# Engine for database connection
engine = create_engine(DATABASE_URL)

# Channel link text based on language
CHANNEL_LINK_TEXT = {
    "🇬🇧 English": "Subscribe",
    "🇷🇺 Русский": "Подписаться",
    "🇵🇹 Português": "Inscreva-se",
    "🇮🇩 Indonesia": "Berlangganan",
    "🇪🇸 Español": "Suscríbete",
    "🇺🇿 O'zbek tili": "Obuna bo'ling",
}

# Telegram channel URL
TELEGRAM_CHANNEL_URL = "https://t.me/hvntr_bots"


def read_qr_code(image_path):
    """
    Reads QR code from the given image path.

    Args:
        image_path (str): Path to the image containing the QR code.

    Returns:
        str: Decoded content of the QR code.
    """
    img = cv2.imread(image_path)
    decoded_objects = decode(img)

    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            try:
                if obj.data.startswith(b'http://') or obj.data.startswith(b'https://'):
                    return f"This is a URL: {obj.data.decode('utf-8')}"
                elif obj.data.startswith(b'BEGIN:VCARD'):
                    return f"This is a vCard: {obj.data.decode('utf-8')}"
                else:
                    return f"{obj.data.decode('utf-8')}"
            except Exception as e:
                print(f"Error decoding QR code content: {e}")
                return f"Error decoding QR code content: {e}"

    return "No QR code or unsupported type detected"


def create_db():
    """Creates the database tables if not exist."""
    Base.metadata.create_all(bind=engine)


def get_user_language(user_id):
    """
    Retrieves user language from the database.

    Args:
        user_id (int): Unique identifier for the user.

    Returns:
        str: Language code of the user.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if user and user.language_code:
            return user.language_code
        return DEFAULT_LANGUAGE
    finally:
        session.close()


def get_user_language_from_db(user_id):
    """
    Retrieves user language from the database.

    Args:
        user_id (int): Unique identifier for the user.

    Returns:
        str: Language code of the user.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        return user.language_code if user and user.language_code else DEFAULT_LANGUAGE
    except Exception as e:
        print(f"Error while getting user language: {e}")
    finally:
        session.close()


def set_user_language_callback(user_id, language_code):
    """
    Sets user language in the database.

    Args:
        user_id (int): Unique identifier for the user.
        language_code (str): Language code to be set.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if user:
            user.language_code = language_code
            session.commit()
    except Exception as e:
        print(f"Error while setting user language: {e}")
    finally:
        session.close()


# SQLAlchemy User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    language_code = Column(String)
    language = Column(String)


# SessionLocal for database interaction
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize Bot and Dispatcher
bot = Bot(token="yourtokenhere")
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


async def get_db():
    """
    Gets the database session asynchronously.

    Returns:
        Session: Database session.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, SessionLocal)


def get_greeting_message(hour, language):
    """
    Generates a greeting message based on the time of the day and user language.

    Args:
        hour (int): Current hour.
        language (str): User's language code.

    Returns:
        str: Greeting message.
    """
    if language in GREETING_MESSAGES:
        if 10 <= hour < 15:
            return GREETING_MESSAGES[language]["morning"]
        elif 15 <= hour < 20:
            return GREETING_MESSAGES[language]["afternoon"]
        elif 20 <= hour < 24:
            return GREETING_MESSAGES[language]["evening"]
        else:
            return GREETING_MESSAGES[language]["night"]
    else:
        return "Hello"


def get_instructions_message(language):
    """
    Retrieves instructions message based on language.

    Args:
        language (str): User's language code.

    Returns:
        str: Instructions message.
    """
    return INSTRUCTIONS_MESSAGES[language]


@dp.message_handler(filters.Command("start"))
async def start_message(message: types.Message):
    """
    Handles /start command and sends a welcome message to the user.

    Args:
        message (types.Message): Message object.
    """
    user_id, first_name, last_name = (
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.last_name,
    )

    session = await get_db()
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            new_user = User(
                telegram_id=user_id,
                first_name=first_name,
                last_name=last_name,
                language_code=DEFAULT_LANGUAGE,
                language="",
            )
            session.add(new_user)
            session.commit()
    except Exception as e:
        print(f"Error while checking or creating user: {e}")
    finally:
        session.close()

    lang_code = get_user_language(user_id)
    current_time = datetime.datetime.now().time()
    greeting_message = get_greeting_message(current_time.hour, lang_code)
    start_message_text = START_MESSAGES[lang_code]

    await bot.send_photo(
        user_id,
        types.InputFile("img/image.png"),
        caption=f"<b>{greeting_message}, {first_name}!</b> {start_message_text}",
        parse_mode='HTML'
    )


# Message handler for language command
@dp.message_handler(filters.Command("language"))
async def language_command(message: types.Message):
    """
    Handles the /language command by sending a language selection keyboard.

    Args:
        message (types.Message): Message object.
    """
    user_id = message.from_user.id
    await bot.send_message(user_id, "Choose your preferred language:", reply_markup=LANGUAGE_KEYBOARD)


# Message handler for help command
@dp.message_handler(filters.Command("help"))
async def help_message(message: types.Message):
    """
    Handles the /help command by sending help text to the user.

    Args:
        message (types.Message): Message object.
    """
    user_id = message.from_user.id
    lang_code = get_user_language_from_db(user_id)
    help_text = HELP_MESSAGES[lang_code]
    await message.reply(help_text, parse_mode='HTML')


# Message handler for privacy command
@dp.message_handler(filters.Command("privacy"))
async def privacy_message(message: types.Message):
    """
    Handles the /privacy command by sending privacy policy text to the user.

    Args:
        message (types.Message): Message object.
    """
    user_id = message.from_user.id
    lang_code = get_user_language_from_db(user_id)
    privacy_text = PRIVACY_MESSAGES[lang_code]
    await message.reply(privacy_text, parse_mode='HTML')


# Message handler for bots command
@dp.message_handler(filters.Command("bots"))
async def bots_message(message: types.Message):
    """
    Handles the /bots command by sending information about bots and a channel link.

    Args:
        message (types.Message): Message object.
    """
    user_id = message.from_user.id
    lang_code = get_user_language_from_db(user_id)
    bots_text = BOTS_MESSAGES[lang_code]
    inline_keyboard = types.InlineKeyboardMarkup()
    channel_link_text = CHANNEL_LINK_TEXT[lang_code]
    inline_keyboard.add(types.InlineKeyboardButton(text=channel_link_text, url=TELEGRAM_CHANNEL_URL))
    await message.reply(bots_text, parse_mode='HTML', reply_markup=inline_keyboard)


# Message handler for stickers
@dp.message_handler(content_types=types.ContentType.STICKER)
async def handle_sticker(message: types.Message):
    """
    Handles stickers by sending a response based on user language.

    Args:
        message (types.Message): Message object.
    """
    user_id = message.from_user.id
    lang_code = get_user_language_from_db(user_id)
    sticker_response = STICKER_RESPONSE[lang_code]
    await message.reply(sticker_response, parse_mode='HTML')


# Message handler for voice messages
@dp.message_handler(content_types=types.ContentType.VOICE)
async def voice_handler(message: types.Message):
    """
    Handles voice messages by sending a response based on user language.

    Args:
        message (types.Message): Message object.
    """
    user_id = message.from_user.id
    lang_code = get_user_language_from_db(user_id)
    response_text = VOICE_RESPONSE[lang_code]
    await message.reply(response_text)


# Message handler for video messages
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def video_handler(message: types.Message):
    """
    Handles video messages by sending a response based on user language.

    Args:
        message (types.Message): Message object.
    """
    user_id = message.from_user.id
    lang_code = get_user_language_from_db(user_id)
    response_text = VIDEO_RESPONSE[lang_code]
    await message.reply(response_text)


# Message handler for text messages
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text_message(message: types.Message):
    """
    Handles text messages by generating a QR code if the content is within limits.

    Args:
        message (types.Message): Message object.
    """
    try:
        content = message.text
        if len(content) <= 2953:
            img = qrcode.make(content)
            img_byte_array = io.BytesIO()
            img.save(img_byte_array, format='PNG')
            img_byte_array.seek(0)
            await bot.send_photo(message.chat.id, types.InputFile(img_byte_array, filename='qrcode.png'),
                                 caption=content)
        else:
            lang_code = get_user_language_from_db(message.from_user.id)
            max_length_error_text = MAX_LENGTH_ERROR_MESSAGES[lang_code]
            await message.reply(max_length_error_text)
    except Exception as e:
        chat_id = -1000000000000
        await handle_errors(e, chat_id)


# Message handler for photos
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    """
    Handles photos by reading QR code from the photo and sending the decoded content.

    Args:
        message (types.Message): Message object.
    """
    try:
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        with open("qr_code_image.jpg", 'wb') as new_file:
            new_file.write(downloaded_file.read())

        content = read_qr_code("qr_code_image.jpg")

        if content:
            await message.reply(f"{content}", disable_web_page_preview=True)
        else:
            await message.reply("The QR code wasn't detected or its content couldn't be read, try another QR code.")
    except Exception as e:
        chat_id = -1000000000000
        await handle_errors(e, chat_id)


# Callback query handler for language selection
@dp.callback_query_handler(lambda c: c.data.startswith('set_language'))
async def process_language_callback(callback_query: types.CallbackQuery):
    """
    Handles language selection callback query.

    Args:
        callback_query (types.CallbackQuery): Callback query object.
    """
    lang_code = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id

    current_language = get_user_language_from_db(user_id)
    set_user_language_callback(user_id, lang_code)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    notification_text = f"Your language has been changed from {current_language} to {lang_code}."
    await bot.send_message(user_id, notification_text)

    await bot.answer_callback_query(callback_query.id, text=f"Language set to {lang_code}")


if __name__ == '__main__':
    create_db()
    executor.start_polling(dp, skip_updates=False)