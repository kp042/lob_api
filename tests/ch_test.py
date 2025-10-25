import asyncio
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

import logging
from app.db.clickhouse import AsyncClickHouseClient


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_clickhouse():
    logger.info("Starting ClickHouse connection test...")
    
    async with AsyncClickHouseClient() as client:
        try:
            # Test: connection to Clickhouse
            result = await client.execute("SELECT 1 as test_value, 'hello' as greeting")
            logger.info(f"Connection test result: {result}")
            
            # Test: getting all symbols
            symbols = await client.execute("""
                SELECT DISTINCT symbol 
                FROM blob_rest_all_aggregated 
                LIMIT 5
            """)
            symbol_list = [s['symbol'] for s in symbols]
            logger.info(f"Available symbols: {symbol_list}")
            
            # Test: queries with params
            if symbol_list:
                first_symbol = symbol_list[0]
                data = await client.execute("""
                    SELECT symbol, best_bid, best_ask, event_time
                    FROM blob_rest_all_aggregated 
                    WHERE symbol = {symbol}
                    LIMIT 3
                """, {'symbol': first_symbol})
                logger.info(f"Data for {first_symbol}: {data}")
                
            logger.info("All tests passed successfully!")
            
        except Exception as e:
            logger.error(f"Test failed with error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_clickhouse())
