import json
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union


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
        Creates a string with the Markdown-table representation of the results.
        Returns
        -------
        as_string
        """
        name_width = max(len("Name"), max(len(name) for name in self.Total))
        max_value_header_width = max(len(header_name) for header_name, _ in self)
        value_width = max(
            max_value_header_width,
            max(len(str(value)) for value in self.Total.values()),
        )

        value_widths = {column_name: max(len(column_name), max(len(str(value)) for value in column_data.values())) for column_name, column_data in self}
        name_format = "{0:" + str(name_width) + "}"
        value_format = "{0:<" + str(value_width) + "}"

        # Table header
        as_string = f"| {name_format.format('Name')} |"
        for column_name, _ in self:
            as_string += f" {value_format.format(column_name)} |"

        # Header separator
        as_string += "\n| " + "-" * name_width + " |"
        for _, _ in self:
            as_string += f" {'-' * value_width}  |"

        # Table rows
        for row_name in self.Total:
            as_string += f"\n| {name_format.format(row_name)} |"
            for column_name, column_data in self:
                row_data = "-"
                if column_name == "Missed":
                    if row_name in self.Missed:
                        row_data = "YES"
                    elif row_name in self.Target:
                        row_data = "NO"
                elif row_name in column_data:
                    row_data = column_data[row_name]
                as_string += f" {value_format.format(row_data)} |"

        return as_string


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
        Creates a string with the Markdown-table representation of the results.
        Returns
        -------
        as_string
        """
        name_width = max(len("Name"), max(len(name) for name, _ in self))
        value_width = max(len("Cost"), max(len(str(value)) for _, value in self))

        def format_row(name: str, data: Union[str, int], prefix: str = "\n") -> str:
            return (
                prefix
                + ("{0:" + str(name_width) + "}").format(name)
                + " | "
                + ("{0:<" + str(value_width) + "}").format(data)
            )

        # Table header + separator
        as_string = format_row("Name", "Cost", prefix="")

        # Header separator
        as_string += format_row("-" * name_width, "-" * value_width)

        # Table rows
        for row_name, row_data in self:
            as_string += format_row(row_name, row_data)

        return as_string


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
        Creates a string with the Markdown-table representation of the results.
        Returns
        -------
        as_string
        """
        as_string = ""
        for attr_name, _ in self:
            as_string += f"\n## {attr_name}\n{getattr(self, attr_name)}\n"
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
