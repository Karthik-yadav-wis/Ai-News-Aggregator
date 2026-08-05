from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Interest(Base):
    __tablename__ = "interests"
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    name = Column(
        String,
        unique=True,
        nullable=False
    )
    image_url = Column(String, nullable=True)

class UserInterest(Base):
    __tablename__ = "user_interests"
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )
    interest_id = Column(
        Integer,
        ForeignKey("interests.id")
    )

class Article(Base):
    """
    Tracks every article URL that has ever been chunked + embedded into
    FAISS, so repeated /fetch-news calls (manual, on save, or from the
    scheduler) don't keep re-embedding the same articles over and over.
    """
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False, index=True)
    title = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow)