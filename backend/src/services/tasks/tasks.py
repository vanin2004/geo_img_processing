import uuid

from sqlalchemy.orm import Session

from src.models.orm_models import Task, TaskStateEnum
from src.services.algorithms import BaseAlgorithm


class TaskServiceError(Exception):
    """Базовый класс для ошибок сервиса задач."""


class InvalidAlgorithmParamsError(TaskServiceError):
    """Ошибка, возникающая при передаче некорректных параметров алгоритма."""


class TaskNotFoundError(TaskServiceError):
    """Ошибка, возникающая при попытке получить несуществующую задачу."""


class TaskCreationError(TaskServiceError):
    """Ошибка, возникающая при создании задачи."""


class TaskService:
    """Сервис для управления задачами обработки геопространственных данных."""

    def __init__(self, db_session: Session):
        self._db = db_session

    def create_task(
        self,
        algorithm: BaseAlgorithm,
        input_file_id: str,
        output_file_full_path: str | None = None,
    ) -> Task:
        """Создает новую задачу обработки данных.

        Args:
            algorithm (BaseAlgorithm): Алгоритм для выполнения.
            params (dict): Параметры алгоритма.
            input_file_id (str): Идентификатор входного файла.
            output_file_full_path (str | None): Полный путь к выходному файлу (необязательно).
        Returns:
            Task: Созданная задача.
        """

        task = Task(
            id=uuid.uuid4(),
            algorithm=algorithm.name,
            params=algorithm._params.model_dump(),
            input_file_id=input_file_id,
            status=TaskStateEnum.PENDING,
            output_file_full_path=output_file_full_path,
        )
        self._db.add(task)
        try:
            self._db.flush()
        except Exception as e:
            print(f"Error creating task: {e}")
            raise TaskCreationError(f"Failed to create task: {e}")
        return task

    def list_tasks(self) -> list[Task]:
        """Возвращает список всех задач."""
        try:
            tasks = self._db.query(Task).all()
        except Exception as e:
            print(f"Error listing tasks: {e}")
            raise TaskServiceError(f"Failed to list tasks: {e}")
        return tasks

    def get_task(self, task_id: uuid.UUID) -> Task:
        """Возвращает задачу по ее идентификатору.

        Args:
            task_id (uuid.UUID): Идентификатор задачи.
        Returns:
            Task: Найденная задача.
        Raises:
            TaskNotFoundError: Если задача с указанным идентификатором не найдена.
        """
        try:
            task = self._db.query(Task).filter(Task.id == task_id).one_or_none()
        except Exception as e:
            raise TaskServiceError(f"Failed to get task: {e}")
        if task is None:
            raise TaskNotFoundError(f"Task with id {task_id} not found")
        return task
