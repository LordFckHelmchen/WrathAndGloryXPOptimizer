from __future__ import annotations

from enum import Enum
from typing import Any
from typing import Generator


class _PropertyEnum(Enum):
    @classmethod
    def get_by_name(cls, name: str) -> _PropertyEnum:
        return next(
            (
                member
                for member in cls
                if member.name == name or member.value.full_name == name
            ),
            cls.INVALID,  # type: ignore  # Mixin class not to be instantiated
        )

    @classmethod
    def get_valid_members(cls) -> Generator[Any, None, None]:
        return (
            cls._member_map_[name]
            for name in cls._member_names_
            if name != cls.INVALID.name  # type: ignore  # Base instead of child
        )
