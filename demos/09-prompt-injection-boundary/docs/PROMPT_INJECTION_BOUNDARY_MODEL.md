# Prompt Injection Boundary Model

This demo treats prompt injection as a consequence-boundary problem.

A prompt may influence model output. Maxwell-style control evaluates whether the resulting proposed effect has independent authority. The demo distinguishes three things:

1. **Instruction evidence** — what the user or model said.
2. **Authority context** — who or what is actually permitted to bind downstream systems.
3. **Effect record** — the record created only when policy permits downstream effect.

The key idea:

```text
Model output can be evidence. It is not authority.
```
