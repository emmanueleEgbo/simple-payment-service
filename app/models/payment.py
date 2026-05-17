"""Defines the SQLAlchemy ORM model representing a Payment entity."""

from sqlalchemy import Column, Integer, String
from app.core.async_db import Base


class Payment(Base):
    pass