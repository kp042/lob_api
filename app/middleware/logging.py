from fastapi import Request
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.api_log import ApiLog
from app.core.security import verify_token
import time

async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()    
    response = await call_next(request)    
    process_time = time.time() - start_time
    
    db = SessionLocal()
    try:
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
    except Exception as e:
        db.rollback()
        print(f"Logging error: {e}")
    finally:
        db.close()
    
    return response
