from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth  # Импортируем наш роутер аутентификации
from app.core.config import settings
from app.api.dependencies import get_current_active_user


app = FastAPI(
    title="Crypto Data API",
    description="API для доступа к данным стаканов ордеров с Binance",
    version="1.0.0"
)

# CORS middleware - позволяет браузерным приложениям обращаться к нашему API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер аутентификации
app.include_router(auth.router, prefix="/auth", tags=["authentication"])

@app.get("/")
async def root():
    return {"message": "Crypto Data API работает!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Добавим тестовый защищенный эндпоинт для демонстрации
@app.get("/protected-test")
async def protected_test(current_user = Depends(get_current_active_user)):
    """
    Тестовый защищенный эндпоинт.
    Требует аутентификацию через JWT токен.
    """
    return {
        "message": "Вы успешно получили доступ к защищенному эндпоинту!",
        "user": current_user.username
    }
