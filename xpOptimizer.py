__version__ = 1.3

import argparse
import json
import os
from collections import namedtuple, OrderedDict
from enum import Enum
from typing import Optional, Dict, Union, Iterable, List, Tuple

import numpy as np
from gekko import GEKKO

ValueProperty = namedtuple('PropertyValue', ['attribute', 'offset'])


class StringEnum(Enum):
    @classmethod
    def is_value(cls, value: str):
        return any(value == member.value for member in cls)

    @classmethod
    def is_name(cls, name: str):
        return any(name == member.name for member in cls)

    @classmethod
    def from_name_or_value(cls, name_or_value: str):
        if cls.is_value(name_or_value):
            # noinspection PyArgumentList
            return cls(name_or_value)
        if cls.is_name(name_or_value):
            return getattr(cls, name_or_value)
        else:
            return None


class Attribute(StringEnum):
    Strength = 'S'
    Toughness = 'T'
    Agility = 'A'
    Initiative = 'I'
    Willpower = 'Wil'
    Intellect = 'Int'
    Fellowship = 'Fel'


class Skill(StringEnum):
    Athletics = 'Athletics'
    Awareness = 'Awareness'
    BallisticSkill = 'BallisticSkill'
    Cunning = 'Cunning'
    Deception = 'Deception'
    Insight = 'Insight'
    Intimidation = 'Intimidation'
    Investigation = 'Investigation'
    Leadership = 'Leadership'
    Medicae = 'Medicae'
    Persuasion = 'Persuasion'
    Pilot = 'Pilot'
    PsychicMastery = 'PsychicMastery'
    Scholar = 'Scholar'
    Stealth = 'Stealth'
    Survival = 'Survival'
    Tech = 'Tech'
    WeaponSkill = 'WeaponSkill'


class DerivedProperty(StringEnum):
    Defence = 'Defence'
    Resilience = 'Resilience'
    Determination = 'Determination'
    MaxWounds = 'MaxWounds'
    MaxShock = 'MaxShock'
    Conviction = 'Conviction'
    Resolve = 'Resolve'
    Influence = 'Influence'


PropertyEnum = Union[Attribute, Skill, DerivedProperty]


class PropertyResults:
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


class SkillResults(PropertyResults):
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
                 attributes: PropertyResults = PropertyResults(),
                 skills: SkillResults = SkillResults(),
                 derived_properties: PropertyResults = PropertyResults(),
                 xp_cost: XPCost = XPCost()
                 ):
        self.Tier: Optional[int] = tier
        self.Attributes: PropertyResults = attributes
        self.Skills: SkillResults = skills
        self.DerivedProperties: PropertyResults = derived_properties
        self.XPCost: XPCost = xp_cost

    def __iter__(self) -> dict:
        yield 'Tier', self.Tier
        yield 'Attributes', dict(self.Attributes)
        yield 'Skills', dict(self.Skills)
        yield 'DerivedProperties', dict(self.DerivedProperties)
        yield 'XPCost', dict(self.XPCost)

    def __str__(self):
        """
        Creates a markdown string-representation of the object.
        """
        as_string = ""
        for attr_name, _ in self:
            as_string += f"\n## {attr_name}\n{getattr(self, attr_name)}\n"
        return as_string


class GekkoContext:
    def __init__(self, *args, **kwargs):
        self.solver = GEKKO(*args, **kwargs)

    def __enter__(self):
        return self.solver

    def __exit__(self, exec_type, exec_value, exec_traceback):
        self.solver.cleanup()


