# Good Template Submission PR

## Summary

Adds a new `customer-success-team` template for teams that manage onboarding, renewals, and escalation routing.

## What Is Included

- Category: `business`
- Tags: `customer-success`, `renewals`, `support-handoff`
- Agents: customer-success-manager, onboarding-specialist, renewal-manager
- Workflows: kickoff, onboarding-review, renewal-risk-check, escalation-handoff

## Tested With

- OpenClaw `0.9.0`
- ClawMax `1.4.2`

## Validation

- Ran `./setup.sh`
- Ran `./format.sh`
- Ran `./lint.sh`
- Ran `./test.sh`

## Notes For Reviewers

- `template.json` and `TEMPLATE.md` are kept in sync
- No external workflow template dependency was added
- The kickoff workflow includes all project-specific parameters that must be filled in at import time
