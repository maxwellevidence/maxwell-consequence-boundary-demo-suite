"""Public-safe Maxwell Effect Gate decision data structures.

The v0.3.0 public preview removes the old authority-label compatibility path.
Reviewer-facing decisions are derived by ``policy_engine.evaluate_policy`` from
an action proposal, evidence bundle, and authority context.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class GateDecision:
    decision: str
    reason_codes: List[str]
    downstream_effect_allowed: bool
