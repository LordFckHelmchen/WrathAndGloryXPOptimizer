from dataclasses import dataclass


@dataclass(frozen=True)
class _BaseProperty:
    full_name: str
