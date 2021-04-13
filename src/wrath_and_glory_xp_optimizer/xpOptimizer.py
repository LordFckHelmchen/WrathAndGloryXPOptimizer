__version__ = 1.5

import argparse
import json
import os
from typing import Optional, Dict, Union, List, Tuple, Type

import numpy as np
from gekko import GEKKO

from src.wrath_and_glory_xp_optimizer.characterProperties import Tier, Attributes, Skills, Traits, IntBounds
from src.wrath_and_glory_xp_optimizer.xpOptimizerResults import CharacterPropertyResults, SkillResults, XPCost, AttributeSkillOptimizerResults


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

    def __init__(self,
                 tier: int = 1,
                 is_verbose: bool = False,
                 solver_options: Tuple[str] = DEFAULT_SOLVER_OPTIONS):
        if not Tier.is_valid_rating(tier):
            raise IOError(f"'tier' must be within {Tier.rating_bounds}, was {tier} instead.")
        self.tier: int = tier
        self.solver_id = 1  # Use APOPT to find the optimal Integer solution, since this is a MINLP.
        self.solver_options = solver_options
        self.is_verbose: bool = is_verbose

    def optimize_selection(self, target_values: Dict[str, int]) -> AttributeSkillOptimizerResults:
        """
        Note
        ----
        This was done with the help of John Hedengren from Gekko (see https://stackoverflow.com/questions/65863807)
        """
        if not is_valid_target_values_dict({Tier.full_name: self.tier, **target_values}):
            raise IOError(f"Invalid target values found: \n{json.dumps(target_values, indent=2)}")

        with GekkoContext(remote=False) as solver:
            # Define variables with optimized initial values.
            attribute_ratings = [solver.Var(name=attribute.name,
                                            value=target_values.get(attribute.name,
                                                                    attribute.value.rating_bounds.min),
                                            lb=attribute.value.rating_bounds.min,
                                            ub=attribute.value.rating_bounds.max,
                                            integer=True) for attribute in Attributes.get_valid_members()]
            skill_ratings = [solver.Var(name=skill.name,
                                        value=skill.value.rating_bounds.min,
                                        lb=skill.value.rating_bounds.min,
                                        ub=skill.value.rating_bounds.max,
                                        integer=True) for skill in Skills.get_valid_members()]
            # Optimize initial guess
            for i, skill in enumerate(Skills):
                if skill.name in target_values:
                    attribute_rating = self._get_gekko_var(skill.value.related_attribute, attribute_ratings).value
                    skill_ratings[i].value = target_values[skill.name] - attribute_rating

            # Target value constraints: Target values must be met or larger.
            for target, target_value in target_values.items():
                if (target_enum := Attributes.get_by_name(target)) != Attributes.INVALID:
                    solver.Equation(self._get_gekko_var(target_enum, attribute_ratings) >= target_value)
                else:
                    if (target_enum := Skills.get_by_name(target)) != Skills.INVALID:
                        rating = self._get_gekko_var(target_enum, skill_ratings)
                        related_attribute = target_enum.value.related_attribute
                    else:  # Traits
                        target_enum = Traits.get_by_name(target)
                        rating = target_enum.value.get_total_attribute_offset(related_tier=self.tier)
                        related_attribute = target_enum.value.related_attribute
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
            result.Attributes = self._get_property_result(Attributes, attribute_ratings + skill_ratings, target_values)
            skill_property_results = self._get_property_result(Skills, attribute_ratings + skill_ratings, target_values)
            result.Skills = SkillResults(
                rating_values={skill.name: int(self._get_gekko_var(skill, skill_ratings).value[0])
                               for skill in Skills.get_valid_members()},
                total_values=skill_property_results.Total,
                target_values=skill_property_results.Target)
            result.Traits = self._get_property_result(Traits,
                                                      attribute_ratings + skill_ratings,
                                                      target_values)
            result.XPCost = XPCost(attribute_costs=int(attribute_cost.VALUE.value[0]),
                                   skill_costs=int(skill_cost.VALUE.value[0]),
                                   total_costs=int(solver.options.objfcnval))
            return result

    @staticmethod
    def _get_gekko_var(attribute_or_skill: Union[Attributes, Skills], ratings: List[GEKKO.Var]) -> Optional[GEKKO.Var]:
        return next((rating for rating in ratings if rating.name == f"int_{attribute_or_skill.name.lower()}"), None)

    def _get_property_result(self,
                             property_class: Union[Type[Attributes], Type[Skills], Type[Traits]],
                             all_ratings: List[GEKKO.Var],
                             target_values: Dict[str, int]) -> CharacterPropertyResults:

        property_result = CharacterPropertyResults()
        for property_member in property_class.get_valid_members():
            property_name = property_member.name
            property_result.Total[property_name] = self._get_total_value(property_member, all_ratings)
            if property_name in target_values:
                property_result.Target[property_name] = target_values[property_name]
                if property_result.Target[property_name] != property_result.Total[property_name]:
                    property_result.Missed.append(property_name)
        return property_result

    def _get_total_value(self, target_enum: Union[Attributes, Skills, Traits], all_ratings: List[GEKKO.Var]) -> int:
        if target_enum in Attributes:
            rating = 0
            related_attribute = target_enum
        elif target_enum in Skills:
            rating = int(self._get_gekko_var(target_enum, all_ratings).value[0])
            related_attribute = target_enum.value.related_attribute
        else:  # Traits
            rating = target_enum.value.get_total_attribute_offset(self.tier)
            related_attribute = target_enum.value.related_attribute

        return rating + int(self._get_gekko_var(related_attribute, all_ratings).value[0])


