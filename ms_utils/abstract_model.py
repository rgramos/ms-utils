from datetime import datetime

from sqlalchemy import Column, DateTime


class BaseModal:
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
