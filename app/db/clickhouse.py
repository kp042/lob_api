import aiohttp
from app.core.config import settings
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AsyncClickHouseClient:
    """
    Асинхронный клиент для работы с ClickHouse через aiohttp
    """
    
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
        """Создаем aiohttp сессию"""
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
                
                # Проверяем подключение
                result = await self.execute("SELECT 1 as test")
                logger.info("Successfully connected to ClickHouse")
                
            except Exception as e:
                logger.error(f"Failed to connect to ClickHouse: {e}")
                await self.close()
                raise

    async def close(self):
        """Закрываем сессию"""
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
        Выполняет SQL запрос к ClickHouse и возвращает результат
        
        Args:
            query: SQL запрос с плейсхолдерами {name}
            params: Словарь параметров для подстановки в запрос
            
        Returns:
            Список словарей с результатами запроса
        """
        if self.session is None or self.session.closed:
            await self.connect()

        try:
            # Добавляем FORMAT JSON если его нет в запросе
            if "FORMAT" not in query.upper():
                query = f"{query} FORMAT JSON"

            # Используем встроенную параметризацию ClickHouse
            if params:
                # ClickHouse использует синтаксис {name:DataType} для параметров
                formatted_params = {}
                for key, value in params.items():
                    if isinstance(value, str):
                        # Для строк указываем тип String
                        formatted_params[key] = f"'{value}'"
                    else:
                        # Для чисел и других типов передаем как есть
                        formatted_params[key] = str(value)
                
                # Заменяем плейсхолдеры в запросе
                for key, value in formatted_params.items():
                    placeholder = "{" + key + "}"
                    if placeholder in query:
                        query = query.replace(placeholder, value)
            
            logger.debug(f"Executing ClickHouse query: {query[:200]}...")

            # Выполняем POST запрос
            async with self.session.post(
                "/",
                data=query,
                params={"database": self.database}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"ClickHouse error {response.status}: {error_text}")
                    raise Exception(f"ClickHouse error: {error_text}")
                
                # Парсим JSON ответ
                data = await response.json()
                logger.debug(f"Query executed successfully, returned {len(data.get('data', []))} rows")
                return data.get('data', [])

        except aiohttp.ClientError as e:
            logger.error(f"ClickHouse HTTP client error: {e}")
            raise
        except Exception as e:
            logger.error(f"ClickHouse query error: {e}")
            raise

    # Контекстный менеджер для использования с async with
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# Глобальный экземпляр
clickhouse_client = AsyncClickHouseClient()
