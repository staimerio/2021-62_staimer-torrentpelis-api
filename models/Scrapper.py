"""Model for chapters"""

# SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean

# SQLAlchemy_serializer
from sqlalchemy_serializer import SerializerMixin

# Services
from services.sqlalchemy.base import Base

# Time
from datetime import datetime


class Scrapper(Base, SerializerMixin):
    """Language Model"""
    __tablename__ = "scrapper"

    """Attributes"""
    scrapper = Column(Integer, primary_key=True)
    key = Column(String(200))
    value = Column(String(50))
    type = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)

    """Relationships"""

    """Serialize settings"""
    serialize_only = (
        'scrapper', 'key', 'value', 'type'
    )
