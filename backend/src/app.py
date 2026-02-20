from contextlib import asynccontextmanager

from fastapi import FastAPI

# from fastapi.openapi.utils import get_openapi
from src.config import fastapi_config, settings
from src.injectors import initialize_database
from src.routers.api import router
from src.routers.handlers import (
    global_exception_handler,
    resource_already_exists_handler,
    resource_not_found_handler,
)

# from src.services import AlgorithmAbstractFactory
from src.services import FileAlreadyExistsError, TaskNotFoundError
from src.services import FileNotFoundError as StorageFileNotFoundError

# def _patch_openapi(app: FastAPI) -> None:
#     """Переопределяет генератор OpenAPI-схемы, добавляя в components/schemas
#     Pydantic-модели параметров всех зарегистрированных алгоритмов.
#     Вызывается один раз после создания приложения; схема кэшируется лениво
#     при первом запросе к /openapi.json.
#     """

#     def custom_openapi() -> dict:
#         if app.openapi_schema:
#             return app.openapi_schema

#         schema = get_openapi(
#             title=app.title,
#             version=app.version,
#             description=app.description or "",
#             routes=app.routes,
#         )

#         components_schemas: dict = schema.setdefault("components", {}).setdefault(
#             "schemas", {}
#         )

#         for algo_cls in AlgorithmAbstractFactory.registry.values():
#             model = algo_cls.get_pydantic_model()
#             algo_schema = model.model_json_schema()
#             # Вложенные $defs поднимаем в верхний уровень components/schemas
#             for ref_name, ref_schema in algo_schema.pop("$defs", {}).items():
#                 components_schemas.setdefault(ref_name, ref_schema)
#             components_schemas[model.__name__] = algo_schema

#         # Проставляем enum допустимых алгоритмов в схему TaskCreate
#         algorithm_names = list(AlgorithmAbstractFactory.registry.keys())
#         task_create = components_schemas.get("TaskCreate", {})
#         algorithm_prop = task_create.get("properties", {}).get("algorithm", {})
#         algorithm_prop["enum"] = algorithm_names
#         algorithm_prop["description"] = "Название алгоритма обработки: " + ", ".join(
#             algorithm_names
#         )

#         app.openapi_schema = schema
#         return schema

#     app.openapi = custom_openapi  # type: ignore[method-assign]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация БД при старте; освобождение ресурсов при остановке."""
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# --- exception handlers ---
app.add_exception_handler(TaskNotFoundError, resource_not_found_handler)
app.add_exception_handler(StorageFileNotFoundError, resource_not_found_handler)
app.add_exception_handler(FileAlreadyExistsError, resource_already_exists_handler)
app.add_exception_handler(Exception, global_exception_handler)

# --- routers ---
app.include_router(router)

# --- patch openapi schema with algorithm param models ---
# _patch_openapi(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app:app",
        host=fastapi_config.host,
        port=fastapi_config.port if fastapi_config.port else 8000,
        log_level=fastapi_config.log_level,
        reload=fastapi_config.reload,
    )
