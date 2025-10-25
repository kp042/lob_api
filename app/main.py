from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
from logging.handlers import RotatingFileHandler
import os

from app.api.endpoints import auth
from app.core.config import settings
from app.api.dependencies import get_current_active_user
from app.db.session import get_db, engine
from app.db.base import Base
from app.middleware.logging import log_requests_middleware
from app.api.endpoints import admin, crypto
from app.db.clickhouse import clickhouse_client


def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)    
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )    
    
    file_handler = RotatingFileHandler(
        f'{log_dir}/app.log',
        maxBytes=5242880,  # 5 MB
        backupCount=2
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)    
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)    
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)    
    
    logging.getLogger('app').setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)


setup_logging()

logger = logging.getLogger(__name__)

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
    logger.info("Root endpoint accessed")
    return {"message": "LOB Data API is working!"}

@public_router.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "version": "1.0.0"}

# Connect public endpoints to the main app without dependencies
app.include_router(public_router, dependencies=[])

# Connect an authentication router without default security
app.include_router(auth.router, prefix="/auth", tags=["authentication"], dependencies=[])

# Connect the admin router
app.include_router(admin.router, prefix="/admin", tags=["administration"])

# Connect crypto router
app.include_router(crypto.router, prefix="/crypto", tags=["cryptodata"])

# Protected endpoint test
@app.get("/protected-test")
async def protected_test(current_user = Depends(get_current_active_user)):
    logger.info(f"Protected endpoint accessed by user: {current_user.username}")
    return {
        "message": "You have successfully accessed the secure endpoint!",
        "user": current_user.username
    }

# Endpoint for checking the db
@app.get("/db-status")
async def db_status(db: Session = Depends(get_db)):
    from app.db.models.user import User
    from app.db.models.api_log import ApiLog
    
    user_count = db.query(User).count()
    log_count = db.query(ApiLog).count()
    
    logger.debug(f"DB status checked - Users: {user_count}, Logs: {log_count}")
    
    return {
        "database": "connected",
        "users_count": user_count,
        "api_logs_count": log_count
    }

# ClickHouse health check
@app.get("/clickhouse-health")
async def clickhouse_health():
    try:
        result = await clickhouse_client.execute("SELECT 1 as status")
        logger.debug("ClickHouse health check passed")
        return {"clickhouse": "connected", "status": "healthy"}
    except Exception as e:
        logger.error(f"ClickHouse health check failed: {e}")
        return {"clickhouse": "disconnected", "status": "unhealthy", "error": str(e)}

@app.on_event("startup")
async def startup_event():    
    await clickhouse_client.connect()
    logger.info("Application started with ClickHouse connection")

@app.on_event("shutdown")
async def shutdown_event():    
    await clickhouse_client.close()
    logger.info("ClickHouse connection closed. Application shutdown.")
