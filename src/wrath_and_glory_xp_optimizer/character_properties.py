from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar, Union


@dataclass
class IntBounds:
    min: int
    max: int

    def __post_init__(self):
        if self.min > self.max:
            self.min, self.max = self.max, self.min

    def __add__(self, other: Union[int, IntBounds]):
        if isinstance(other, int):
            other = IntBounds(other, other)

        return IntBounds(min=self.min + other.min, max=self.max + other.max)

    def __contains__(self, item: int) -> bool:
        return self.min <= item <= self.max

    def __iter__(self):
        yield self.min
        yield self.max

    def __str__(self):
        return self.__repr__().replace(IntBounds.__name__, "Integer ")

    def as_range(self) -> range:
        return range(self.min, self.max + 1)


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


@dataclass(frozen=True)
class Tier(BaseProperty, RatingMixin):
    full_name: str = "Tier"
    rating_bounds: ClassVar[IntBounds] = IntBounds(1, 5)


class PropertyEnum(Enum):
    @classmethod
    def get_by_name(cls, name: str) -> PropertyEnum:
        return next((member for member in cls if member.name == name or member.value.full_name == name),
                    cls.INVALID)

    @classmethod
    def get_valid_members(cls):
        return (cls._member_map_[name] for name in cls._member_names_ if name != cls.INVALID.name)


@dataclass(frozen=True)
class Attribute(BaseProperty, RatingMixin):
    rating_bounds: ClassVar[IntBounds] = IntBounds(1, 12)
    short_name: str


@dataclass(frozen=True)
class InvalidAttribute(Attribute):
    full_name: str = "INVALID"
    rating_bounds: ClassVar[IntBounds] = IntBounds(*[Attribute.rating_bounds.min - 1] * 2)
    short_name: str = "N/A"

    def is_valid_rating(self, rating: Any) -> bool:
        return False


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
            member = next((member for member in cls if member.value.short_name == name), cls.INVALID)
        return member


@dataclass(frozen=True)
class Skill(BaseProperty, RatingMixin, RelatedAttributeMixin):
    rating_bounds: ClassVar[IntBounds] = IntBounds(0, 8)

    @property
    def total_rating_bounds(self) -> IntBounds:
        return self.rating_bounds + Attribute.rating_bounds

    def is_valid_total_rating(self, rating: Any) -> bool:
        return isinstance(rating, int) and rating in self.total_rating_bounds


@dataclass(frozen=True)
class InvalidSkill(Skill):
    full_name: str = "INVALID"
    rating_bounds: ClassVar[IntBounds] = IntBounds(*[Skill.rating_bounds.min - 1] * 2)
    related_attribute: Attributes = Attributes.INVALID

    @property
    def total_rating_bounds(self) -> IntBounds:
        return self.rating_bounds

    def is_valid_rating(self, rating: Any) -> bool:
        return False

    def is_valid_total_rating(self, rating: Any) -> bool:
        return False


class Skills(PropertyEnum):
    # full names must be unique, to avoid Enum.unique() to remove duplicates.
    Athletics = Skill(full_name="Athletics", related_attribute=Attributes.Strength)
    Awareness = Skill(full_name="Awareness", related_attribute=Attributes.Intellect)
    BallisticSkill = Skill(full_name="Ballistic Skill", related_attribute=Attributes.Agility)
    Cunning = Skill(full_name="Cunning", related_attribute=Attributes.Fellowship)
    Deception = Skill(full_name="Deception", related_attribute=Attributes.Fellowship)
    Insight = Skill(full_name="Insight", related_attribute=Attributes.Fellowship)
    Intimidation = Skill(full_name="Intimidation", related_attribute=Attributes.Willpower)
    Investigation = Skill(full_name="Investigation", related_attribute=Attributes.Intellect)
    Leadership = Skill(full_name="Leadership", related_attribute=Attributes.Willpower)
    Medicae = Skill(full_name="Medicae", related_attribute=Attributes.Intellect)
    Persuasion = Skill(full_name="Persuasion", related_attribute=Attributes.Willpower)
    Pilot = Skill(full_name="Pilot", related_attribute=Attributes.Agility)
    PsychicMastery = Skill(full_name="Psychic Mastery", related_attribute=Attributes.Willpower)
    Scholar = Skill(full_name="Scholar", related_attribute=Attributes.Intellect)
    Stealth = Skill(full_name="Stealth", related_attribute=Attributes.Agility)
    Survival = Skill(full_name="Survival", related_attribute=Attributes.Willpower)
    Tech = Skill(full_name="Tech", related_attribute=Attributes.Intellect)
    WeaponSkill = Skill(full_name="Weapon Skill", related_attribute=Attributes.Initiative)
    # noinspection PyArgumentList
    INVALID = InvalidSkill()


@dataclass(frozen=True)
class Trait(BaseProperty, RelatedAttributeMixin):
    attribute_offset: int
    tier_modifier: int

    def get_rating_bounds(self, related_tier: int) -> IntBounds:
        return Attribute.rating_bounds + self.get_total_attribute_offset(related_tier)

    def get_total_attribute_offset(self, related_tier: int) -> int:
        return self.attribute_offset + self.tier_modifier * related_tier

    def is_valid_rating(self, rating: Any, related_tier: int) -> bool:
        return isinstance(rating, int) and rating in self.get_rating_bounds(related_tier)


@dataclass(frozen=True)
class InvalidTrait(Trait):
    full_name: str = "INVALID"
    related_attribute: Attributes = Attributes.INVALID
    attribute_offset: int = 0
    tier_modifier: int = 0

    def is_valid_rating(self, rating: Any, related_tier: int) -> bool:
        return False


class Traits(PropertyEnum):
    # full names must be unique, to avoid Enum.unique() to remove duplicates.
    Conviction = Trait(full_name="Conviction",
                       related_attribute=Attributes.Willpower,
                       attribute_offset=0,
                       tier_modifier=0)
    Defence = Trait(full_name="Defence",
                    related_attribute=Attributes.Initiative,
                    attribute_offset=-1,
                    tier_modifier=0)
    Determination = Trait(full_name="Determination",
                          related_attribute=Attributes.Toughness,
                          attribute_offset=0,
                          tier_modifier=0)
    Influence = Trait(full_name="Influence",
                      related_attribute=Attributes.Fellowship,
                      attribute_offset=-1,
                      tier_modifier=0)
    MaxShock = Trait(full_name="Max Shock",
                     related_attribute=Attributes.Willpower,
                     attribute_offset=0,
                     tier_modifier=1)
    MaxWounds = Trait(full_name="Max Wounds",
                      related_attribute=Attributes.Toughness,
                      attribute_offset=0,
                      tier_modifier=2)
    Resilience = Trait(full_name="Resilience",
                       related_attribute=Attributes.Toughness,
                       attribute_offset=1,
                       tier_modifier=0)
    Resolve = Trait(full_name="Resolve",
                    related_attribute=Attributes.Willpower,
                    attribute_offset=-1,
                    tier_modifier=0)
    # noinspection PyArgumentList
    INVALID = InvalidTrait()
