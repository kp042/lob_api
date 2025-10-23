from fastapi import Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.api_log import ApiLog
import time

async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Пропускаем запрос через цепочку middleware
    response = await call_next(request)
    
    # Логируем после получения ответа
    process_time = time.time() - start_time
    
    # Создаем сессию базы данных вручную
    db = SessionLocal()
    try:
        # Получаем пользователя из токена (если есть)
        user_id = None
        authorization = request.headers.get("authorization")
        
        # if authorization and authorization.startswith("Bearer "):
        #     token = authorization.replace("Bearer ", "")
        #     # Здесь нужно добавить логику извлечения user_id из токена
        #     # Пока оставляем как есть
        
        # Создаем запись в логе
        api_log = ApiLog(
            user_id=user_id,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        db.add(api_log)
        db.commit()
        
    except Exception as e:
        # В случае ошибки логирования - откатываем транзакцию
        db.rollback()
        # Но не прерываем запрос - логирование не должно ломать API
        print(f"Logging error: {e}")
    finally:
        db.close()
    
    return response
