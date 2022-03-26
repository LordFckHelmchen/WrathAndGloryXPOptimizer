from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Any

from wrath_and_glory_xp_optimizer.character_properties.int_bounds import IntBounds


@dataclass(frozen=True)
class _RatingMixin:
    rating_bounds: ClassVar[IntBounds]

    @classmethod
    def is_valid_rating(cls, rating: Any) -> bool:
        return isinstance(rating, int) and rating in cls.rating_bounds