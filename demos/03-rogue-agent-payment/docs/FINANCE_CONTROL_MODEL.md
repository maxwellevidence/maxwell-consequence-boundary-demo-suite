# Finance Control Model

This demo is not a payment product. It is a public-safe model of a finance consequence boundary.

The demo separates five concepts that are often collapsed in AI demos:

1. **Recommendation** — the AI proposes payment.
2. **Evidence** — invoice, purchase order, vendor record, and receiving evidence are referenced.
3. **Authority** — the claimed approver and their payment scope are normalized.
4. **Reviewability** — some cases are routed to controlled review rather than committed.
5. **Effect** — a synthetic payment effect record is created only when policy permits.

The point is not that this policy is complete. The point is that payment effect is not created merely because an AI-generated instruction says it should be.
