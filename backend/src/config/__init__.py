from .fastapi import FastAPIConfig
from .fs import FsConfig
from .pg import PgConfig
from .settings import settings

pg_config = PgConfig(
    database_url=settings.database_url,
    retries=settings.db_retries,
    retry_delay_sec=settings.db_retry_delay,
    debug_mode=settings.debug,
)
fs_config = FsConfig(
    host=settings.file_storage_host,
    port=settings.file_storage_port,
    timeout_seconds=settings.file_storage_timeout,
)
fastapi_config = FastAPIConfig(
    host=settings.app_host,
    port=settings.app_port,
    log_level="debug" if settings.debug else "info",
    reload=settings.debug,
)
__all__ = [
    "PgConfig",
    "FsConfig",
    "FastAPIConfig",
    "pg_config",
    "fs_config",
    "fastapi_config",
]
