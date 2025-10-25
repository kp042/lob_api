from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from pydantic import BaseModel

from app.services.crypto_service import CryptoService
from app.api.dependencies import get_current_active_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Модели ответов
class SymbolDataResponse(BaseModel):
    symbol: str
    data: List[dict]
    data_points: int

# Зависимость для сервиса
async def get_crypto_service() -> CryptoService:
    return CryptoService()

@router.get("/symbols", response_model=List[str])
async def get_available_symbols(
    crypto_service: CryptoService = Depends(get_crypto_service),
    current_user = Depends(get_current_active_user)
):
    """
    Получение списка доступных торговых пар
    (только символы, по которым есть данные за последние 24 часа)
    """
    logger.info(f"User {current_user.username} requested available symbols")
    
    symbols = await crypto_service.get_available_symbols()
    if not symbols:
        logger.warning("No symbols found in database")
        raise HTTPException(404, detail="No symbols found in the database")
    
    logger.debug(f"Returning {len(symbols)} symbols to user")
    return symbols

@router.get("/data/{symbol}", response_model=SymbolDataResponse)
async def get_symbol_data(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    crypto_service: CryptoService = Depends(get_crypto_service),
    current_user = Depends(get_current_active_user)
):
    """
    Получение данных по конкретной торговой паре
    Данные возвращаются в порядке убывания времени (сначала самые свежие)
    """
    logger.info(f"User {current_user.username} requested data for {symbol}, limit: {limit}")
    
    result = await crypto_service.get_symbol_data(symbol, limit)
    
    if not result['data']:
        logger.warning(f"No data found for symbol {symbol}")
        raise HTTPException(
            404, 
            detail=f"No data found for symbol {symbol} or symbol doesn't exist"
        )
    
    logger.debug(f"Returning {result['data_points']} data points for {symbol}")
    return result
