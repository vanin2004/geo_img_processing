from dataclasses import dataclass


@dataclass
class ConfigBase:
    """Базовый класс для конфигурации приложения."""

    pass


@dataclass
class ipConfig(ConfigBase):
    """Конфигурация для IP-адресов и портов."""

    host: str = ""
    port: int | None = None
