from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .base_property import BaseProperty
from .int_bounds import IntBounds, RatingMixin


@dataclass(frozen=True)
class Tier(BaseProperty, RatingMixin):
    full_name: str = "Tier"
    rating_bounds: ClassVar[IntBounds] = IntBounds(1, 5)
