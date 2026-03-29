# Contributing

Use this repository when you want to submit a new team template, improve the spec, or tighten validation and docs.

## Before You Open A PR

- Run `./setup.sh`
- Run `./format.sh`
- Run `./lint.sh`
- Run `./test.sh`
- Confirm every template directory you touched still contains both `template.json` and `TEMPLATE.md`

## Template Submission Checklist

- State the template goal in one clear sentence
- Include the category and meaningful tags
- Keep `template.json` and `TEMPLATE.md` aligned for top-level metadata and agent/community/group structure
- Include `testedWith` platform/version entries when you verified the template in OpenClaw, ClawMax, or both
- List the included agents and workflows in the PR description
- Mention any reusable workflow dependencies and submit them to `https://github.com/Maximilien-ai/workflows` if needed
- Include agent template files only when the template genuinely depends on them

## Submission Notes

- Use the repository pull request template for template submissions and spec changes
- Use the community feedback issue template for bugs, friction reports, and improvement suggestions
- If you changed formatting-sensitive Markdown, run `./format.sh` before your final test pass

## Good Examples

- [good-template-submission-pr.md](examples/good-template-submission-pr.md)
- [good-community-feedback-issue.md](examples/good-community-feedback-issue.md)
