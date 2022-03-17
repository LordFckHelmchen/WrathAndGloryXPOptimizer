from dataclasses import dataclass


@dataclass(frozen=True)
class BaseProperty:
    full_name: str
