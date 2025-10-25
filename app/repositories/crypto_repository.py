from typing import List, Dict, Any
from app.db.clickhouse import clickhouse_client
import logging


logger = logging.getLogger(__name__)


class CryptoRepository:    
    async def get_available_symbols(self) -> List[str]:
        """active symbols for 24 hours"""
        query = """
        SELECT DISTINCT symbol 
        FROM blob_rest_all_aggregated 
        WHERE event_time >= (now() - 86400000)
        ORDER BY symbol
        """

        try:
            logger.debug("Fetching available symbols from ClickHouse")
            result = await clickhouse_client.execute(query)
            symbols = [row['symbol'] for row in result]
            logger.info(f"Found {len(symbols)} available symbols")
            return symbols
        except Exception as e:
            logger.error(f"Error getting available symbols: {e}")
            return []

    async def get_symbol_data(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        # placeholders {name}
        query = """
        SELECT *
        FROM blob_rest_all_aggregated 
        WHERE symbol = {symbol}
        ORDER BY event_time DESC
        LIMIT {limit}
        """
        
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        try:
            logger.debug(f"Fetching data for symbol {symbol}, limit: {limit}")
            data = await clickhouse_client.execute(query, params)
            logger.info(f"Retrieved {len(data)} records for symbol {symbol}")
            return data
        except Exception as e:
            logger.error(f"Error getting data for symbol {symbol}: {e}")
            return []
