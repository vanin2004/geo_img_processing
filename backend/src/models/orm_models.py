import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Integer, String
from sqlalchemy import func as sa_func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .declarative_base import Base


class TaskStateEnum(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    ERROR = "ERROR"


class ErrorCodeEnum(enum.Enum):
    UNKNOWN_ERROR = 500
    ALGORITHM_EXECUTION_FAILED = 501
    FILE_CREATION_FAILED = 502
    INVALID_INPUT_PARAMS = 401
    INPUT_FILE_NOT_FOUND = 402
    OUTPUT_FILE_ALREADY_EXISTS = 403


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    algorithm: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[TaskStateEnum] = mapped_column(
        Enum(TaskStateEnum), nullable=False, default=TaskStateEnum.PENDING
    )

    input_file_id: Mapped[str] = mapped_column(String, nullable=False)
    params: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    output_file_id: Mapped[str | None] = mapped_column(String, nullable=True)
    output_file_full_path: Mapped[str | None] = mapped_column(String, nullable=True)

    datetime_create: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa_func.now(), nullable=False
    )
    datetime_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    datetime_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    error: Mapped[str | None] = mapped_column(String, nullable=True)
    error_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
