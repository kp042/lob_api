from typing import List, Dict, Any
from app.repositories.crypto_repository import CryptoRepository
import logging

logger = logging.getLogger(__name__)

class CryptoService:
    """
    Сервис для работы с крипто-данными
    """
    
    def __init__(self):
        self.repository = CryptoRepository()
        logger.debug("CryptoService initialized")
    
    async def get_available_symbols(self) -> List[str]:
        """Получает список доступных символов"""
        logger.debug("Getting available symbols from service")
        
        return await self.repository.get_available_symbols()
    
    async def get_symbol_data(self, symbol: str, limit: int = 100) -> Dict[str, Any]:        
        logger.debug(f"Service: getting data for {symbol}")
        data = await self.repository.get_symbol_data(symbol.upper(), limit)

        return {
            'symbol': symbol,
            'data': data,
            'data_points': len(data)
        }
