"""
Abstract Base Model
"""
from datetime import datetime

from sqlalchemy import Column, DateTime


class BaseModal:
    """
    Datetime created_at and updated_at
    """
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
