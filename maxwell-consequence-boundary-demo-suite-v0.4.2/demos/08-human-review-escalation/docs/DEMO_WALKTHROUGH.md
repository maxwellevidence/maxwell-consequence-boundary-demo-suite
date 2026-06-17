# Demo Walkthrough

Run:

```bash
make demo
make verify
```

Then inspect `artifacts/runs/`.

## Case 01: Hold missing evidence

The original action is reviewable but lacks the required risk assessment. Maxwell creates a review ticket and does not create an authorized effect record.

## Case 02: Reviewer adds evidence

A valid operations reviewer adds the missing risk assessment and approves within the original scope. Maxwell creates `authorized_effect_record.json`.

## Case 03: Reviewer lacks authority

A junior reviewer attempts to approve the action. Maxwell records the review attempt, rejects the review, and suppresses downstream effect.

## Case 04: Authorized reviewer approves

A high-risk customer-credit action requires compliance review. A compliance reviewer supplies the remaining high-risk evidence and approval. Maxwell creates the authorized effect record.

## Case 05: Review fails blocked

The proposed action contains injected override language. Maxwell preserves the attempted override as evidence and does not let review convert it into effect.

## Case 06: Review attempts scope expansion

The original proposal is a support-case update. Review tries to convert it into a customer-credit effect. Maxwell blocks the scope expansion.
