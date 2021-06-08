"""
Command-line interface of the optimizer core.
"""
import json
from typing import Any
from typing import TextIO

import click

from wrath_and_glory_xp_optimizer import __version__
from wrath_and_glory_xp_optimizer.character_properties import Attributes
from wrath_and_glory_xp_optimizer.character_properties import IntBounds
from wrath_and_glory_xp_optimizer.character_properties import Skills
from wrath_and_glory_xp_optimizer.character_properties import Tier
from wrath_and_glory_xp_optimizer.character_properties import Traits
from wrath_and_glory_xp_optimizer.exceptions import InvalidTargetValueException
from wrath_and_glory_xp_optimizer.optimizer_core import AttributeSkillOptimizer
from wrath_and_glory_xp_optimizer.optimizer_core import optimize_xp


def print_target_values_text(click_context: click.Context, _: Any, value: Any) -> None:
    if not value or click_context.resilient_parsing:
        return

    indent = "   "
    max_name_width = max(
        max(
            len(target_enum.name)
            for target_enum in target_enum_class.get_valid_members()
        )
        for target_enum_class in [Attributes, Skills, Traits]
    )
    name_format = "{0:" + str(max_name_width) + "}"

    def format_entry(name: str, bounds: IntBounds) -> str:
        return f"{indent}{name_format.format(name)}  {bounds}"

    properties = [
        "The following target values are available:",
        "TIER",
        f"{format_entry(Tier.full_name, Tier.rating_bounds)} -> This is a mandatory parameter!",
    ]

    for target_enum_class in [Attributes, Skills, Traits]:
        properties.append(target_enum_class.__name__.upper())
        for target_enum in target_enum_class.get_valid_members():
            if not isinstance(target_enum, Traits):
                rating_bounds = target_enum.value.rating_bounds
            else:
                rating_bounds = IntBounds(
                    target_enum.value.get_rating_bounds(
                        related_tier=Tier.rating_bounds.min
                    ).min,
                    target_enum.value.get_rating_bounds(
                        related_tier=Tier.rating_bounds.max
                    ).max,
                )
            properties.append(format_entry(target_enum.name, rating_bounds))

    click.echo(f"\n{indent}".join(properties))
    click_context.exit()


@click.command(name="optimizer-xp", no_args_is_help=True)
@click.argument("file", type=click.File(mode="r"))
@click.option(
    "-o",
    "--output-format",
    type=click.Choice(["md", "markdown", "json"], case_sensitive=False),
    help="Type of the printed result: Either a JSON string (json) or a Markdown table (markdown/md).",
    default="markdown",
    show_default=True,
)
@click.option(
    "-v",
    "--verbose",
    "is_verbose",
    is_flag=True,
    help="If given, shows diagnostic output.",
)
@click.version_option(
    version=f"{__version__} (Wrath & Glory core rules version "
    f"{AttributeSkillOptimizer.WRATH_AND_GLORY_CORE_RULES_VERSION})"
)
@click.option(
    "--help-target-values",
    is_flag=True,
    help="Show the possible target values and exit.",
    callback=print_target_values_text,
    expose_value=False,
    is_eager=True,
)
def cli(file: TextIO, output_format: str, is_verbose: bool):
    """
    XP Optimizer for Wrath & Glory (see README.md for more details).

    Target values for attributes, skills & most traits (e.g. conviction, max. wounds, ...) can be given and the
    function will try to optimize the spent XP, e.g. optimally increase the ratings for attributes & skills with a
    minimum amount of xp.

    The function takes an existing FILE in JSON-format with the name-value pairs for the target values. FILE must
    contain the "Tier" value.
    """
    if is_verbose:
        click.echo(
            f"optimizer-xp(file='{file.name}', output_format='{output_format}', is_verbose={is_verbose})\n"
        )

    try:
        optimizer_result = optimize_xp(json.load(file), is_verbose=is_verbose)
        click.echo(
            optimizer_result.as_json()
            if output_format == "json"
            else optimizer_result.as_markdown()
        )
    except InvalidTargetValueException as error:
        raise click.ClickException(str(error))


if __name__ == "__main__":  # pragma: no cover
    cli()
