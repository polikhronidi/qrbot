from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define the URL for the SQLite database
DATABASE_URL = "sqlite:///./test.db"

# SQLAlchemy engine creation
# Note: This section sets up the connection to the database.
engine = create_engine(DATABASE_URL)

# SQLAlchemy session creation
# Note: This section sets up the session management for interacting with the database.
# It provides a central point for creating new sessions and managing transactions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)