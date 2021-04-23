import json
import unittest
from typing import Tuple

from click.testing import CliRunner, Result
from wrath_and_glory_xp_optimizer.character_properties import Tier
from wrath_and_glory_xp_optimizer.optimize_xp import cli

from tests.example_file_access import get_example_data, EXPECTED_RESULTS_EXTENSIONS, EXAMPLE_FILE


class TestOptimizeXpCLI(unittest.TestCase):
    VALID_EXIT_CODE = 0
    example_file_name = str(EXAMPLE_FILE)

    def run_with_example_file(self, additional_arguments: Tuple[str, ...] = ()) -> Result:
        return CliRunner().invoke(cli, [self.example_file_name] + list(additional_arguments))

    def assert_valid_exit_code(self, cli_result):
        self.maxDiff = None  # Show diff for long comparisons.
        self.assertEqual(self.VALID_EXIT_CODE, cli_result.exit_code, f"Observed result\n{cli_result.output}")

    def test_file_argument_with_invalid_target_values_expect_invalid_exit_code(self):
        invalid_example_file_name = "invalid_example_file.json"
        cli_runner = CliRunner()

        with cli_runner.isolated_filesystem():
            with open(invalid_example_file_name, "w") as invalid_example_file:
                json.dump({Tier.full_name: Tier.rating_bounds.max + 1}, invalid_example_file)
            result = cli_runner.invoke(cli, [invalid_example_file_name])

        self.assertNotEqual(self.VALID_EXIT_CODE, result.exit_code)

    def test_file_argument_with_valid_target_values_expect_valid_exit_code(self):
        self.assert_valid_exit_code(CliRunner().invoke(cli, [self.example_file_name]))

    def test_output_formats_expect_valid_exit_code_and_correctly_formatted_results(self):
        example_data = get_example_data()
        for extension in EXPECTED_RESULTS_EXTENSIONS:
            with self.subTest(i=extension):
                result = self.run_with_example_file(additional_arguments=("--output-format", extension))
                self.assert_valid_exit_code(result)
                # Remove additional newline from echo.
                self.assertEqual(example_data["expected_results"][extension], result.output[:-1])

    def test_verbose_flag_expect_valid_exit_code_and_longer_output_than_normal_execution(self):
        normal_result = self.run_with_example_file()
        verbose_result = self.run_with_example_file(additional_arguments=("--verbose",))
        self.assert_valid_exit_code(verbose_result)
        self.assertGreater(len(verbose_result.output), len(normal_result.output))

    def test_help_and_version_flags_expect_valid_exit_code(self):
        runner = CliRunner()
        for arg in ["--help", "--help-target-values", "--version"]:
            with self.subTest(i=arg):
                self.assert_valid_exit_code(runner.invoke(cli, [arg]))
