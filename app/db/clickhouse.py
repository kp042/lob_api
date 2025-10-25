import aiohttp
from app.core.config import settings
import logging
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)


class AsyncClickHouseClient:
    def __init__(self):
        self.base_url = f"http://{settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}"
        self.auth = aiohttp.BasicAuth(
            settings.CLICKHOUSE_USER, 
            settings.CLICKHOUSE_PASSWORD
        )
        self.database = settings.CLICKHOUSE_DATABASE
        self.session: Optional[aiohttp.ClientSession] = None
        logger.debug("ClickHouse client initialized")

    async def connect(self):
        if self.session is None or self.session.closed:
            try:
                connector = aiohttp.TCPConnector(
                    limit=100,
                    limit_per_host=20,
                    keepalive_timeout=30
                )

                self.session = aiohttp.ClientSession(
                    base_url=self.base_url,
                    auth=self.auth,
                    connector=connector,
                    timeout=aiohttp.ClientTimeout(total=30.0)
                )

                # Connection check
                result = await self.execute("SELECT 1 as test")
                logger.info("Successfully connected to ClickHouse")

            except Exception as e:
                logger.error(f"Failed to connect to ClickHouse: {e}")
                await self.close()
                raise

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
            logger.debug("ClickHouse connection closed")

    async def execute(
        self, 
        query: str, 
        params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL query
        
        Args:
            query: SQL query with placeholders {name}
            params: Dict of parameters for query
            
        Returns:
            List of dicts with query results
        """
        if self.session is None or self.session.closed:
            await self.connect()

        try:
            if "FORMAT" not in query.upper():
                query = f"{query} FORMAT JSON"

            if params:
                # ClickHouse uses the {name:DataType} for params
                formatted_params = {}
                for key, value in params.items():
                    if isinstance(value, str):
                        formatted_params[key] = f"'{value}'"
                    else:
                        formatted_params[key] = str(value)
                
                # Replacing placeholders in a query
                for key, value in formatted_params.items():
                    placeholder = "{" + key + "}"
                    if placeholder in query:
                        query = query.replace(placeholder, value)
            
            logger.debug(f"Executing ClickHouse query: {query[:200]}...")
            
            async with self.session.post(
                "/",
                data=query,
                params={"database": self.database}
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"ClickHouse error {response.status}: {error_text}")
                    raise Exception(f"ClickHouse error: {error_text}")
                
                data = await response.json()
                logger.debug(f"Query executed successfully, returned {len(data.get('data', []))} rows")
                return data.get('data', [])

        except aiohttp.ClientError as e:
            logger.error(f"ClickHouse HTTP client error: {e}")
            raise
        except Exception as e:
            logger.error(f"ClickHouse query error: {e}")
            raise

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

clickhouse_client = AsyncClickHouseClient()
