from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .base_property import BaseProperty
from .int_bounds import IntBounds, RatingMixin
from .property_enum import PropertyEnum


@dataclass(frozen=True)
class Attribute(BaseProperty, RatingMixin):
    rating_bounds: ClassVar[IntBounds] = IntBounds(1, 12)
    short_name: str


@dataclass(frozen=True)
class InvalidAttribute(Attribute):
    full_name: str = "INVALID"
    rating_bounds: ClassVar[IntBounds] = IntBounds(None, None)
    short_name: str = "N/A"


@dataclass(frozen=True)
class RelatedAttributeMixin:
    related_attribute: Attributes


class Attributes(PropertyEnum):
    # full or short names must be unique, to avoid Enum.unique() to remove duplicates.
    Strength = Attribute(full_name="Strength", short_name="S")
    Toughness = Attribute(full_name="Toughness", short_name="T")
    Agility = Attribute(full_name="Agility", short_name="A")
    Initiative = Attribute(full_name="Initiative", short_name="I")
    Willpower = Attribute(full_name="Willpower", short_name="Wil")
    Intellect = Attribute(full_name="Intellect", short_name="Int")
    Fellowship = Attribute(full_name="Fellowship", short_name="Fel")
    # noinspection PyArgumentList
    INVALID = InvalidAttribute()

    @classmethod
    def get_by_name(cls, name: str) -> Attributes:
        member = super().get_by_name(name)
        if member is cls.INVALID:
            member = next(
                (member for member in cls if member.value.short_name == name),
                cls.INVALID,
            )
        return member