class AttributeSkillOptimizer:
    WRATH_AND_GLORY_CORE_RULES_VERSION = 2.1

    DEFAULT_SOLVER_OPTIONS = ('minlp_maximum_iterations 500',
                              'minlp_max_iter_with_int_sol 50',  # minlp iterations with integer solution
                              'minlp_as_nlp 0',  # treat minlp as nlp
                              'nlp_maximum_iterations 50',  # nlp sub-problem max iterations
                              'minlp_branch_method 1',  # 1 = depth first, 2 = breadth first
                              'minlp_integer_tol 0.05',  # maximum deviation from whole number
                              'minlp_gap_tol 0.01')  # convergence tolerance

    TIER_RANGE = {'lb': 1, 'ub': 5}
    ATTRIBUTE_RANGE = {'lb': 1, 'ub': 12}
    SKILL_RANGE = {'lb': 0, 'ub': 8}

    def __init__(self,
                 tier: int = 1,
                 is_verbose: bool = False,
                 solver_options: Tuple[str] = DEFAULT_SOLVER_OPTIONS):
        if tier < AttributeSkillOptimizer.TIER_RANGE['lb'] or tier > AttributeSkillOptimizer.TIER_RANGE['ub']:
            raise IOError(
                f"'tier' must be an integer within {list(AttributeSkillOptimizer.TIER_RANGE.values())}, was {tier}")
        self.tier: int = tier
        self.skills = OrderedDict({Skill.Athletics: ValueProperty(Attribute.Strength, 0),
                                   Skill.Awareness: ValueProperty(Attribute.Intellect, 0),
                                   Skill.BallisticSkill: ValueProperty(Attribute.Agility, 0),
                                   Skill.Cunning: ValueProperty(Attribute.Fellowship, 0),
                                   Skill.Deception: ValueProperty(Attribute.Fellowship, 0),
                                   Skill.Insight: ValueProperty(Attribute.Fellowship, 0),
                                   Skill.Intimidation: ValueProperty(Attribute.Willpower, 0),
                                   Skill.Investigation: ValueProperty(Attribute.Intellect, 0),
                                   Skill.Leadership: ValueProperty(Attribute.Willpower, 0),
                                   Skill.Medicae: ValueProperty(Attribute.Intellect, 0),
                                   Skill.Persuasion: ValueProperty(Attribute.Fellowship, 0),
                                   Skill.Pilot: ValueProperty(Attribute.Agility, 0),
                                   Skill.PsychicMastery: ValueProperty(Attribute.Willpower, 0),
                                   Skill.Scholar: ValueProperty(Attribute.Intellect, 0),
                                   Skill.Stealth: ValueProperty(Attribute.Agility, 0),
                                   Skill.Survival: ValueProperty(Attribute.Willpower, 0),
                                   Skill.Tech: ValueProperty(Attribute.Intellect, 0),
                                   Skill.WeaponSkill: ValueProperty(Attribute.Initiative, 0)})
        self.derived_properties = OrderedDict({DerivedProperty.Conviction: ValueProperty(Attribute.Willpower, 0),
                                               DerivedProperty.Defence: ValueProperty(Attribute.Initiative, -1),
                                               DerivedProperty.Determination: ValueProperty(Attribute.Toughness, 0),
                                               DerivedProperty.Influence: ValueProperty(Attribute.Fellowship, -1),
                                               DerivedProperty.MaxShock: ValueProperty(Attribute.Willpower, tier),
                                               DerivedProperty.MaxWounds: ValueProperty(Attribute.Toughness, 2 * tier),
                                               DerivedProperty.Resilience: ValueProperty(Attribute.Toughness, 1),
                                               DerivedProperty.Resolve: ValueProperty(Attribute.Willpower, -1)})

        self.solver_id = 1  # Use APOPT to find the optimal Integer solution, since this is a MINLP.
        self.solver_options = solver_options
        self.is_verbose: bool = is_verbose

    @staticmethod
    def name_to_enum(name: str) -> Optional[StringEnum]:
        for enum_class in [Attribute, Skill, DerivedProperty]:
            name_as_enum = enum_class.from_name_or_value(name)
            if name_as_enum is not None:
                return name_as_enum
        raise KeyError(f"Invalid value name: {name}")

    def optimize_selection(self, target_values: Dict[str, int]) -> AttributeSkillOptimizerResults:
        """
        Note
        ----
        This was done with the help of John Hedengren from Gekko (see https://stackoverflow.com/questions/65863807)
        """
        target_values = {AttributeSkillOptimizer.name_to_enum(key): value for key, value in target_values.items()}

        with GekkoContext(remote=False) as solver:
            # Define variables with optimized initial values.
            attribute_ratings = [solver.Var(name=attribute.name,
                                            value=target_values.get(attribute,
                                                                    AttributeSkillOptimizer.ATTRIBUTE_RANGE['lb']),
                                            lb=AttributeSkillOptimizer.ATTRIBUTE_RANGE['lb'],
                                            ub=AttributeSkillOptimizer.ATTRIBUTE_RANGE['ub'],
                                            integer=True) for attribute in Attribute]
            skill_ratings = [solver.Var(name=skill.name,
                                        value=AttributeSkillOptimizer.SKILL_RANGE['lb'],
                                        lb=AttributeSkillOptimizer.SKILL_RANGE['lb'],
                                        ub=AttributeSkillOptimizer.SKILL_RANGE['ub'],
                                        integer=True) for skill in Skill]
            # Optimize initial guess
            for i, skill in enumerate(Skill):
                if skill in target_values:
                    attribute_rating = self._get_gekko_var(self.skills[skill].attribute, attribute_ratings).value
                    skill_ratings[i].value = target_values[skill] - attribute_rating

            # Target value constraints: Target values must be met or larger.
            for target, target_value in target_values.items():
                if target in Attribute:
                    solver.Equation(self._get_gekko_var(target, attribute_ratings) >= target_value)
                else:
                    if target in Skill:
                        rating = self._get_gekko_var(target, skill_ratings)
                        related_attribute = self.skills[target].attribute
                    else:  # Derived property
                        rating = self.derived_properties[target].offset
                        related_attribute = self.derived_properties[target].attribute
                    solver.Equation(rating + self._get_gekko_var(related_attribute, attribute_ratings) >= target_value)

            # Tree of learning constraint: number of non-zero skill ratings >= max. skill rating
            epsilon_for_zero = 0.5  # threshold for a "zero" value
            number_of_nonzero_skill_ratings = solver.sum(
                [solver.if3(skill_rating - epsilon_for_zero, 0, 1) for skill_rating in skill_ratings])
            max_skill_rating = 0
            for skill_rating in skill_ratings:
                max_skill_rating = solver.Intermediate(solver.max3(max_skill_rating, skill_rating))
            solver.Equation(number_of_nonzero_skill_ratings >= max_skill_rating)

            # Objective (intermediates for readability).
            k = np.array([solver.min3(attribute_rating, 3) for attribute_rating in attribute_ratings])
            attribute_cost = solver.Intermediate(
                solver.sum((k - 1) * (k + 2) + 2.5 * (attribute_ratings - k) * (attribute_ratings + k - 3)),
                name='attribute_cost')
            skill_cost = solver.Intermediate(solver.sum(skill_ratings * (np.array(skill_ratings) + 1)),
                                             name='skill_cost')
            solver.Obj(attribute_cost + skill_cost)

            # Solve: Use APOPT to find the optimal Integer solution.
            solver.options.SOLVER = self.solver_id
            solver.solver_options = self.solver_options

            solver.solve(disp=self.is_verbose)

            result = AttributeSkillOptimizerResults()
            result.Tier = self.tier
            result.Attributes = self._get_property_result(Attribute, attribute_ratings + skill_ratings, target_values)
            skill_property_results = self._get_property_result(Skill, attribute_ratings + skill_ratings, target_values)
            result.Skills = SkillResults(
                rating_values={skill.value: int(self._get_gekko_var(skill, skill_ratings).value[0]) for skill in Skill},
                total_values=skill_property_results.Total,
                target_values=skill_property_results.Target)
            result.DerivedProperties = self._get_property_result(DerivedProperty,
                                                                 attribute_ratings + skill_ratings,
                                                                 target_values)
            result.XPCost = XPCost(attribute_costs=int(attribute_cost.VALUE.value[0]),
                                   skill_costs=int(skill_cost.VALUE.value[0]),
                                   total_costs=int(solver.options.objfcnval))
            return result

    @staticmethod
    def _get_gekko_var(var_name: Union[Attribute, Skill], ratings: List[GEKKO.Var]) -> Optional[GEKKO.Var]:
        return next((rating for rating in ratings if rating.name == f"int_{var_name.name.lower()}"), None)

    def _get_property_result(self,
                             property_names: Iterable,
                             all_ratings: List[GEKKO.Var],
                             target_values: Dict[PropertyEnum, int]) -> PropertyResults:

        property_result = PropertyResults()
        for property_name in property_names:
            property_result.Total[property_name.name] = self._get_total_value(property_name, all_ratings)
            if property_name in target_values:
                property_result.Target[property_name.name] = target_values[property_name]
                if property_result.Target[property_name.name] != property_result.Total[property_name.name]:
                    property_result.Missed.append(property_name.name)
        return property_result

    def _get_total_value(self, name: PropertyEnum, all_ratings: List[GEKKO.Var]) -> int:
        if name in Attribute:
            return int(self._get_gekko_var(name, all_ratings).value[0])

        if name in Skill:
            rating = int(self._get_gekko_var(name, all_ratings).value[0])
            related_attribute = self.skills[name].attribute
        else:  # Derived property
            rating = self.derived_properties[name].offset
            related_attribute = self.derived_properties[name].attribute
        return rating + int(self._get_gekko_var(related_attribute, all_ratings).value[0])


