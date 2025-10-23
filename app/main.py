from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.endpoints import auth
from app.core.config import settings
from app.api.dependencies import get_current_active_user
from app.db.session import get_db, engine
from app.db.base import Base

from app.middleware.logging import log_requests_middleware


# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем приложение с защитой по умолчанию для ВСЕХ эндпоинтов
app = FastAPI(
    title="Crypto Data API",
    description="API для доступа к данным стаканов ордеров с Binance",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования
app.middleware("http")(log_requests_middleware)

# Создаем отдельный роутер для публичных эндпоинтов БЕЗ аутентификации
public_router = APIRouter()

@public_router.get("/")
async def root():
    return {"message": "Crypto Data API работает!"}

@public_router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Подключаем публичные эндпоинты к основному приложению БЕЗ зависимостей
app.include_router(public_router, dependencies=[])

# Подключаем роутер аутентификации БЕЗ защиты по умолчанию
app.include_router(auth.router, prefix="/auth", tags=["authentication"], dependencies=[])

# # Защищенный эндпоинт (явно указываем зависимость)
# @app.get("/protected-test", dependencies=[Depends(get_current_active_user)])
# async def protected_test():
#     """
#     Тестовый защищенный эндпоинт.
#     Требует аутентификацию через JWT токен.
#     """
#     return {
#         "message": "Вы успешно получили доступ к защищенному эндпоинту!",
#         "note": "Этот эндпоинт защищен явно указанной зависимостью"
#     }

# # Защита для будущих эндпоинтов будет добавляться аналогично

# Защищенный эндпоинт
@app.get("/protected-test")
async def protected_test(current_user = Depends(get_current_active_user)):
    return {
        "message": "Вы успешно получили доступ к защищенному эндпоинту!",
        "user": current_user.username
    }

# Эндпоинт для проверки базы данных
@app.get("/db-status")
async def db_status(db: Session = Depends(get_db)):
    from app.db.models.user import User
    from app.db.models.api_log import ApiLog

    user_count = db.query(User).count()
    log_count = db.query(ApiLog).count()
    
    return {
        "database": "connected",
        "users_count": user_count,
        "api_logs_count": log_count
    }