def optimize_xp(target_values: Dict[str, int], is_verbose: bool = False) -> AttributeSkillOptimizerResults:
    """
    :param target_values: A dictionary containing key-value pairs for 'Tier' and the attributes, skills & traits.
    :param is_verbose: Flag to show detailed solver output.
    :return: The attributes, skills & traits. Either as Markdown table or as JSON string.
    """
    tier = target_values.pop('Tier', None)
    if tier is None:
        raise IOError("'Tier' is a mandatory parameter!")
    optimizer = AttributeSkillOptimizer(tier=tier, is_verbose=is_verbose)
    return optimizer.optimize_selection(target_values=target_values)


def is_valid_target_values_dict(target_values: Dict[str, int]) -> bool:
    tier = target_values.get(Tier.full_name)
    if not Tier.is_valid_rating(tier):
        return False

    for target_name, target_value in target_values.items():
        if not (target_name == Tier.full_name
                or Attributes.get_by_name(target_name).value.is_valid_rating(target_value)
                or Skills.get_by_name(target_name).value.is_valid_total_rating(target_value)
                or Traits.get_by_name(target_name).value.is_valid_rating(target_value, tier)):
            return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=f"XP Optimizer for Wrath & Glory v{AttributeSkillOptimizer.WRATH_AND_GLORY_CORE_RULES_VERSION}. "
                    f"Target values can be given for each attribute and skill and for most traits (e.g. conviction, "
                    f"max. wounds, ...). The function will try to optimize the spent XP, e.g. optimally increase "
                    f"attributes & skills with a min. amount of xp.",
        add_help=True)
    parser.add_argument('-f', '--file',
                        type=str,
                        help='A json file with the name-value pairs for the target values (see other input arguments '
                             'for names & value ranges). The file MUST contain the tier value. If the file is '
                             'specified, duplicate command line parameters take precedence.')
    parser.add_argument('-j', '--return_json',
                        action='store_true',
                        help='If enabled, prints the result as JSON string instead of as Markdown table (default).')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='If enabled, shows diagnostic output of the solver.')
    parser.add_argument('--Tier',
                        type=int,
                        choices=Tier.rating_bounds.as_range(),
                        help='The tier of the character.')

    # Add optional inputs for each attribute, skill & trait
    for target_enum_class in [Attributes, Skills]:
        for target_enum in target_enum_class.get_valid_members():
            parser.add_argument(f'--{target_enum.name}', type=int, choices=target_enum.value.rating_bounds.as_range())
    for trait in Traits.get_valid_members():
        rating_bounds = IntBounds(trait.value.get_rating_bounds(related_tier=Tier.rating_bounds.min).min,
                                  trait.value.get_rating_bounds(related_tier=Tier.rating_bounds.max).max)
        parser.add_argument(f'--{trait.name}', type=int, choices=rating_bounds.as_range())

    input_arguments = vars(parser.parse_args())

    # Input values from file...
    input_target_values = dict()
    if input_arguments['file'] is not None:
        if not os.path.isfile(input_arguments['file']):
            raise FileNotFoundError(f"For argument '--file {input_arguments['file']}'")
        with open(input_arguments['file'], 'r') as file:
            input_target_values = json.load(file)
    # ...and directly via command line parameters (supersede file-based values).
    for target_enum_class in [Attributes, Skills, Traits]:
        input_target_values.update({target_enum.name: input_arguments[target_enum.name]
                                    for target_enum in target_enum_class.get_valid_members()
                                    if input_arguments.get(target_enum.name) is not None})
    if input_arguments['Tier'] is not None:
        input_target_values['Tier'] = input_arguments['Tier']

    optimizer_result = optimize_xp(input_target_values, is_verbose=input_arguments['verbose'])
    print(json.dumps(dict(optimizer_result), indent=2) if input_arguments['return_json'] else str(optimizer_result))
