import json
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from tabulate import tabulate


@dataclass()
class CharacterPropertyResults:
    Total: Dict[str, int] = field(default_factory=dict)
    Target: Dict[str, int] = field(default_factory=dict)

    def __iter__(self) -> Iterator[Tuple[str, Union[Dict[str, int], List[str]]]]:
        yield "Total", self.Total
        yield "Target", self.Target
        yield "Missed", self.Missed

    def __str__(self) -> str:
        return self.as_markdown()

    @property
    def Missed(self) -> List[str]:
        return [
            target
            for target, target_value in self.Target.items()
            if target in self.Total and self.Total[target] < target_value
        ]

    def as_markdown(self) -> str:
        """
        Creates a string with the GitHub-styled Markdown-table representation of the results.
        """
        table = {
            "Name": self.Total.keys(),
            "Total": self.Total.values(),
            "Target": [None] * len(self.Total),
            "Missed": [None] * len(self.Total),
        }
        for row_id, row_name in enumerate(self.Total):
            if row_name in self.Target:
                table["Target"][row_id] = self.Target[row_name]
                table["Missed"][row_id] = "YES" if row_name in self.Missed else "NO"
        return tabulate(table, headers="keys", tablefmt="github", missingval="-")


class SkillResults(CharacterPropertyResults):
    def __init__(
        self,
        rating_values: Dict[str, int] = None,
        total_values: Dict[str, int] = None,
        target_values: Dict[str, int] = None,
    ):
        super().__init__(
            total_values if total_values is not None else dict(),
            target_values if target_values is not None else dict(),
        )
        self.Rating: Dict[str, int] = (
            rating_values if rating_values is not None else dict()
        )

    def __iter__(self) -> Iterator[Tuple[str, Union[Dict[str, int], List[str]]]]:
        yield "Rating", self.Rating
        for d in super().__iter__():
            yield d

    def as_markdown(self) -> str:
        """
        Creates a string with the GitHub-styled Markdown-table representation of the results.
        """
        table = {
            "Name": self.Total.keys(),
            "Rating": self.Rating.values(),
            "Total": self.Total.values(),
            "Target": [None] * len(self.Total),
            "Missed": [None] * len(self.Total),
        }
        for row_id, row_name in enumerate(self.Total):
            if row_name in self.Target:
                table["Target"][row_id] = self.Target[row_name]
                table["Missed"][row_id] = "YES" if row_name in self.Missed else "NO"
        return tabulate(table, headers="keys", tablefmt="github", missingval="-")


@dataclass()
class XPCost:
    Attributes: int = 0
    Skills: int = 0

    @property
    def Total(self) -> int:
        return self.Attributes + self.Skills

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        yield "Attributes", self.Attributes
        yield "Skills", self.Skills
        yield "Total", self.Total

    def __str__(self) -> str:
        return self.as_markdown()

    def as_markdown(self) -> str:
        """
        Creates a string with the GitHub-styled Markdown-table representation of the results.
        """
        table = {"Name": [], "Cost": []}
        for row_name, row_data in self:
            table["Name"].append(row_name)
            table["Cost"].append(row_data)
        return tabulate(table, headers="keys", tablefmt="github")


@dataclass
class AttributeSkillOptimizerResults:
    Tier: Optional[int] = None
    Attributes: CharacterPropertyResults = CharacterPropertyResults()
    Skills: SkillResults = SkillResults()
    Traits: CharacterPropertyResults = CharacterPropertyResults()
    XPCost: XPCost = XPCost()

    def __iter__(self) -> Iterator[Tuple[str, Union[Optional[int], dict]]]:
        yield "Tier", self.Tier
        yield "Attributes", dict(self.Attributes)
        yield "Skills", dict(self.Skills)
        yield "Traits", dict(self.Traits)
        yield "XPCost", dict(self.XPCost)

    def __str__(self) -> str:
        return self.as_markdown()

    def as_markdown(self) -> str:
        """
        Creates a string with the GitHub-styled Markdown-table representation of the results.
        """
        as_string = ""
        for attr_name, _ in self:
            as_string += f"\n## {attr_name}\n\n{getattr(self, attr_name)}\n"
        return as_string

    def as_json(self, indent: Optional[int] = 2) -> str:
        """
        Creates a JSON string with the results.

        Parameters
        ----------
        indent
            The indent used for the JSON dump call (see json.dumps).

        Returns
        -------
        as_string
        """
        return json.dumps(dict(self), indent=indent)
