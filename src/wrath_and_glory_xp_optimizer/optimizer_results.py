import json
from typing import Dict, List, Optional


class CharacterPropertyResults:
    def __init__(self,
                 total_values: Dict[str, int] = None,
                 target_values: Dict[str, int] = None):
        self.Total: Dict[str, int] = total_values if total_values is not None else dict()
        self.Target: Dict[str, int] = target_values if target_values is not None else dict()

    def __iter__(self) -> dict:
        yield 'Total', self.Total
        yield 'Target', self.Target
        yield 'Missed', self.Missed

    def __str__(self):
        """
        Creates a markdown-table string representation of the object.
        """
        name_width = max(len('Name'), max(len(name) for name in self.Total))
        max_value_header_width = max(len(header_name) for header_name, _ in self)
        value_width = max(max_value_header_width, max(len(str(value)) for value in self.Total.values()))

        name_format = "{0:" + str(name_width) + "}"
        value_format = "{0:<" + str(value_width) + "}"

        # Table header
        as_string = name_format.format('Name')
        for column_name, _ in self:
            as_string += ' | ' + value_format.format(column_name)

        # Header separator
        as_string += '\n' + '-' * name_width
        for _, _ in self:
            as_string += ' | ' + '-' * value_width

        # Table rows
        for row_name in self.Total:
            as_string += '\n' + name_format.format(row_name)
            for column_name, column_data in self:
                as_string += ' | '
                row_data = '-'
                if column_name == 'Missed':
                    if row_name in self.Missed:
                        row_data = 'YES'
                    elif row_name in self.Target:
                        row_data = 'NO'
                elif row_name in column_data:
                    row_data = column_data[row_name]
                as_string += value_format.format(row_data)

        return as_string

    def __repr__(self):
        return str(dict(self))

    @property
    def Missed(self) -> List[str]:
        return [target for target, target_value in self.Target.items() if
                target in self.Total and self.Total[target] < target_value]


class SkillResults(CharacterPropertyResults):
    def __init__(self,
                 rating_values: Dict[str, int] = None,
                 total_values: Dict[str, int] = None,
                 target_values: Dict[str, int] = None):
        super().__init__(total_values, target_values)
        self.Rating: Dict[str, int] = rating_values if rating_values is not None else dict()

    def __iter__(self) -> dict:
        yield 'Rating', self.Rating
        for d in super().__iter__():
            yield d


class XPCost:
    def __init__(self,
                 attribute_costs: int = 0,
                 skill_costs: int = 0,
                 total_costs: Optional[int] = None):
        self.Attributes: int = attribute_costs
        self.Skills: int = skill_costs
        if total_costs is not None and self.Attributes + self.Skills != total_costs:
            raise IOError(f"Total XP cost didn't sum up from Attribute & Skill costs: {self.Attributes} != "
                          f"{self.Skills} + {total_costs}")

    def __eq__(self, other):
        return self.Attributes == other.Attributes and self.Skills == other.Skills

    @property
    def Total(self):
        return self.Attributes + self.Skills

    def __iter__(self) -> dict:
        yield 'Attributes', self.Attributes
        yield 'Skills', self.Skills
        yield 'Total', self.Total

    def __str__(self):
        """
        Creates a markdown-table string representation of the object.
        """
        name_width = max(len('Name'), max(len(name) for name, _ in self))
        value_width = max(len('Cost'), max(len(str(value)) for _, value in self))

        def format_row(name: str, data, prefix: str = '\n') -> str:
            return prefix + ("{0:" + str(name_width) + "}").format(name) + ' | ' + (
                    "{0:<" + str(value_width) + "}").format(data)

        # Table header + separator
        as_string = format_row('Name', 'Cost', prefix='')

        # Header separator
        as_string += format_row('-' * name_width, '-' * value_width)

        # Table rows
        for row_name, row_data in self:
            as_string += format_row(row_name, row_data)

        return as_string

    def __repr__(self):
        return str(dict(self))


class AttributeSkillOptimizerResults:
    def __init__(self,
                 tier: int = None,
                 attributes: CharacterPropertyResults = CharacterPropertyResults(),
                 skills: SkillResults = SkillResults(),
                 traits: CharacterPropertyResults = CharacterPropertyResults(),
                 xp_cost: XPCost = XPCost()
                 ):
        self.Tier: Optional[int] = tier
        self.Attributes: CharacterPropertyResults = attributes
        self.Skills: SkillResults = skills
        self.Traits: CharacterPropertyResults = traits
        self.XPCost: XPCost = xp_cost

    def __iter__(self) -> dict:
        yield 'Tier', self.Tier
        yield 'Attributes', dict(self.Attributes)
        yield 'Skills', dict(self.Skills)
        yield 'Traits', dict(self.Traits)
        yield 'XPCost', dict(self.XPCost)

    def __str__(self):
        """
        Creates a Markdown-table representation of the object.
        """
        as_string = ""
        for attr_name, _ in self:
            as_string += f"\n## {attr_name}\n{getattr(self, attr_name)}\n"
        return as_string

    def as_markdown(self) -> str:
        """
        Creates a string with the Markdown-table representation of the results.
        Returns
        -------
        result_str
        """
        return str(self)

    def as_json(self, indent: Optional[int] = 2) -> str:
        """
        Creates a JSON string with the results.

        Parameters
        ----------
        indent
            The indent used for the JSON dump call (see json.dumps).

        Returns
        -------
        result_str
        """
        return json.dumps(dict(self), indent=indent)
