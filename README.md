# Wrath & Glory XP Optimizer

[![PyPI](https://img.shields.io/pypi/v/WrathAndGloryOptimizer.svg)](https://pypi.org/project/WrathAndGloryOptimizer/)
[![Python Version](https://img.shields.io/pypi/pyversions/WrathAndGloryOptimizer)](https://pypi.org/project/WrathAndGloryOptimizer)
[![License](https://img.shields.io/pypi/l/WrathAndGloryOptimizer)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/LordFckHelmchen/WrathAndGloryOptimizer/workflows/Tests/badge.svg)](https://github.com/LordFckHelmchen/WrathAndGloryOptimizer/actions?workflow=Tests)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

Ever wondered if it is better to choose _Agility_ over separate points into _Ballistic Skill_ & _Stealth_? Ever thought
that your current character has only _Intellect_ but no points left for anything else?

This repo contains a Mixed-Integer Non-Linear Programming (MI-NLP) optimization solution to spending the optimal amount
of XP on selected attributes, skills & traits in the role-playing
game [Wrath & Glory by Cubicle 7](https://www.cubicle7games.com/our-games/wrath-glory/).

For simple character management, I recommend using
the [Character Forge @ Doctors of Doom](https://www.doctors-of-doom.com/forge/my-characters). The XP optimizer can then
minimize the spent XP for your created character. Just pass in your desired target values (e.g., the total values for _
Cunning_, _Tech_ & _Deception_ and your desired _Strength_), and the optimizer will figure out the best distribution
under minimal XP.

If you encounter any errors/wrong numbers please post your input & the expected values, so I can debug them. If you have
any recommendations, feel free to leave some comments.

The optimizer uses v2.1 of the core rules. It does not take into account any bonuses or prerequisites from species and
archetypes - but these should be fine given that they use the same XP cost tables.

The theoretical background around the involved formulas can be found [here](docs/theoretical_background.md)

## Features

- TODO

## Requirements

- Python 3.8 or better
- TODO

## Installation

- TODO
- Install Python, if not already done.
- Switch to folder of this project, open terminal & install requirements

  ```Bash
  pip install -r requirements.txt
  ```

- Try, if it works (shows help content)

  ```Bash
  python3 optimize-xp --help
  ```

## Usage

### NOTES

- You always have to specify the _tier_ of your character!
- The optimizer takes the tree-of-learning rule into account, but assigns the skill ratings randomly (within the min-xp
  constraint). Simply move the 1s around to your liking - the xp cost stay the same.

### Via command-line interface (CLI)

- TODO

Please see the [Command-line Reference](docs/usage.rst) for details.

The CLI takes a JSON file as input with your tier, and your target values (see
tests/example_file.json for an example).

Let's say you want to optimize your _Tier_ 1 character with _Strength_ 3 and _Max Wounds_ 5. First create a file (
e.g. `my_file.json`) with the following content:

```json
{
  "Tier": 1,
  "Strength": 3,
  "MaxWounds": 5
}
```

Then run the optimizer in the command line from the same folder as the file:

```Bash
python optimize-xp my_file.json
```

which will output a Markdown table showing the different properties, their (total) ratings, and the spent XP.

#### A more complex example

If you have a higher-level character and want to optimize the following properties at _Tier_ 3

- _Agility_ 5
- _BallisticSkill_ 11
- _Cunning_ 7
- _Deception_ 8
- _Stealth_ 12
- _Defence_ 6 (note the British spelling!)
- _Max Wounds_ 10

then create a file (e.g. `my_file.json`) with the following content:

```json
{
  "Tier": 3,
  "Agility": 5,
  "BallisticSkill": 11,
  "Cunning": 7,
  "Deception": 8,
  "Stealth": 12,
  "Defence": 6,
  "MaxWounds": 10
}
```

This time you'd like to have a json file as output. Then call:

```Bash
python optimize-xp my_file.json --output-format json
```

For a list of available CLI parameters use:

```Bash
python optimize-xp --help
```

## License

Distributed under the terms of the [MIT license](https://opensource.org/licenses/MIT),
_Wrath & Glory XP Optimizer_ is free and open source software.

## Issues

If you encounter any problems, please [file an issue](https://github.com/LordFckHelmchen/WrathAndGloryOptimizer/issues)
along with a detailed description.

## Credits

This project was generated from
[@cjolowicz](https://github.com/cjolowicz) [Hypermodern Python Cookiecutter](https://github.com/cjolowicz/cookiecutter-hypermodern-python)
template.
