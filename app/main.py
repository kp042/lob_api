from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.api.endpoints import auth
from app.core.config import settings
from app.api.dependencies import get_current_active_user
from app.db.session import get_db, engine
from app.db.base import Base
from app.middleware.logging import log_requests_middleware
from app.api.endpoints import admin

# Create tables in the db
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LOB Data API",
    description="API for accessing Limit Order Book (LOB) data from Binance",
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

# Middleware for logging in db requests
app.middleware("http")(log_requests_middleware)

# Router for public endpoints
public_router = APIRouter()

@public_router.get("/")
async def root():
    return {"message": "LOB Data API is working!"}

@public_router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Connect public endpoints to the main app without dependencies
app.include_router(public_router, dependencies=[])

# Connect an authentication router without default security
app.include_router(auth.router, prefix="/auth", tags=["authentication"], dependencies=[])

# Connect the admin router
app.include_router(admin.router, prefix="/admin", tags=["administration"])

# Protected endpoint test
@app.get("/protected-test")
async def protected_test(current_user = Depends(get_current_active_user)):
    return {
        "message": "Вы успешно получили доступ к защищенному эндпоинту!",
        "user": current_user.username
    }

# Endpoint for checking the db
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

