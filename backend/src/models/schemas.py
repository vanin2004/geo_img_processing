from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskRead(BaseModel):
    """Pydantic-модель задачи для ответов API"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    algorithm: str
    state: str
    input_file_id: str
    params: dict | None = None
    output_file_id: str | None = None
    output_file_full_path: str | None = None
    datetime_create: datetime
    datetime_start: datetime | None = None
    datetime_end: datetime | None = None
    error: str | None = None
    error_code: int | None = None


class TaskCreate(BaseModel):
    """Pydantic-модель задачи для создания новой задачи через API"""

    algorithm: str = Field(..., description="Название алгоритма")
    input_file_id: str = Field(..., description="ID входного файла")
    params: dict | None = Field(
        default=None, description="Параметры алгоритма (необязательно)"
    )


class AlgorithmParamsBaseModel(BaseModel):
    """Базовая Pydantic-модель для параметров алгоритмов обработки геопространственных данных."""
