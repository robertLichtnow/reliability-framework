#!/usr/bin/env python3
"""Validate SLO files, print error budgets, and generate Prometheus rules.

Usage:
    python tools/slo_tool.py check  <slo.yaml>
    python tools/slo_tool.py budget <slo.yaml>
    python tools/slo_tool.py rules  <slo.yaml>

Alerting follows the multi-window, multi-burn-rate method described in
Google's "The Site Reliability Workbook", chapter 5 ("Alerting on SLOs").
"""

import argparse
import re
import sys

import yaml

# (budget fraction consumed, long window, short window, severity)
ALERT_POLICY = [
    (0.02, "1h", "5m", "page"),
    (0.05, "6h", "30m", "page"),
    (0.10, "3d", "6h", "ticket"),
]
WINDOWS = ["5m", "30m", "1h", "6h", "3d"]
NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
UNIT_HOURS = {"m": 1 / 60, "h": 1, "d": 24}


class SLOError(ValueError):
    pass


def hours(duration):
    return int(duration[:-1]) * UNIT_HOURS[duration[-1]]


def load(path):
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    validate(doc)
    return doc


def validate(doc):
    errors = []
    if not isinstance(doc, dict):
        raise SLOError("file must contain a mapping at the top level")
    for key in ("service", "owner", "window_days", "slos"):
        if key not in doc:
            errors.append(f"missing required field '{key}'")
    if errors:
        raise SLOError("; ".join(errors))

    if not NAME_RE.match(str(doc["service"])):
        errors.append("'service' must be lowercase letters, digits and dashes")
    wd = doc["window_days"]
    if not isinstance(wd, int) or not 1 <= wd <= 90:
        errors.append("'window_days' must be a whole number from 1 to 90")
    slos = doc["slos"]
    if not isinstance(slos, list) or not slos:
        raise SLOError("; ".join(errors + ["'slos' must be a non-empty list"]))

    seen = set()
    for i, slo in enumerate(slos):
        where = f"slos[{i}]"
        if not isinstance(slo, dict):
            errors.append(f"{where} must be a mapping")
            continue
        name = slo.get("name")
        if not name or not NAME_RE.match(str(name)):
            errors.append(f"{where}.name is missing or not lowercase-with-dashes")
        elif name in seen:
            errors.append(f"{where}.name '{name}' is duplicated")
        seen.add(name)
        obj = slo.get("objective")
        if not isinstance(obj, (int, float)) or not 0 < obj < 100:
            errors.append(f"{where}.objective must be a number between 0 and 100 (exclusive)")
        sli = slo.get("sli") or {}
        for q in ("good", "total"):
            if not isinstance(sli.get(q), str) or "{{window}}" not in sli[q]:
                errors.append(f"{where}.sli.{q} must be a query containing {{{{window}}}}")
    if errors:
        raise SLOError("; ".join(errors))


def format_duration(total_seconds):
    s = round(total_seconds)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    parts = [f"{v}{u}" for v, u in ((d, "d"), (h, "h"), (m, "m"), (s, "s")) if v]
    return " ".join(parts) or "0s"


def burn_rate(fraction, long_window, window_days):
    return fraction * window_days * 24 / hours(long_window)


def cmd_check(doc):
    print(f"OK: {doc['service']} ({len(doc['slos'])} SLOs, {doc['window_days']}-day window)")


def cmd_budget(doc):
    window_s = doc["window_days"] * 86400
    print(f"Service: {doc['service']}   Window: {doc['window_days']} days\n")
    print(f"{'SLO':<20}{'Objective':>11}{'Budget':>10}{'Allowed downtime':>20}")
    for slo in doc["slos"]:
        budget = 1 - slo["objective"] / 100
        print(f"{slo['name']:<20}{slo['objective']:>10}%{budget:>10.4%}"
              f"{format_duration(window_s * budget):>20}")
    print("\nAlert thresholds (multi-window, multi-burn-rate):")
    for fraction, long_w, short_w, sev in ALERT_POLICY:
        rate = burn_rate(fraction, long_w, doc["window_days"])
        print(f"  {sev:<7} burn rate >= {rate:g} over {long_w} and {short_w} "
              f"({fraction:.0%} of budget in {long_w})")


def record_name(window):
    return f"slo:sli_error:ratio_rate{window}"


def cmd_rules(doc):
    service = doc["service"]
    recording, alerts = [], []
    for slo in doc["slos"]:
        labels = {"service": service, "slo": slo["name"]}
        selector = f'{{service="{service}",slo="{slo["name"]}"}}'
        for w in WINDOWS:
            good = slo["sli"]["good"].replace("{{window}}", w)
            total = slo["sli"]["total"].replace("{{window}}", w)
            recording.append({
                "record": record_name(w),
                "expr": f"1 - (({good}) / ({total}))",
                "labels": dict(labels),
            })
        budget = 1 - slo["objective"] / 100
        for fraction, long_w, short_w, sev in ALERT_POLICY:
            rate = burn_rate(fraction, long_w, doc["window_days"])
            threshold = round(rate * budget, 10)
            alerts.append({
                "alert": f"SLOBurnRate{sev.title()}",
                "expr": (f"{record_name(long_w)}{selector} > {threshold}"
                         f" and {record_name(short_w)}{selector} > {threshold}"),
                "labels": {**labels, "severity": sev,
                           "long_window": long_w, "short_window": short_w},
                "annotations": {
                    "summary": f"{service}/{slo['name']} is burning its error budget "
                               f"{rate:g}x faster than sustainable",
                    "description": f"At this rate {fraction:.0%} of the "
                                   f"{doc['window_days']}-day error budget is consumed "
                                   f"in {long_w}. Objective: {slo['objective']}%.",
                },
            })
    rules = {"groups": [
        {"name": f"{service}-slo-recording", "rules": recording},
        {"name": f"{service}-slo-alerts", "rules": alerts},
    ]}
    print(f"# Generated by tools/slo_tool.py from the SLO file for '{service}'. Do not edit by hand.")
    yaml.safe_dump(rules, sys.stdout, sort_keys=False, width=120)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["check", "budget", "rules"])
    parser.add_argument("file")
    args = parser.parse_args(argv)
    try:
        doc = load(args.file)
    except (OSError, yaml.YAMLError, SLOError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    {"check": cmd_check, "budget": cmd_budget, "rules": cmd_rules}[args.command](doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
