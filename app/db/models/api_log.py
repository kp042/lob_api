from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Может быть None для публичных эндпоинтов
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    client_host = Column(String, nullable=False)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь с пользователем
    user = relationship("User", backref="api_logs")
    
    def __repr__(self):
        return f"<ApiLog(id={self.id}, endpoint='{self.endpoint}', method='{self.method}')>"
