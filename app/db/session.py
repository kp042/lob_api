from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
 

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Нужно только для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
