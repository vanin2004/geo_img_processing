from dataclasses import dataclass

from .config_base import ipConfig


@dataclass
class FastAPIConfig(ipConfig):
    log_level: str = "info"
    reload: bool = False
