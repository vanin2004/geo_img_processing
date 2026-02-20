from fastapi import Depends
from sqlalchemy.orm import Session

from src.injectors.connections import get_db, get_fs
from src.services import FileService, TaskService, WorkerService
from src.services.algorithms import AlgorithmAbstractFactory


def get_task_service(
    db: Session = Depends(get_db),
) -> TaskService:
    """Зависимость для получения TaskService, привязанного к текущей сессии БД."""
    return TaskService(db_session=db)


def get_worker_service(
    db: Session = Depends(get_db),
    file_service: FileService = Depends(get_fs),
) -> WorkerService:
    """Зависимость для получения WorkerService, привязанного к текущей сессии БД и FileService."""
    worker_service = WorkerService(db=db, file_service=file_service)
    return worker_service


def get_algorithm_factory() -> type[AlgorithmAbstractFactory]:
    """Зависимость для получения фабрики алгоритмов."""
    return AlgorithmAbstractFactory
