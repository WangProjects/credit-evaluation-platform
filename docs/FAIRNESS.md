## Fairness (engineering notes)

This repo treats fairness as a **measured, monitored property**. The default posture is:

- do **not** use sensitive attributes for prediction by default
- optionally collect sensitive attributes for **monitoring and auditing** where lawful and consented

### Included metrics (minimal)

In `ice.fairness.metrics`:

- selection rate
- disparate impact ratio (selection_rate_a / selection_rate_b)
- true positive rate by group (when outcomes are available)
- false positive rate by group

### Practical deployment advice

- define a **policy** for which attributes are collected, why, and how long retained
- define thresholds for alerting (e.g., DI < 0.8 triggers review)
- document how to handle small-sample instability


