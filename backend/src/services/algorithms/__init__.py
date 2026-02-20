from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

from src.models.schemas import AlgorithmParamsBaseModel


class BaseAlgorithmError(Exception):
    """Базовый класс для ошибок алгоритмов обработки данных."""


class AlgorithmValidationError(BaseAlgorithmError):
    """Ошибка валидации параметров алгоритма."""


class AlgorithmExecutionError(BaseAlgorithmError):
    """Ошибка выполнения алгоритма."""


T = TypeVar("T", bound=AlgorithmParamsBaseModel)


class BaseAlgorithm(ABC, Generic[T]):
    """Базовый класс для алгоритмов обработки геопространственных данных."""

    _name = "BASE_ALGORITHM"

    @classmethod
    def name(cls) -> str:
        """Возвращает название алгоритма.

        Returns:
            str: Название алгоритма.
        """
        return cls._name

    @abstractmethod
    def run(self, input_file_bytes: bytes, file_ext: str, params: T) -> bytes:
        """Запускает алгоритм обработки данных.

        Args:
            input_file_bytes (bytes): Байтовое представление входного файла.
            file_ext (str): Расширение входного файла.
        Returns:
            bytes: Байтовое представление выходного файла.
        Raises:
            NotImplementedError: Если метод не был переопределен в дочернем классе.
        """
        raise NotImplementedError(
            "Метод run() должен быть реализован в дочернем классе."
        )

    @classmethod
    @abstractmethod
    def get_pydantic_model(cls) -> type[T]:
        """Возвращает Pydantic-модель для валидации параметров алгоритма.

        Returns:
            BaseModel: Pydantic-модель параметров алгоритма.
        Raises:
            NotImplementedError: Если метод не был переопределен в дочернем классе.
        """
        raise NotImplementedError(
            "Метод get_pydantic_model() должен быть реализован в дочернем классе."
        )


class AlgorithmAbstractFactory:
    registry: dict[
        str,
        type[BaseAlgorithm],
    ] = {}

    @classmethod
    def get_algorithm(cls, name: str) -> BaseAlgorithm:
        """Возвращает экземпляр алгоритма по его названию.

        Args:
            name (str): Название алгоритма.
            params (dict): Параметры алгоритма.

        Returns:
            BaseAlgorithm: Экземпляр алгоритма.

        Raises:
            ValueError: Если алгоритм с таким названием не зарегистрирован.
        """
        name = name.upper()
        if name not in cls.registry:
            raise ValueError(f"Алгоритм с именем '{name}' не найден.")
        try:
            algorithm = cls.registry[name]()
        except Exception:
            raise ValueError(f"Ошибка при создании экземпляра алгоритма '{name}'.")

        return algorithm

    @classmethod
    def list_algorithms(cls) -> list[type[BaseAlgorithm]]:
        """Возвращает список названий всех зарегистрированных алгоритмов.

        Returns:
            list[type[BaseAlgorithm]]: Список классов алгоритмов.
        """
        return list(cls.registry.values())

    @classmethod
    def register_algorithm(
        cls,
        algorithm_name: str,
    ) -> Callable[[type[BaseAlgorithm]], type[BaseAlgorithm]]:
        """Декоратор для регистрации алгоритмов в системе."""
        algorithm_name = algorithm_name.upper()

        def decorator(algorithm_cls: type[BaseAlgorithm]) -> type[BaseAlgorithm]:
            if not issubclass(algorithm_cls, BaseAlgorithm):
                raise ValueError("Класс должен наследоваться от BaseAlgorithm")
            if algorithm_name in AlgorithmAbstractFactory.registry:
                raise ValueError(
                    f"Алгоритм с именем '{algorithm_name}' уже зарегистрирован."
                )
            algorithm_cls._name = algorithm_name
            AlgorithmAbstractFactory.registry[algorithm_name] = algorithm_cls

            return algorithm_cls

        return decorator


from .raster_rescale import RasterRescaleAlgorithm  # type: ignore  # noqa: E402, F401
from .raster_transform import RasterTransformAlgorithm  # noqa: E402, F401
from .vector_transform import (  # type: ignore # noqa: E402, F401
    VectorTransformAlgorithm,  # noqa: E402, F401
)
