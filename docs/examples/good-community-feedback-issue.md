# Good Community Feedback Issue

## Type

Template submission friction

## Summary

The current submission flow is clear overall, but contributors can still miss the expected `testedWith` metadata because the examples in older templates do not show it yet.

## What I Tried

- Read `README.md`
- Followed `docs/CONTRIBUTING.md`
- Ran `./setup.sh`, `./format.sh`, `./lint.sh`, and `./test.sh`

## Where I Got Stuck

- I was not sure whether `testedWith` belonged in both `template.json` and `TEMPLATE.md`
- I was not sure what version format was expected for platform entries

## Suggested Improvement

- Add one fully worked example template in a future release that includes `testedWith`
- Keep the PR and issue fixtures linked from `README.md`

## Environment

- Platform tested: OpenClaw `0.9.0`
- Repository version: `v0.1.3`
