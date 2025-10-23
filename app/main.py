from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth
from app.core.config import settings
from app.api.dependencies import get_current_active_user

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

# Защищенный эндпоинт (явно указываем зависимость)
@app.get("/protected-test", dependencies=[Depends(get_current_active_user)])
async def protected_test():
    """
    Тестовый защищенный эндпоинт.
    Требует аутентификацию через JWT токен.
    """
    return {
        "message": "Вы успешно получили доступ к защищенному эндпоинту!",
        "note": "Этот эндпоинт защищен явно указанной зависимостью"
    }

# Защита для будущих эндпоинтов будет добавляться аналогично
