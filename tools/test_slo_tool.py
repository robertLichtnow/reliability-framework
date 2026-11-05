"""Tests for slo_tool. Run with: python -m unittest discover tools"""

import copy
import io
import os
import unittest
from contextlib import redirect_stdout

import yaml

import slo_tool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(ROOT, "slo", "examples", "checkout-api")
TEMPLATE = os.path.join(ROOT, "slo", "templates", "slo.yaml")


def run(command, path):
    out = io.StringIO()
    with redirect_stdout(out):
        code = slo_tool.main([command, path])
    return code, out.getvalue()


class BurnRateTest(unittest.TestCase):
    def test_matches_site_reliability_workbook_for_30_days(self):
        rates = [slo_tool.burn_rate(f, w, 30) for f, w, _, _ in slo_tool.ALERT_POLICY]
        self.assertEqual([round(r, 6) for r in rates], [14.4, 6.0, 1.0])

    def test_scales_with_window(self):
        self.assertAlmostEqual(slo_tool.burn_rate(0.02, "1h", 7), 3.36)


class ValidationTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(EXAMPLE, "slo.yaml"), encoding="utf-8") as f:
            self.doc = yaml.safe_load(f)

    def test_shipped_files_are_valid(self):
        for path in (TEMPLATE, os.path.join(EXAMPLE, "slo.yaml")):
            self.assertEqual(run("check", path)[0], 0, path)

    def assertInvalid(self, doc, message):
        with self.assertRaises(slo_tool.SLOError) as ctx:
            slo_tool.validate(doc)
        self.assertIn(message, str(ctx.exception))

    def test_rejects_100_percent(self):
        doc = copy.deepcopy(self.doc)
        doc["slos"][0]["objective"] = 100
        self.assertInvalid(doc, "objective")

    def test_rejects_missing_window_placeholder(self):
        doc = copy.deepcopy(self.doc)
        doc["slos"][0]["sli"]["good"] = "sum(rate(x[5m]))"
        self.assertInvalid(doc, "sli.good")

    def test_rejects_duplicate_names(self):
        doc = copy.deepcopy(self.doc)
        doc["slos"][1]["name"] = doc["slos"][0]["name"]
        self.assertInvalid(doc, "duplicated")

    def test_rejects_missing_fields(self):
        self.assertInvalid({"service": "x"}, "missing required field 'owner'")


class OutputTest(unittest.TestCase):
    def test_budget_shows_allowed_downtime(self):
        _, out = run("budget", os.path.join(EXAMPLE, "slo.yaml"))
        self.assertIn("21m 36s", out)
        self.assertIn("43m 12s", out)

    def test_rules_threshold_is_burn_rate_times_budget(self):
        _, out = run("rules", os.path.join(EXAMPLE, "slo.yaml"))
        rules = yaml.safe_load(out)
        alert = rules["groups"][1]["rules"][0]
        self.assertIn("> 0.0072", alert["expr"])  # 14.4 * 0.0005

    def test_committed_example_rules_are_up_to_date(self):
        _, out = run("rules", os.path.join(EXAMPLE, "slo.yaml"))
        with open(os.path.join(EXAMPLE, "prometheus-rules.yaml"), encoding="utf-8") as f:
            self.assertEqual(f.read(), out)


if __name__ == "__main__":
    unittest.main()
