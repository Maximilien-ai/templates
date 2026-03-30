# Changelog

## v0.1.7 - 2026-03-30

README clarification.

- Clarifies that ClawMax originated the current spec, workflows, and templates
- Notes that this repository is currently syncing ClawMax-derived templates while the long-term plan is to make this repo the upstream source

## v0.1.6 - 2026-03-30

Template source-of-truth sync.

- Syncs the organization templates in this repo to the current ClawMax template set
- Keeps verified `testedWith` metadata for the `small-startup-team` and `technical-writing` examples
- Repairs two source inconsistencies needed for local parity validation while tracking the upstream ClawMax follow-up separately

## v0.1.5 - 2026-03-29

Issue-template and CI follow-up.

- Adds a template-guidance issue form and a direct contribution-guidance link in the New Issue flow
- Updates CI to provision Go 1.24 so `actionlint` installs cleanly again
- Improves `./setup.sh` messaging and fallback behavior when local Go is too old for the current `actionlint` release

## v0.1.4 - 2026-03-29

Dependency refresh follow-up.

- Picks up the merged Dependabot updates for GitHub Actions, Node tooling, and Python tooling
- Fixes `./setup.sh` so it refreshes repo-local dependencies when pinned versions change instead of only when binaries are missing

## v0.1.3 - 2026-03-29

Contributor guidance and submission example improvements.

- Adds `docs/CONTRIBUTING.md` with submission expectations and local dev/test workflow
- Adds example good-submission fixtures for pull requests and community feedback issues
- Adds optional `testedWith` schema and validator checks for explicit platform/version metadata
- Links the new guidance and examples from the repository README

## v0.1.2 - 2026-03-29

Community submission and formatting improvements.

- Adds issue and pull request templates for bugs, suggestions, spec changes, and template submissions
- Adds `./format.sh` and pinned Prettier support for Markdown normalization
- Documents contributor expectations for template goal, category, tags, included agents and workflows, workflow dependency submissions, and tested OpenClaw or ClawMax versions
- Prepares the repository for wider community submissions and feedback

## v0.1.1 - 2026-03-29

Repository quality gates, tooling, and governance updates.

- Adds CI for pull requests and pushes to `main`
- Adds schema-backed validation for `template.json` and `TEMPLATE.md`
- Adds local developer entrypoints: `./setup.sh`, `./lint.sh`, and `./test.sh`
- Adds Markdown linting, Python script linting, and GitHub Actions linting
- Adds `CODEOWNERS` with `@maximilien` as the current sole owner
- Adds Dependabot for GitHub Actions, npm, and pip toolchain updates
- Adds branch protection policy and updates it so admins can merge without an additional reviewer
- Brings template parity checks online and fixes out-of-sync Markdown templates

## v0.1.0 - 2026-03-29

TEMPLATE.md spec is ready for review and feedback.

- Publishes the initial TEMPLATE.md specification for multiagent team templates
- Includes multiple example templates across business, technical, and personal categories
- Invites feedback on the format before further stabilization
- Welcomes community submissions of additional examples
