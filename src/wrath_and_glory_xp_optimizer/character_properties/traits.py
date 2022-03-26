from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._base_property import _BaseProperty
from ._property_enum import _PropertyEnum
from .attributes import Attributes
from .attributes import RelatedAttributeMixin
from .int_bounds import IntBounds


@dataclass(frozen=True)
class Trait(_BaseProperty, RelatedAttributeMixin):
    attribute_offset: int
    tier_modifier: int

    def get_rating_bounds(self, related_tier: int) -> IntBounds:
        return (
            self.related_attribute.value.rating_bounds
            + self.get_total_attribute_offset(related_tier)
        )

    def get_total_attribute_offset(self, related_tier: int) -> int:
        return self.attribute_offset + self.tier_modifier * related_tier

    def is_valid_rating(self, rating: Any, related_tier: int) -> bool:
        return isinstance(rating, int) and rating in self.get_rating_bounds(
            related_tier
        )


@dataclass(frozen=True)
class InvalidTrait(Trait):
    full_name: str = "INVALID"
    related_attribute: Attributes = Attributes.INVALID
    attribute_offset: int = 0
    tier_modifier: int = 0


class Traits(_PropertyEnum):
    # full names must be unique, to avoid Enum.unique() to remove duplicates.
    Conviction = Trait(
        full_name="Conviction",
        related_attribute=Attributes.Willpower,
        attribute_offset=0,
        tier_modifier=0,
    )
    Defence = Trait(
        full_name="Defence",
        related_attribute=Attributes.Initiative,
        attribute_offset=-1,
        tier_modifier=0,
    )
    Determination = Trait(
        full_name="Determination",
        related_attribute=Attributes.Toughness,
        attribute_offset=0,
        tier_modifier=0,
    )
    Influence = Trait(
        full_name="Influence",
        related_attribute=Attributes.Fellowship,
        attribute_offset=-1,
        tier_modifier=0,
    )
    MaxShock = Trait(
        full_name="Max Shock",
        related_attribute=Attributes.Willpower,
        attribute_offset=0,
        tier_modifier=1,
    )
    MaxWounds = Trait(
        full_name="Max Wounds",
        related_attribute=Attributes.Toughness,
        attribute_offset=0,
        tier_modifier=2,
    )
    Resilience = Trait(
        full_name="Resilience",
        related_attribute=Attributes.Toughness,
        attribute_offset=1,
        tier_modifier=0,
    )
    Resolve = Trait(
        full_name="Resolve",
        related_attribute=Attributes.Willpower,
        attribute_offset=-1,
        tier_modifier=0,
    )
    # noinspection PyArgumentList
    INVALID = InvalidTrait()
