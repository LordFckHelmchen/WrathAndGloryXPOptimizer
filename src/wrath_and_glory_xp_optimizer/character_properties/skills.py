from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import ClassVar

from ._base_property import _BaseProperty
from ._property_enum import _PropertyEnum
from ._rating_mixin import _RatingMixin
from .attributes import Attributes
from .attributes import RelatedAttributeMixin
from .int_bounds import IntBounds


@dataclass(frozen=True)
class Skill(_BaseProperty, _RatingMixin, RelatedAttributeMixin):
    rating_bounds: ClassVar[IntBounds] = IntBounds(0, 8)

    @property
    def total_rating_bounds(self) -> IntBounds:
        return (  # type: ignore  # Doesn't return 'Any'
            self.rating_bounds + self.related_attribute.value.rating_bounds
        )

    def is_valid_total_rating(self, rating: Any) -> bool:
        return isinstance(rating, int) and rating in self.total_rating_bounds


@dataclass(frozen=True)
class InvalidSkill(Skill):
    full_name: str = "INVALID"
    rating_bounds: ClassVar[IntBounds] = IntBounds(None, None)
    related_attribute: Attributes = Attributes.INVALID

    @property
    def total_rating_bounds(self) -> IntBounds:
        return self.rating_bounds


class Skills(_PropertyEnum):
    # full names must be unique, to avoid Enum.unique() to remove duplicates.
    Athletics = Skill(full_name="Athletics", related_attribute=Attributes.Strength)
    Awareness = Skill(full_name="Awareness", related_attribute=Attributes.Intellect)
    BallisticSkill = Skill(
        full_name="Ballistic Skill", related_attribute=Attributes.Agility
    )
    Cunning = Skill(full_name="Cunning", related_attribute=Attributes.Fellowship)
    Deception = Skill(full_name="Deception", related_attribute=Attributes.Fellowship)
    Insight = Skill(full_name="Insight", related_attribute=Attributes.Fellowship)
    Intimidation = Skill(
        full_name="Intimidation", related_attribute=Attributes.Willpower
    )
    Investigation = Skill(
        full_name="Investigation", related_attribute=Attributes.Intellect
    )
    Leadership = Skill(full_name="Leadership", related_attribute=Attributes.Willpower)
    Medicae = Skill(full_name="Medicae", related_attribute=Attributes.Intellect)
    Persuasion = Skill(full_name="Persuasion", related_attribute=Attributes.Fellowship)
    Pilot = Skill(full_name="Pilot", related_attribute=Attributes.Agility)
    PsychicMastery = Skill(
        full_name="Psychic Mastery", related_attribute=Attributes.Willpower
    )
    Scholar = Skill(full_name="Scholar", related_attribute=Attributes.Intellect)
    Stealth = Skill(full_name="Stealth", related_attribute=Attributes.Agility)
    Survival = Skill(full_name="Survival", related_attribute=Attributes.Willpower)
    Tech = Skill(full_name="Tech", related_attribute=Attributes.Intellect)
    WeaponSkill = Skill(
        full_name="Weapon Skill", related_attribute=Attributes.Initiative
    )
    # noinspection PyArgumentList
    INVALID = InvalidSkill()
