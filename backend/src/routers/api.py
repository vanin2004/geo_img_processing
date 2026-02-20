import uuid

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter

from src.injectors.services import get_task_service
from src.models.schemas import TaskCreate, TaskRead
from src.services import (
    AlgorithmAbstractFactory,
    InvalidAlgorithmParamsError,
    TaskNotFoundError,
    TaskService,
)

router = APIRouter(prefix="/api")

# # Строится один раз при загрузке модуля — к этому моменту все алгоритмы
# # уже зарегистрированы через @register_algorithm в algorithms/__init__.py.
# _algorithms_openapi_extra = {
#     "responses": {
#         "200": {
#             "description": "Словарь {имя_алгоритма: JSON-схема параметров}",
#             "content": {
#                 "application/json": {
#                     "schema": {
#                         "type": "object",
#                         "properties": {
#                             name: {
#                                 "$ref": f"#/components/schemas/{algo_cls.get_pydantic_model().__name__}"
#                             }
#                             for name, algo_cls in AlgorithmAbstractFactory.registry.items()
#                         },
#                     }
#                 }
#             },
#         }
#     }
# }


# @router.get(
#     "/tasks/available-algorithms",
#     response_model=None,
#     openapi_extra=_algorithms_openapi_extra,
#     summary="Доступные алгоритмы и схемы их параметров",
# )
# def get_available_algorithms() -> dict[str, dict]:
#     """Возвращает словарь {имя_алгоритма: JSON-схема параметров}."""
#     return {
#         name: algo_cls.get_pydantic_model().model_json_schema()
#         for name, algo_cls in AlgorithmAbstractFactory.registry.items()
#     }


@router.get("/tasks/")
def list_tasks(
    task_service: TaskService = Depends(get_task_service),
) -> list[TaskRead]:
    """Возвращает список всех задач из базы данных."""
    return [TaskRead.model_validate(task) for task in task_service.list_tasks()]


@router.get("/tasks/{task_id}")
def get_task(
    task_id: uuid.UUID,
    task_service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """Возвращает информацию о задаче: статус, время выполнения, результат."""
    try:
        return TaskRead.model_validate(task_service.get_task(task_id))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/task")
def create_task(
    body: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
) -> TaskRead:
    try:
        algorithm = AlgorithmAbstractFactory.get_algorithm(body.algorithm)
        params = algorithm.get_pydantic_model().model_validate(body.params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        task = task_service.create_task(
            algorithm=algorithm, input_file_id=body.input_file_id, params=params
        )

    except InvalidAlgorithmParamsError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return TaskRead.model_validate(task)
