# Multiagent Team Templates

> **Status:** v0.1.2 review release — template submission tooling is ready for community review and feedback

Organization templates for deploying multiagent teams. Each template defines agents, communication channels, workflows, and a kickoff sequence.

## Tested With

- [OpenClaw](https://openclaw.ai) — open-source multiagent CLI
- [ClawMax](https://clawmax.ai) — multiagent orchestration platform

## Structure

```text
spec/                          # Format specification
  template-spec.md             # TEMPLATE.md format spec
templates/                     # Organization templates
  dev-team/
    TEMPLATE.md                # Lean markdown format
    template.json              # JSON format (equivalent)
  support-team/
    TEMPLATE.md
    template.json
  ...
```

## Format

Templates can be defined as `TEMPLATE.md` (markdown) or `template.json` (JSON). Both are equivalent — tools auto-detect the format.

**TEMPLATE.md** uses minimal YAML frontmatter + structured markdown body:

```yaml
---
name: Dev Team
type: organization
version: "1.0.0"
category: technical
author: ClawMax Team
tags: [engineering, software]
---

A multiagent software development team.

## Agents

| id | name | role | tags | skills |
|----|------|------|------|--------|
| tech-lead | Tech Lead | Technical leadership | lead | github |
| engineer | Software Engineer | Feature development | engineering | github |

## Communities

- **Dev Team** — All engineering coordination

## Groups

- **Engineering** — Code review and development (Dev Team)
- **QA** — Testing and quality (Dev Team)

## Workflows

### Team Kickoff
- **Schedule:** manual
- **Mode:** managed (owner: tech-lead)
- **Targets:** agents: tech-lead

# Dev Team Kickoff
...
```

See [spec/template-spec.md](spec/template-spec.md) for the full specification.

## Templates

| Category  | Template           | Agents | Workflows |
| --------- | ------------------ | ------ | --------- |
| Business  | Sales Team         | 4      | 4         |
| Business  | HR Team            | 4      | 4         |
| Business  | Support Team       | 4      | 4         |
| Business  | Legal Team         | 3      | 4         |
| Business  | Marketing Team     | 4      | 4         |
| Business  | Convenience Store  | 3      | 4         |
| Business  | Specialty Retailer | 4      | 4         |
| Technical | Dev Team           | 4      | 5         |
| Technical | Data Team          | 4      | 4         |
| Technical | RAG Team           | 5      | 6         |
| Technical | Engineering Team   | 4      | 5         |
| Personal  | Student Research   | 4      | 4         |
| Personal  | Technical Writing  | 4      | 5         |

All templates include:

- Kickoff workflow with user-fillable Project Configuration
- DAG dependencies between workflows
- GitHub coordination skills (where applicable)
- Category tags for filtering

## Contributing

Contributions welcome. Please follow the `TEMPLATE.md` format and include both `.md` and `.json` versions.

For community submissions:

- describe the template goal clearly
- include the template category and tags
- list the included agents and workflows
- state which OpenClaw and/or ClawMax version you tested with
- include ClawMax-style agent templates or actual OpenClaw agent files when relevant
- submit reusable workflow templates to `https://github.com/Maximilien-ai/workflows` first or at the same time if your template depends on them

Use the PR template when submitting new templates or spec changes.

## Validation

- JSON templates are defined by [schemas/template.schema.json](schemas/template.schema.json)
- `TEMPLATE.md` documents are parsed and checked against [schemas/template-markdown.schema.json](schemas/template-markdown.schema.json)
- Run `python3 scripts/validate_templates.py` to validate all templates locally
- Run `./format.sh` to normalize Markdown before linting

## CI

GitHub Actions runs on pull requests and pushes to `main` to:

- lint Markdown
- lint GitHub Actions and repository Python scripts
- validate every `templates/*/template.json`
- validate every `templates/*/TEMPLATE.md`
- verify that each template directory has both formats and that key metadata stays in sync

For local use, run `./setup.sh`, then `./format.sh`, `./lint.sh`, and `./test.sh`.

## Dev/Test

Local developer workflow:

- `./setup.sh` installs the pinned repo-local tooling used by formatting and linting
- `./format.sh` normalizes Markdown formatting before review or submission
- `./lint.sh` runs Markdown linting, Python script checks, and GitHub Actions linting
- `./test.sh` validates every template directory, including `template.json` and `TEMPLATE.md` parity

Recommended flow before opening a PR:

1. Run `./setup.sh`
2. Run `./format.sh`
3. Run `./lint.sh`
4. Run `./test.sh`

## Branch Protection

The desired protection policy for `main` lives in [`.github/branch-protection-main.json`](.github/branch-protection-main.json).

After authenticating GitHub CLI with admin access to the repo, apply it with:

`./scripts/apply_branch_protection.sh`

## License

MIT
