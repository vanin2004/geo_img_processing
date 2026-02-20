import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.models.orm_models import Task, TaskStateEnum

from .algorithms import AlgorithmAbstractFactory
from .files import FileService


class WorkerServiceError(Exception):
    """Базовый класс для ошибок сервиса воркера."""


class TaskNotFoundError(WorkerServiceError):
    """Ошибка, возникающая при попытке получить несуществующую задачу."""


class FileNotFoundError(WorkerServiceError):
    """Ошибка, возникающая при попытке получить несуществующий файл."""


class FileUploadError(WorkerServiceError):
    """Ошибка, возникающая при загрузке файла."""


class AlgorithmExecutionError(WorkerServiceError):
    """Ошибка, возникающая при выполнении алгоритма."""


class WorkerService:
    def __init__(
        self,
        db: Session,
        file_service: FileService,
    ):
        self._db = db
        self._file_service = file_service

    def run(self, task_id: uuid.UUID) -> None:
        """Запускает выполнение алгоритма обработки данных."""
        task = self._db.get(Task, task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with id {task_id} not found.")
        task.state = TaskStateEnum.RUNNING
        task.datetime_start = datetime.now(timezone.utc)
        self._db.commit()

        try:
            algorithm = AlgorithmAbstractFactory.get_algorithm(task.algorithm)
            params = algorithm.get_pydantic_model().model_validate(task.params)

            file_meta = self._file_service.get_file_meta(task.input_file_id)
            file_bytes = self._file_service.get_file(task.input_file_id)

            output_bytes = algorithm.run(
                file_bytes, file_ext=file_meta.file_extension, params=params
            )

            file_name = f"processed_{file_meta.filename}"
            file_extension = file_meta.file_extension
            file_path = file_meta.path

            uploaded = self._file_service.post_file(
                filename=file_name,
                file_extension=file_extension,
                path=file_path,
                file_content=output_bytes,
                comment=(
                    f"Processed file: {file_meta.filename}\n"
                    f"uuid: {file_meta.uuid}\nalgorithm: {algorithm.name()}\nparams: {params.model_dump()}"
                ),
            )

            task.output_file_id = uploaded.uuid
            task.output_file_full_path = f"{uploaded.path.rstrip('/')}/{uploaded.filename}.{uploaded.file_extension}"
            task.state = TaskStateEnum.DONE
            task.datetime_end = datetime.now(timezone.utc)
            self._db.commit()

        except Exception as e:
            task.state = TaskStateEnum.ERROR
            task.error = str(e)
            task.datetime_end = datetime.now(timezone.utc)
            self._db.commit()
            raise AlgorithmExecutionError(f"Algorithm execution failed: {e}")
