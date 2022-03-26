from __future__ import annotations

from enum import Enum


class _PropertyEnum(Enum):
    @classmethod
    def get_by_name(cls, name: str) -> _PropertyEnum:
        return next(
            (
                member
                for member in cls
                if member.name == name or member.value.full_name == name
            ),
            cls.INVALID,
        )

    @classmethod
    def get_valid_members(cls):
        return (
            cls._member_map_[name]
            for name in cls._member_names_
            if name != cls.INVALID.name
        )
