# Demo Walkthrough

Run:

```bash
make demo
make verify
```

The CLI runs six synthetic cases.

## 01_complete_eligibility_evidence

A benefits caseworker proposes a non-adverse eligibility approval. Evidence is complete, the case record is consistent, and the actor has authority to bind a non-adverse effect.

Expected result:

```text
determination_effect_committed
```

A `determination_effect_record.json` is created.

## 02_missing_required_document

The proposed approval is missing required income evidence.

Expected result:

```text
case_review_routed
```

No determination effect is created. A `case_review_ticket.json` is created.

## 03_inconsistent_case_record

The proposed approval has a complete set of references, but the case record is internally inconsistent.

Expected result:

```text
case_review_routed
```

No determination effect is created. A review ticket preserves the reason.

## 04_unauthorized_auto_denial

An automated case assistant attempts to bind an adverse denial and the AI output claims final authority.

Expected result:

```text
determination_effect_suppressed
```

No determination effect is created. A suppression notice is written.

## 05_review_required_due_process

A caseworker proposes an adverse eligibility denial. Evidence and notice context are present, but authorized human review is missing.

Expected result:

```text
due_process_review_routed
```

No determination effect is created. A `due_process_review_ticket.json` is created.

## 06_authorized_reviewed_determination_effect

An adverse benefit reduction has complete evidence, notice, appeal-rights context, and authorized senior review.

Expected result:

```text
determination_effect_committed
```

A `determination_effect_record.json` is created.
