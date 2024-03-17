# models.py

# This module defines SQLAlchemy models for the bot's database schema.

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Base class for all SQLAlchemy models
Base = declarative_base()

class User(Base):
    """
    Represents a user in the bot's database.

    Attributes:
        id (int): The unique identifier for the user.
        telegram_id (int): The Telegram user ID.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        language_code (str): The language code chosen by the user.
    """
    __tablename__ = "users"

    # Primary key representing the user's ID
    id = Column(Integer, primary_key=True, index=True)

    # Unique Telegram ID for the user
    telegram_id = Column(Integer, unique=True, index=True)

    # First name of the user
    first_name = Column(String, index=True)

    # Last name of the user
    last_name = Column(String, index=True)

    # Language code chosen by the user
    language_code = Column(String, index=True)