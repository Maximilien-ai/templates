# Backlog

## Completed

- [x] Create the `v0.1.0` review release for the `TEMPLATE.md` spec
- [x] Add JSON and Markdown schema artifacts for template validation
- [x] Add repository validation for `template.json` and `TEMPLATE.md` parity
- [x] Add `./setup.sh`, `./lint.sh`, and `./test.sh` for local developer workflows
- [x] Add GitHub Actions CI for pull requests and pushes to `main`
- [x] Add Markdown linting, Python linting, and GitHub Actions linting
- [x] Add `CODEOWNERS` with `@maximilien` as the sole owner
- [x] Add Dependabot for GitHub Actions and toolchain dependency updates
- [x] Add and apply branch protection for `main`
- [x] Update branch protection so admins, including `@maximilien`, can merge without an extra reviewer
- [x] Fix template drift so the repository passes validation checks
- [x] Document validation, CI, and branch protection workflows in the repository docs

## Next Up

- [ ] Review and merge the `chore/template-ci` pull request
- [ ] Verify GitHub Actions checks are green on the PR
- [ ] Cut and publish the `v0.1.1` release from `main`

## Later

- [ ] Consider adding a ruleset if you want bypass allowances for specific non-admin users
- [ ] Consider adding issue and pull request templates
- [ ] Consider adding a formatter or autofix command for Markdown style normalization
