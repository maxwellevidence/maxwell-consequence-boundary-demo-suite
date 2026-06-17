from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PolicyDecision:
    outcome: str
    lifecycle_state: str
    reason_code: str
    effect_permitted: bool
    explanation: str
    review_route: str | None = None


def load_policy(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Policy file must contain a mapping: {path}")
    return data


def _contains_prompt_injection_marker(case: dict[str, Any], policy: dict[str, Any]) -> bool:
    text = str(case.get("proposed_instruction", "")).lower()
    markers = policy.get("prompt_injection_markers") or []
    return any(str(marker).lower() in text for marker in markers)


def evaluate_policy(
    case: dict[str, Any],
    evidence_bundle: dict[str, Any],
    authority_context: dict[str, Any],
    policy: dict[str, Any],
) -> PolicyDecision:
    """Evaluate the public demo policy.

    This function is intentionally simple and public-safe. Real demos should replace
    or extend it with demo-specific policy rules while preserving the same output shape.
    """
    required_fields = policy.get("required_fields") or []
    missing = [field for field in required_fields if field not in case]
    if missing:
        return PolicyDecision(
            outcome="block",
            lifecycle_state="EFFECT_SUPPRESSED",
            reason_code="EFFECT_GATE_MALFORMED_INPUT",
            effect_permitted=False,
            explanation=f"Required fields missing: {', '.join(missing)}.",
        )

    if _contains_prompt_injection_marker(case, policy):
        return PolicyDecision(
            outcome="block",
            lifecycle_state="EFFECT_SUPPRESSED",
            reason_code="EFFECT_GATE_PROMPT_INJECTION_SUPPRESSED",
            effect_permitted=False,
            explanation="Instruction text attempted to create or bypass authority. Output is not authority.",
        )

    if evidence_bundle.get("evidence_count", 0) <= 0:
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="REVIEW_ROUTED",
            reason_code="EFFECT_GATE_REQUIRED_EVIDENCE_MISSING",
            effect_permitted=False,
            explanation="Required evidence references are missing.",
            review_route=policy.get("review_route", "demo_review_queue"),
        )

    if not authority_context.get("authority_present") or not authority_context.get("can_execute"):
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="REVIEW_ROUTED",
            reason_code="EFFECT_GATE_AUTHORITY_CONTEXT_MISSING",
            effect_permitted=False,
            explanation="Authority context is missing or cannot execute the requested effect.",
            review_route=policy.get("review_route", "demo_review_queue"),
        )

    target_scope = authority_context.get("target_scope")
    allowed_scopes = authority_context.get("allowed_scopes") or []
    if target_scope not in allowed_scopes:
        return PolicyDecision(
            outcome="block",
            lifecycle_state="EFFECT_SUPPRESSED",
            reason_code="EFFECT_GATE_SCOPE_NOT_AUTHORIZED",
            effect_permitted=False,
            explanation="The requested target scope is outside the actor's claimed authority.",
        )

    risk_level = str(case.get("risk_level", "")).lower()
    review_levels = set(policy.get("review_required_risk_levels") or [])
    if risk_level in review_levels:
        return PolicyDecision(
            outcome="hold",
            lifecycle_state="REVIEW_ROUTED",
            reason_code="EFFECT_GATE_REVIEW_REQUIRED_HIGH_RISK",
            effect_permitted=False,
            explanation="The action is high enough risk to require review before downstream effect.",
            review_route=policy.get("review_route", "demo_review_queue"),
        )

    allowed_levels = set(policy.get("allowed_risk_levels") or [])
    if risk_level in allowed_levels:
        return PolicyDecision(
            outcome="allow",
            lifecycle_state="EFFECT_COMMITTED",
            reason_code="EFFECT_GATE_EFFECT_PERMITTED",
            effect_permitted=True,
            explanation="Evidence and authority were sufficient for this public demo policy.",
        )

    return PolicyDecision(
        outcome="hold",
        lifecycle_state="REVIEW_ROUTED",
        reason_code="EFFECT_GATE_REVIEW_REQUIRED_HIGH_RISK",
        effect_permitted=False,
        explanation="Risk level is not explicitly auto-allowed by the demo policy.",
        review_route=policy.get("review_route", "demo_review_queue"),
    )
