import json
from contextlib import contextmanager
from typing import ContextManager, Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

import numpy as np
from gekko import GEKKO
from gekko.gk_operators import GK_Intermediate
from gekko.gk_variable import GKVariable

from .character_properties.attributes import Attributes
from .character_properties.skills import Skills
from .character_properties.tier import Tier
from .character_properties.traits import Traits
from .exceptions import InvalidTargetValueException
from .optimizer_results import (
    AttributeSkillOptimizerResults,
)
from .optimizer_results import CharacterPropertyResults
from .optimizer_results import SkillResults
from .optimizer_results import XPCost


@contextmanager
def managed_gekko_solver(*args, **kwargs) -> ContextManager[GEKKO]:
    """
    Context manager for the GEKKO class, to automatically clean-up temp. files & folders after solving.
    """
    solver = GEKKO(*args, **kwargs)
    try:
        yield solver
    finally:
        solver.cleanup()


class AttributeSkillOptimizer:
    WRATH_AND_GLORY_CORE_RULES_VERSION = 2.1

    DEFAULT_SOLVER_OPTIONS = (
        "minlp_maximum_iterations 500",
        "minlp_max_iter_with_int_sol 50",  # minlp iterations with integer solution
        "minlp_as_nlp 0",  # treat minlp as nlp
        "nlp_maximum_iterations 50",  # nlp sub-problem max_value iterations
        "minlp_branch_method 1",  # 1 = depth first, 2 = breadth first
        "minlp_integer_tol 0.05",  # maximum deviation from whole number
        "minlp_gap_tol 0.01",
    )  # convergence tolerance

    def __init__(
            self,
            target_values: Dict[str, int],
            is_verbose: bool = False,
            solver_options: Tuple[str, ...] = DEFAULT_SOLVER_OPTIONS,
    ):
        """
        Parameters
        ----------
        target_values
            A dictionary containing key-value pairs for 'Tier' and the attributes, skills & traits to optimize the XP
            for. If Tier is missing, the default value of 1 is used.
        is_verbose
            If to show additional solver output.
        solver_options
            Options passed to the Gekko class.
        """
        if Tier.full_name not in target_values:
            target_values[Tier.full_name] = Tier.rating_bounds.min
        if not self.is_valid_target_values_dict(target_values):
            raise InvalidTargetValueException(
                f"Invalid target value(s) found: \n{json.dumps(target_values, indent=2)}"
            )

        self.tier: int = target_values.pop(Tier.full_name)
        self.target_values: Dict[str, int] = target_values
        self.solver_id = (
            1  # Use APOPT to find the optimal Integer solution, since this is a MINLP.
        )
        self.solver_options = list(solver_options)
        self.is_verbose: bool = is_verbose

    @staticmethod
    def is_valid_target_values_dict(target_values: Dict[str, int]) -> bool:
        """
        Checks if the given dictionary adheres to the expected format, e.g. contains the required parameters and each
        value is within its specified bounds.

        Parameters
        ----------
        target_values
            The dictionary to check.

        Returns
        -------
        is_valid
            True if all checks passed, False otherwise.

        """
        tier = target_values.get(Tier.full_name)
        if not Tier.is_valid_rating(tier):
            return False

        for target_name, target_value in target_values.items():
            if not (target_name == Tier.full_name or Attributes.get_by_name(target_name).value.is_valid_rating(target_value)
                    or Skills.get_by_name(target_name).value.is_valid_total_rating(target_value)
                    or Traits.get_by_name(target_name).value.is_valid_rating(target_value, tier)
            ):
                return False

        return True

    def optimize_selection(self) -> AttributeSkillOptimizerResults:
        """
        Note
        ----
        This was done with the help of John Hedengren from Gekko (see https://stackoverflow.com/questions/65863807)
        """
        with managed_gekko_solver(remote=False) as solver:
            # Define variables with optimized initial values.
            attribute_ratings = [
                solver.Var(
                    name=attribute.name,
                    value=self.target_values.get(
                        attribute.name, attribute.value.rating_bounds.min
                    ),
                    lb=attribute.value.rating_bounds.min,
                    ub=attribute.value.rating_bounds.max,
                    integer=True,
                )
                for attribute in Attributes.get_valid_members()
            ]
            skill_ratings = [
                solver.Var(
                    name=skill.name,
                    value=skill.value.rating_bounds.min,
                    lb=skill.value.rating_bounds.min,
                    ub=skill.value.rating_bounds.max,
                    integer=True,
                )
                for skill in Skills.get_valid_members()
            ]
            # Optimize initial guess
            for i, skill in enumerate(Skills):
                if skill.name in self.target_values:
                    attribute_rating = self._get_gekko_var(
                        skill.value.related_attribute, attribute_ratings
                    ).value
                    skill_ratings[i].value = (
                            self.target_values[skill.name] - attribute_rating
                    )

            # Target value constraints: Target values must be met or larger.
            for target, target_value in self.target_values.items():
                if (
                        target_enum := Attributes.get_by_name(target)
                ) != Attributes.INVALID:
                    solver.Equation(
                        self._get_gekko_var(target_enum, attribute_ratings)
                        >= target_value
                    )
                else:
                    if (target_enum := Skills.get_by_name(target)) != Skills.INVALID:
                        rating = self._get_gekko_var(target_enum, skill_ratings)
                        related_attribute = target_enum.value.related_attribute
                    else:  # Traits
                        target_enum = Traits.get_by_name(target)
                        rating = target_enum.value.get_total_attribute_offset(self.tier)
                        related_attribute = target_enum.value.related_attribute
                    solver.Equation(
                        rating
                        + self._get_gekko_var(related_attribute, attribute_ratings)
                        >= target_value
                    )

            # Tree of learning constraint: number of non-zero skill ratings >= max_value. skill rating
            epsilon_for_zero = 0.5  # threshold for a "zero" value
            number_of_nonzero_skill_ratings = solver.sum(
                [
                    solver.if3(skill_rating - epsilon_for_zero, 0, 1)
                    for skill_rating in skill_ratings
                ]
            )
            max_skill_rating = 0
            for skill_rating in skill_ratings:
                max_skill_rating = solver.Intermediate(
                    solver.max3(max_skill_rating, skill_rating)
                )
            solver.Equation(number_of_nonzero_skill_ratings >= max_skill_rating)

            # Objective (intermediates for readability).
            k = np.array(
                [
                    solver.min3(attribute_rating, 3)
                    for attribute_rating in attribute_ratings
                ]
            )
            attribute_cost = solver.Intermediate(
                solver.sum(
                    (k - 1) * (k + 2)
                    + 2.5 * (attribute_ratings - k) * (attribute_ratings + k - 3)
                ),
                name="attribute_cost",
            )
            skill_cost = solver.Intermediate(
                solver.sum(skill_ratings * (np.array(skill_ratings) + 1)),
                name="skill_cost",
            )
            solver.Obj(attribute_cost + skill_cost)

            # Solve: Use APOPT to find the optimal Integer solution.
            solver.options.SOLVER = self.solver_id
            solver.solver_options = self.solver_options

            solver.solve(disp=self.is_verbose)

            return self._compile_results(attribute_ratings, skill_ratings, attribute_cost, skill_cost)

    def _compile_results(
            self,
            attribute_ratings: List[GKVariable],
            skill_ratings: List[GKVariable],
            attribute_cost: GK_Intermediate,
            skill_cost: GK_Intermediate,
    ):
        all_ratings = attribute_ratings + skill_ratings

        skill_property_results = self._get_property_result(Skills, all_ratings)
        skill_result = SkillResults(
            rating_values={
                skill.name: int(self._get_gekko_var(skill, skill_ratings).value[0])
                for skill in Skills.get_valid_members()
            },
            total_values=skill_property_results.Total,
            target_values=skill_property_results.Target,
        )

        return AttributeSkillOptimizerResults(
            Tier=self.tier,
            Attributes=self._get_property_result(Attributes, all_ratings),
            Skills=skill_result,
            Traits=self._get_property_result(Traits, all_ratings),
            XPCost=XPCost(
                Attributes=int(attribute_cost.VALUE.value[0]),
                Skills=int(skill_cost.VALUE.value[0]),
            ),
        )

    @staticmethod
    def _get_gekko_var(
            attribute_or_skill: Union[Attributes, Skills], ratings: List[GKVariable]
    ) -> Optional[GKVariable]:
        return next(
            (
                rating
                for rating in ratings
                if rating.name == f"int_{attribute_or_skill.name.lower()}"
            )
        )

    def _get_property_result(
            self,
            property_class: Union[Type[Attributes], Type[Skills], Type[Traits]],
            all_ratings: List[GKVariable],
    ) -> CharacterPropertyResults:

        property_result = CharacterPropertyResults()
        for property_member in property_class.get_valid_members():
            property_name = property_member.name
            property_result.Total[property_name] = self._get_total_value(
                property_member, all_ratings
            )
            if property_name in self.target_values:
                property_result.Target[property_name] = self.target_values[
                    property_name
                ]
                if (
                        property_result.Target[property_name]
                        != property_result.Total[property_name]
                ):
                    property_result.Missed.append(property_name)
        return property_result

    def _get_total_value(
            self,
            target_enum: Union[Attributes, Skills, Traits],
            all_ratings: List[GKVariable],
    ) -> int:
        if target_enum in Attributes:
            rating = 0
            related_attribute = target_enum
        elif target_enum in Skills:
            rating = int(self._get_gekko_var(target_enum, all_ratings).value[0])
            related_attribute = target_enum.value.related_attribute
        else:  # Traits
            rating = target_enum.value.get_total_attribute_offset(self.tier)
            related_attribute = target_enum.value.related_attribute

        return rating + int(
            self._get_gekko_var(related_attribute, all_ratings).value[0]
        )


def optimize_xp(
        target_values: Dict[str, int], is_verbose: bool = False
) -> AttributeSkillOptimizerResults:
    """
    Parameters
    ----------
    target_values
        A dictionary containing key-value pairs for 'Tier' and the attributes, skills & traits. If Tier is missing, the
        default value of 1 is used.
    is_verbose
        Flag to show detailed solver output.

    Returns
    -------
    optimized_results
        The attributes, skills & traits. Either as Markdown table or as JSON string.

    """
    return AttributeSkillOptimizer(target_values, is_verbose).optimize_selection()
