from abc import ABC, abstractmethod
from typing import Callable

from src.models.schemas import AlgorithmParamsBaseModel


class BaseAlgorithmException(Exception):
    """Базовый класс для ошибок алгоритмов обработки данных."""


class AlgorithmValidationError(BaseAlgorithmException):
    """Ошибка валидации параметров алгоритма."""


class AlgorithmExecutionError(BaseAlgorithmException):
    """Ошибка выполнения алгоритма."""


class BaseAlgorithm(ABC):
    """Базовый класс для алгоритмов обработки геопространственных данных."""

    _name = "BASE_ALGORITHM"

    @classmethod
    def name(cls) -> str:
        """Возвращает название алгоритма.

        Returns:
            str: Название алгоритма.
        """
        return cls._name

    def __init__(self, params: dict):
        """Инициализирует алгоритм с заданными параметрами."""

        try:
            self._params = self.get_pydantic_model().model_validate(params)
        except Exception as e:
            raise AlgorithmValidationError(f"Invalid parameters for {self.name()}: {e}")

    @abstractmethod
    def run(self, input_file_bytes: bytes, file_ext: str) -> bytes:
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
    def get_pydantic_model(cls) -> type[AlgorithmParamsBaseModel]:
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
    def get_algorithm(cls, name: str, params: dict) -> BaseAlgorithm:
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
            algorithm = cls.registry[name](params=params)
        except Exception:
            raise ValueError(f"Ошибка при создании экземпляра алгоритма '{name}'.")

        return algorithm

    @classmethod
    def list_algorithms(cls) -> list[str]:
        """Возвращает список названий всех зарегистрированных алгоритмов.

        Returns:
            list[str]: Список названий алгоритмов.
        """
        return list(cls.registry.keys())

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


from .raster_transform import RasterTransformAlgorithm  # noqa: E402, F401
from .vector_transform import (  # type: ignore # noqa: E402, F401
    VectorTransformAlgorithm,  # noqa: E402, F401
)
