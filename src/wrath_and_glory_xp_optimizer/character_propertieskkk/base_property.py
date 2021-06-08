from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class BaseProperty:
    full_name: str


@dataclass(frozen=True)
class RatingMixin:
    rating_bounds: ClassVar[IntBounds]

    @classmethod
    def is_valid_rating(cls, rating: Any) -> bool:
        return isinstance(rating, int) and rating in cls.rating_bounds


@dataclass(frozen=True)
class RelatedAttributeMixin:
    related_attribute: Attributes
