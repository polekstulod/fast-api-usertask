from sqlalchemy import Integer, String, DateTime, text, Boolean
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'Users'

    user_id = Column(String(36), primary_key=True, default=text('UUID()'))
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=text('NOW()'))
    updated_at = Column(DateTime, onupdate=text('NOW()'))
    status = Column(Boolean, default=True)
    tasks = relationship('Task', back_populates='author')
