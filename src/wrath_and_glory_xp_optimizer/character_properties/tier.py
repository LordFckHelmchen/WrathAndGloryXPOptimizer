from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ._base_property import _BaseProperty
from ._rating_mixin import _RatingMixin
from .int_bounds import IntBounds


@dataclass(frozen=True)
class Tier(_BaseProperty, _RatingMixin):
    full_name: str = "Tier"
    rating_bounds: ClassVar[IntBounds] = IntBounds(1, 5)
