from database import SessionLocal
from models import User
from sqlalchemy.orm import Session

def get_user_language_from_db(user_id: int) -> str:
    """
    Retrieves the language code associated with the given user ID from the database.

    Args:
        user_id (int): The unique Telegram user ID.

    Returns:
        str: The language code chosen by the user.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            return user.language_code
        return ""
    finally:
        db.close()

def set_user_language_in_db(user_id: int, language_code: str) -> None:
    """
    Sets the language code for the given user ID in the database.

    Args:
        user_id (int): The unique Telegram user ID.
        language_code (str): The language code to be set for the user.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            user.language_code = language_code
            db.commit()
    finally:
        db.close()