class OutputFormat(StringEnum):
    Markdown = 'md'
    JSON = 'json'


def optimize_xp_from_and_to_json(target_value_string: str) -> str:
    """
    Parses & optimizes selected target values the xp.
    :param target_value_string: JSON string with the target values.
    :return: JSON string with the results.
    """
    return optimize_xp(json.loads(target_value_string), output_format=OutputFormat.JSON)


def optimize_xp(target_values: Dict[str, int],
                output_format: OutputFormat = OutputFormat.JSON,
                is_verbose: bool = False) -> str:
    """
    :param target_values: A dictionary containing key-value pairs for 'Tier' and the target values to optimize for
    :param output_format: The string format of the return value
    :param is_verbose: Flag to show detailed solver output.
    :return: The attributes, skills & derived properties. Either as Markdown table or as JSON string.
    """
    tier = target_values.pop('Tier', None)
    if tier is None:
        raise IOError("'Tier' is a mandatory parameter!")
    optimizer = AttributeSkillOptimizer(tier=tier, is_verbose=is_verbose)
    optimizer_result = optimizer.optimize_selection(target_values=input_target_values)
    return str(optimizer_result) if output_format == OutputFormat.JSON else json.dumps(dict(optimizer_result), indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=f"XP Optimizer for Wrath & Glory v{AttributeSkillOptimizer.WRATH_AND_GLORY_CORE_RULES_VERSION}. "
                    f"Target values can be given for each attribute and skill and for most derived properties (e.g. "
                    f"conviction, max. wounds, ...). The function will try to optimize the spent XP, e.g. optimally "
                    f"increase attributes & skills with a min. amount of xp.",
        add_help=True)
    parser.add_argument('-f', '--file',
                        type=str,
                        help='A json file with the name-value pairs for the target values (see other input arguments '
                             'for names & value ranges). The file MUST contain the tier value. If the file is '
                             'specified, duplicate command line parameters take precedence.')
    parser.add_argument('-j', '--return_json',
                        action='store_false',
                        help='If enabled, prints the result as JSON string instead of as Markdown table (default).')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='If enabled, shows diagnostic output of the solver.')
    parser.add_argument('--Tier',
                        type=int,
                        choices=range(AttributeSkillOptimizer.TIER_RANGE['lb'],
                                      AttributeSkillOptimizer.TIER_RANGE['ub'] + 1),
                        help='The tier of the character.')

    # Add optional inputs for each attribute, skill & derived property.
    for target_enum in [Attribute, Skill]:
        value_bounds = getattr(AttributeSkillOptimizer, str(target_enum.__name__).upper() + '_RANGE')
        for target_name in target_enum:
            parser.add_argument(f'--{target_name.name}',
                                type=int,
                                choices=range(value_bounds['lb'], value_bounds['ub'] + 1))
    for target_name in DerivedProperty:
        parser.add_argument(f'--{target_name.name}',
                            type=int,
                            choices=range(value_bounds['lb'], value_bounds['ub'] + 1))

    input_arguments = vars(parser.parse_args())

    # Input values from file...
    input_target_values = dict()
    if input_arguments['file'] is not None:
        if not os.path.isfile(input_arguments['file']):
            raise FileNotFoundError(f"For argument '--file {input_arguments['file']}'")
        with open(input_arguments['file'], 'r') as file:
            input_target_values = json.load(file)
    # ...and directly via command line parameters (supersede file-based values).
    for target_enum in [Attribute, Skill, DerivedProperty]:
        input_target_values.update(
            {target_name.name: input_arguments[target_name.name] for target_name in target_enum if
             input_arguments[target_name.name] is not None})
    if input_arguments['Tier'] is not None:
        input_target_values['Tier'] = input_arguments['Tier']

    print(optimize_xp(input_target_values,
                      output_format=OutputFormat.JSON if input_arguments['return_json'] else OutputFormat.Markdown,
                      is_verbose=input_arguments['verbose']))
