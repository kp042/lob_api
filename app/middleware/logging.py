from fastapi import Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.api_log import ApiLog
from app.core.security import verify_token
import time
import logging


logger = logging.getLogger(__name__)


"""
TODO:
    Add asynchronous logging
    Send logging to a background task

    async def async_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        asyncio.create_task(save_log_async(request, response, process_time))

    async def save_log_async(request, response, process_time):
        # Asynchronously save the log
        # This doesn't block the main thread
        pass
"""

async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        raise    
    
    try:
        db = SessionLocal()
        user_id = None
        authorization = request.headers.get("authorization")
        
        # Extract user_id from token
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            username = verify_token(token)
            
            if username:
                # Find a user in the db by username
                from app.db.models.user import User
                user = db.query(User).filter(User.username == username).first()
                if user:
                    user_id = user.id
        
        # Create a log entry
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

        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Duration: {process_time:.3f}s "
            f"User: {user_id or 'anonymous'}"
        )
    except Exception as e:
        logger.error(f"Logging error: {e}")
        if db:
            db.rollback()        
    finally:
        if db:
            db.close()
    
    return response
