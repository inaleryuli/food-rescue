"""Checks for benchmark timing, scenario coverage, and failure reporting."""

import contextlib
import io
import types
import unittest
from unittest.mock import patch

import benchmark


def scenario_module(call):
    def test(self):
        self.assertEqual(call(), "ok")

    cases = {
        f"test_case_{number:02d}_example": test
        for number in range(1, 11)
    }
    return types.SimpleNamespace(
        ProposalScenarioTests=type("Scenarios", (unittest.TestCase,), cases),
        rank_recipes=lambda: "ok",
        run_food_rescue=lambda: "ok",
    )


class BenchmarkTests(unittest.TestCase):
    def test_timing_records_success_and_exceptions(self):
        samples = []
        with patch.object(benchmark.time, "perf_counter_ns", side_effect=[10, 30, 40, 90]):
            self.assertEqual(benchmark.timed_call(lambda: "ok", samples)(), "ok")
            def fail():
                raise ValueError("bad input")
            with self.assertRaises(ValueError):
                benchmark.timed_call(fail, samples)()
        self.assertEqual(samples, [20, 50])

    def test_strict_boundary_and_repeated_calls(self):
        module = scenario_module(lambda: module.rank_recipes())
        ticks = [tick for _ in range(20) for tick in (0, benchmark.SLA_NS)]
        output = io.StringIO()
        with patch.object(benchmark.time, "perf_counter_ns", side_effect=ticks), \
             contextlib.redirect_stdout(output):
            passed = benchmark.run_benchmark(module, repeats=2)
        self.assertFalse(passed)
        self.assertEqual(output.getvalue().count("SLA violations=2"), 10)

    def test_success_below_boundary(self):
        module = scenario_module(lambda: module.run_food_rescue())
        ticks = [tick for _ in range(10) for tick in (0, benchmark.SLA_NS - 1)]
        with patch.object(benchmark.time, "perf_counter_ns", side_effect=ticks), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(benchmark.run_benchmark(module, repeats=1))

    def test_unmeasured_and_failed_scenarios_fail(self):
        module = scenario_module(lambda: "wrong")
        output = io.StringIO()
        errors = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertFalse(benchmark.run_benchmark(module, repeats=1))
        self.assertIn("No response calls were measured.", errors.getvalue())
        self.assertIn("AssertionError", errors.getvalue())

    def test_missing_or_duplicate_scenario_rejected(self):
        module = scenario_module(lambda: "ok")
        delattr(module.ProposalScenarioTests, "test_case_10_example")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            benchmark.scenario_names(module.ProposalScenarioTests)
        module = scenario_module(lambda: "ok")
        setattr(module.ProposalScenarioTests, "test_case_01_duplicate", lambda self: None)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            benchmark.scenario_names(module.ProposalScenarioTests)

    def test_invalid_repeats_rejected(self):
        for value in ("0", "-1", "abc"):
            with self.subTest(value=value), self.assertRaises(benchmark.argparse.ArgumentTypeError):
                benchmark.positive_int(value)


if __name__ == "__main__":
    unittest.main()
