import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import TextIO

EXAMPLE_FILE = Path("tests/example_file.json")
EXPECTED_RESULTS_SUFFIX = "_expected_results"
EXPECTED_RESULTS_EXTENSIONS = ["md", "json"]

TargetValuesDict = Dict[str, int]
ExampleDataDict = Dict[str, str]


class FileAccessMode(Enum):
    READ = "r"
    WRITE = "w"


def access_expected_result_files(
    access_function: Callable[[TextIO], str], mode: FileAccessMode = FileAccessMode.READ
) -> ExampleDataDict:
    """
    Applies a function to the expected results files.

    Parameters
    ----------
    access_function
        A function on the opened file handle of the expected results file.
    mode
        The file opening mode.

    Returns
    -------
    return_values
        The results of the function for each extension.
    """
    return_values = {}
    for extension in EXPECTED_RESULTS_EXTENSIONS:
        expected_results_file = (
            EXAMPLE_FILE.parent
            / f"{EXAMPLE_FILE.stem}{EXPECTED_RESULTS_SUFFIX}.{extension}"
        )
        with open(expected_results_file, mode=mode.value) as file:
            return_values[extension] = access_function(file)
    return return_values


def load_target_values() -> TargetValuesDict:
    """
    Loads the target values from the example file.

    Returns
    -------
    target_values
    """
    with open(EXAMPLE_FILE) as file:
        target_values: TargetValuesDict = json.load(file)
    return target_values


@dataclass
class ExampleDataContainer:
    target_values: TargetValuesDict
    expected_results: ExampleDataDict


def get_example_data() -> ExampleDataContainer:
    """
    Loads the data from the example file & the according expected results.

    Returns
    -------
    example_data
        The target_values & expected results.
    """

    def access_function(file: TextIO) -> str:
        return file.read()

    return ExampleDataContainer(
        target_values=load_target_values(),
        expected_results=access_expected_result_files(access_function),
    )


def create_expected_results() -> None:  # pragma: nocover
    """
    This function creates the expected-results files for the example file. Useful in case of updates of the format.
    """
    from wrath_and_glory_xp_optimizer.optimizer_core import AttributeSkillOptimizer

    result = AttributeSkillOptimizer(load_target_values()).optimize_selection()

    def access_function(file: TextIO) -> str:
        extension = Path(file.name).suffix.lower()
        if extension == ".json":
            file.write(result.as_json())
        elif extension == ".md":
            file.write(result.as_markdown())
        else:
            file.write(str(result))
        return ""  # Unused

    access_expected_result_files(access_function, mode=FileAccessMode.WRITE)


if __name__ == "__main__":  # pragma: nocover
    create_expected_results()
