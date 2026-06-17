"""Workflow profiling metrics builder for the public Maxwell Effect Gate proof."""

from typing import Any, Dict


def build_workflow_profiling_metrics(case: str) -> Dict[str, Any]:
    """Build public-safe workflow profiling metrics.

    These are illustrative metrics for the public proof. They are not
    performance benchmarks, production telemetry, or NVIDIA validation data.
    """

    return {
        "run_case": case,
        "metrics_scope": "public_safe_demo_metrics",
        "workflow_type": "ai_assisted_cve_incident_research",
        "bounded_effect": "change_control_record_creation",
        "artifact_count_expected_minimum": 11,
        "model_latency_ms": None,
        "tool_latency_ms": None,
        "gate_evaluation_latency_ms": None,
        "external_api_calls_replayed": False,
        "model_calls_replayed": False,
        "notes": [
            "Metrics are illustrative placeholders for the public proof.",
            "This repository does not claim production performance.",
            "This repository does not claim deterministic replay of model calls or external tool state."
        ]
    }
