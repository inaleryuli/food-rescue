"""Benchmark the ten proposal scenarios' in-process response calls."""

import argparse
import importlib.util
import re
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch


SLA_NS = 1_500_000_000
SCENARIO_PATH = Path(__file__).resolve().parent / "tests" / "test_scenarios.py"
SCENARIO_PATTERN = re.compile(r"^test_case_(\d{2})_")


def load_scenarios():
    spec = importlib.util.spec_from_file_location("benchmark_scenarios", SCENARIO_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load scenarios from {SCENARIO_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scenario_names(test_class):
    names = unittest.TestLoader().getTestCaseNames(test_class)
    scenarios = [name for name in names if SCENARIO_PATTERN.match(name)]
    numbers = [SCENARIO_PATTERN.match(name).group(1) for name in scenarios]
    if sorted(numbers) != [f"{number:02d}" for number in range(1, 11)]:
        raise ValueError("Expected exactly one scenario for each case 01 through 10.")
    return scenarios


def timed_call(function, samples):
    def wrapped(*args, **kwargs):
        start = time.perf_counter_ns()
        try:
            return function(*args, **kwargs)
        finally:
            samples.append(time.perf_counter_ns() - start)

    return wrapped


def run_benchmark(module, repeats):
    names = scenario_names(module.ProposalScenarioTests)
    all_passed = True
    print("In-process scenario response benchmark (strict SLA: < 1.500 s per call)")
    print(f"Iterations per scenario: {repeats}")

    for name in names:
        samples = []
        failures = []
        for iteration in range(1, repeats + 1):
            previous_count = len(samples)
            result = unittest.TestResult()
            with patch.object(module, "rank_recipes", timed_call(module.rank_recipes, samples)), \
                 patch.object(module, "run_food_rescue", timed_call(module.run_food_rescue, samples)):
                module.ProposalScenarioTests(name).run(result)
            for _, detail in result.failures + result.errors:
                failures.append(f"iteration {iteration}:\n{detail}")
            for _, reason in result.skipped:
                failures.append(f"iteration {iteration}: skipped: {reason}")
            for test, detail in result.expectedFailures:
                failures.append(f"iteration {iteration}: expected failure: {detail}")
            for test in result.unexpectedSuccesses:
                failures.append(f"iteration {iteration}: unexpected success: {test}")
            if len(samples) == previous_count:
                failures.append(f"iteration {iteration}: No response calls were measured.")

        slow = sum(duration >= SLA_NS for duration in samples)
        passed = not failures and slow == 0
        all_passed = all_passed and passed
        durations = ", ".join(f"{duration / 1e9:.9f}" for duration in samples)
        print(f"{'PASS' if passed else 'FAIL'} {name}: calls={len(samples)}, "
              f"seconds=[{durations}], SLA violations={slow}")
        for failure in failures:
            print(failure, file=sys.stderr)

    print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


def positive_int(value):
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=positive_int, default=1,
                        help="number of runs per scenario (default: 1)")
    args = parser.parse_args(argv)
    return 0 if run_benchmark(load_scenarios(), args.repeats) else 1


if __name__ == "__main__":
    sys.exit(main())
