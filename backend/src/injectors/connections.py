import time
from functools import lru_cache
from typing import Generator

from fastapi import Depends
from requests import Session as RequestsSession
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.config import fs_config, pg_config
from src.models import Base
from src.services.files import FileService


class DatabaseError(Exception):
    """Базовый класс для ошибок бд"""


class DatabaseConnectionError(DatabaseError):
    """Ошибка подключения к базе данных"""


class DatabaseOperationError(DatabaseError):
    """Ошибка выполнения операции с базой данных"""


@lru_cache(maxsize=1)
def create_engine():
    """Создает и кэширует синхронный движок базы данных."""

    config = pg_config
    return sa_create_engine(config.database_url, echo=config.debug_mode)


@lru_cache(maxsize=1)
def create_database() -> sessionmaker[Session]:
    """Создает и кэширует фабрику синхронных сессий."""

    engine = create_engine()
    return sessionmaker(bind=engine)


def initialize_database() -> None:
    """Создает таблицы в базе данных при старте приложения (синхронно)."""

    config = pg_config
    engine = create_engine()
    retries = getattr(config, "retries", 1)
    for attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except SQLAlchemyError as e:
            if attempt < retries - 1:
                time.sleep(getattr(config, "retry_delay_sec", 1))
            else:
                raise DatabaseConnectionError(
                    f"Error creating database after {retries} attempts: {e}"
                )


def get_db(
    session_factory: sessionmaker[Session] = Depends(create_database),
) -> Generator[Session, None, None]:
    """
    Генератор сессий базы данных для использования в FastAPI зависимостях.
    Обеспечивает автоматический commit при успехе и rollback при ошибке.
    """
    session: Session = session_factory()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise DatabaseOperationError("Database transaction failed and was rolled back.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_request_session() -> Generator[RequestsSession, None, None]:
    """Зависимость для получения сессии базы данных."""

    with RequestsSession() as session:
        yield session


def get_fs(r_session=Depends(get_request_session)) -> FileService:
    """Зависимость для получения сессии базы данных в файловом сервисе."""

    return FileService(
        session=r_session,
        host=fs_config.host,
        port=fs_config.port,
        timeout_seconds=fs_config.timeout_seconds,
    )
