# Multiagent Team Templates

> **Status:** v0.1.0 review release — TEMPLATE.md spec is ready for review and feedback

Organization templates for deploying multiagent teams. Each template defines agents, communication channels, workflows, and a kickoff sequence.

## Tested With

- [OpenClaw](https://openclaw.ai) — open-source multiagent CLI
- [ClawMax](https://clawmax.ai) — multiagent orchestration platform

## Structure

```
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

| Category | Template | Agents | Workflows |
|----------|----------|--------|-----------|
| Business | Sales Team | 4 | 4 |
| Business | HR Team | 4 | 4 |
| Business | Support Team | 4 | 4 |
| Business | Legal Team | 3 | 4 |
| Business | Marketing Team | 4 | 4 |
| Business | Convenience Store | 3 | 4 |
| Business | Specialty Retailer | 4 | 4 |
| Technical | Dev Team | 4 | 5 |
| Technical | Data Team | 4 | 4 |
| Technical | RAG Team | 5 | 6 |
| Technical | Engineering Team | 4 | 5 |
| Personal | Student Research | 4 | 4 |
| Personal | Technical Writing | 4 | 5 |

All templates include:
- Kickoff workflow with user-fillable Project Configuration
- DAG dependencies between workflows
- GitHub coordination skills (where applicable)
- Category tags for filtering

## Contributing

Contributions welcome. Please follow the TEMPLATE.md format and include both `.md` and `.json` versions.

If you have a template pattern or example to contribute, open a PR and submit it for review.

## License

MIT
