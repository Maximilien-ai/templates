#!/usr/bin/env python3
"""Validate JSON and Markdown templates in this repository."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "templates"
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
KEBAB_RE = re.compile(r"^[a-z][a-z0-9-]*$")
COMMUNITY_BULLET_RE = re.compile(r"^- \*\*(.+?)\*\* \u2014 (.+)$")
GROUP_BULLET_RE = re.compile(r"^- \*\*(.+?)\*\* \u2014 (.+?)(?: \((.+)\))?$")
METADATA_RE = re.compile(r"^- \*\*(.+?):\*\* (.+)$")
VALID_TEMPLATE_TYPES = {"organization", "agent"}
VALID_CATEGORIES = {"business", "technical", "personal", "science", "travel", "hobbies", "family"}
VALID_EXECUTION_MODES = {"automated", "managed"}
VALID_WORKFLOW_TYPES = {"once", "recurring", "conditional"}
VALID_WORKFLOW_SCALING = {"singleton", "parallel"}


class ValidationError(Exception):
    pass


@dataclass
class MarkdownTemplate:
    metadata: dict[str, Any]
    description: str
    agents: list[dict[str, Any]]
    communities: list[dict[str, Any]]
    groups: list[dict[str, Any]]
    workflows: list[dict[str, Any]]


def fail(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        return split_csv(value[1:-1])
    if value.isdigit():
        return int(value)
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def parse_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValidationError("missing opening YAML frontmatter delimiter")

    try:
        _, rest = text.split("---\n", 1)
        frontmatter_text, body = rest.split("\n---\n", 1)
    except ValueError as exc:
        raise ValidationError("missing closing YAML frontmatter delimiter") from exc

    lines = frontmatter_text.splitlines()
    data: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith(" "):
            raise ValidationError(f"unexpected indentation in frontmatter: {line!r}")
        if ":" not in line:
            raise ValidationError(f"invalid frontmatter line: {line!r}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value:
            data[key] = parse_scalar(raw_value)
            i += 1
            continue

        block_lines: list[str] = []
        i += 1
        while i < len(lines) and (not lines[i] or lines[i].startswith("  ")):
            if lines[i]:
                block_lines.append(lines[i])
            i += 1
        data[key] = parse_frontmatter_block(block_lines, path, key)

    return data, body.lstrip("\n")


def parse_frontmatter_block(lines: list[str], path: Path, key: str) -> Any:
    if not lines:
        return []

    items: list[Any] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("  - "):
            raise ValidationError(
                f"unsupported frontmatter block for {key!r} in {path.relative_to(ROOT)}"
            )
        item_text = line[4:].strip()
        if ":" in item_text:
            item_key, item_value = item_text.split(":", 1)
            item: dict[str, Any] = {item_key.strip(): parse_scalar(item_value.strip())}
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                nested = lines[i].strip()
                if ":" not in nested:
                    raise ValidationError(
                        f"invalid nested frontmatter line for {key!r}: {nested!r}"
                    )
                nested_key, nested_value = nested.split(":", 1)
                item[nested_key.strip()] = parse_scalar(nested_value.strip())
                i += 1
            items.append(item)
            continue

        items.append(parse_scalar(item_text))
        i += 1

    return items


def find_section_start(lines: list[str], title: str) -> int:
    for idx, line in enumerate(lines):
        if line.strip() == f"## {title}":
            return idx
    raise ValidationError(f"missing '## {title}' section")


def split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        raise ValidationError(f"invalid table row: {line!r}")
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def parse_agents_section(lines: list[str]) -> list[dict[str, Any]]:
    content = [line for line in lines if line.strip()]
    if len(content) < 3:
        raise ValidationError("agents section is missing the table")

    headers = split_table_row(content[0])
    if headers not in (
        ["id", "name", "role", "tags", "skills"],
        ["id", "name", "role", "tags", "skills", "template"],
    ):
        raise ValidationError("agents table header does not match the spec")

    agents: list[dict[str, Any]] = []
    for row in content[2:]:
        values = split_table_row(row)
        if len(values) != len(headers):
            raise ValidationError(f"agents row has {len(values)} columns, expected {len(headers)}")
        item = dict(zip(headers, values))
        agent = {
            "id": item["id"],
            "name": item["name"],
            "role": item["role"],
            "tags": split_csv(item["tags"]),
            "skills": split_csv(item["skills"]),
        }
        if "template" in item and item["template"]:
            agent["template"] = item["template"]
        agents.append(agent)
    return agents


def parse_bullet_section(lines: list[str], pattern: re.Pattern[str], kind: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        match = pattern.match(line.strip())
        if not match:
            raise ValidationError(f"invalid {kind} line: {line!r}")
        groups = match.groups()
        item = {"name": groups[0].strip(), "description": groups[1].strip()}
        if len(groups) > 2 and groups[2]:
            item["community"] = groups[2].strip()
        items.append(item)
    return items


def parse_targets(value: str) -> dict[str, list[str]]:
    targets = {"agents": [], "groups": [], "tags": [], "communities": []}
    for segment in [segment.strip() for segment in value.split(";") if segment.strip()]:
        if ":" not in segment:
            raise ValidationError(f"invalid targets segment: {segment!r}")
        key, raw_items = segment.split(":", 1)
        key = key.strip().lower()
        if key not in targets:
            raise ValidationError(f"unsupported targets key: {key!r}")
        targets[key] = split_csv(raw_items)
    return targets


def parse_mode(value: str) -> dict[str, Any]:
    lowered = value.strip().lower()
    if lowered == "automated":
        return {"executionMode": "automated"}
    if lowered == "managed":
        return {"executionMode": "managed"}

    match = re.fullmatch(r"managed\s*\(owner:\s*([a-z][a-z0-9-]*)\s*\)", lowered)
    if match:
        return {"executionMode": "managed", "owner": match.group(1)}

    raise ValidationError(f"invalid workflow mode: {value!r}")


def parse_workflows_section(lines: list[str]) -> list[dict[str, Any]]:
    def is_workflow_heading(index: int) -> bool:
        if not lines[index].startswith("### "):
            return False
        probe = index + 1
        while probe < len(lines) and not lines[probe].strip():
            probe += 1
        return probe < len(lines) and METADATA_RE.match(lines[probe].strip()) is not None

    workflows: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if not is_workflow_heading(i):
            raise ValidationError(f"invalid workflow heading: {line!r}")
        workflow_name = line[4:].strip()
        i += 1

        while i < len(lines) and not lines[i].strip():
            i += 1

        metadata: dict[str, Any] = {}
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue
            metadata_match = METADATA_RE.match(lines[i].strip())
            if not metadata_match:
                break
            meta_key, meta_value = metadata_match.groups()
            key = meta_key.strip().lower().replace(" ", "")
            if key == "schedule":
                metadata["schedule"] = meta_value.strip()
            elif key == "mode":
                metadata.update(parse_mode(meta_value))
            elif key == "targets":
                metadata["targets"] = parse_targets(meta_value)
            elif key == "owner":
                metadata["owner"] = meta_value.strip()
            elif key == "dependson":
                metadata["dependsOn"] = split_csv(meta_value)
            elif key == "template":
                metadata["template"] = meta_value.strip()
            else:
                raise ValidationError(f"unsupported workflow metadata key: {meta_key!r}")
            i += 1

        content_lines: list[str] = []
        while i < len(lines) and not is_workflow_heading(i):
            content_lines.append(lines[i])
            i += 1
        content = "\n".join(content_lines).strip()
        if not content:
            raise ValidationError(f"workflow {workflow_name!r} is missing content")

        workflows.append(
            {
                "name": workflow_name,
                "schedule": metadata.get("schedule"),
                "executionMode": metadata.get("executionMode"),
                "targets": metadata.get("targets", {"agents": [], "groups": [], "tags": [], "communities": []}),
                "owner": metadata.get("owner"),
                "dependsOn": metadata.get("dependsOn", []),
                "template": metadata.get("template"),
                "content": content,
            }
        )

    return workflows


def parse_markdown_template(path: Path) -> MarkdownTemplate:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text, path)
    lines = body.splitlines()

    agents_start = find_section_start(lines, "Agents")
    communities_start = find_section_start(lines, "Communities")
    groups_start = find_section_start(lines, "Groups")
    workflows_start = find_section_start(lines, "Workflows")

    if not (agents_start < communities_start < groups_start < workflows_start):
        raise ValidationError("top-level sections must appear in the order Agents, Communities, Groups, Workflows")

    agents_end = communities_start
    communities_end = groups_start
    groups_end = workflows_start
    workflows_end = len(lines)

    description = "\n".join(lines[:agents_start]).strip()
    if not description:
        raise ValidationError("missing description before '## Agents'")

    agents = parse_agents_section(lines[agents_start + 1 : agents_end])
    communities = parse_bullet_section(
        lines[communities_start + 1 : communities_end], COMMUNITY_BULLET_RE, "community"
    )
    groups = parse_bullet_section(lines[groups_start + 1 : groups_end], GROUP_BULLET_RE, "group")
    workflows = parse_workflows_section(lines[workflows_start + 1 : workflows_end])

    return MarkdownTemplate(
        metadata=metadata,
        description=description,
        agents=agents,
        communities=communities,
        groups=groups,
        workflows=workflows,
    )


def expect_nonempty_string(errors: list[str], path: Path, value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(errors, path, f"{label} must be a non-empty string")


def expect_string_list(errors: list[str], path: Path, value: Any, label: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        fail(errors, path, f"{label} must be a list of non-empty strings")


def validate_tested_with(errors: list[str], path: Path, value: Any, label: str) -> None:
    if not isinstance(value, list):
        fail(errors, path, f"{label} must be a list")
        return

    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        if not isinstance(item, dict):
            fail(errors, path, f"{item_label} must be an object")
            continue
        expect_nonempty_string(errors, path, item.get("platform"), f"{item_label}.platform")
        expect_nonempty_string(errors, path, item.get("version"), f"{item_label}.version")


def validate_core_template(data: dict[str, Any], path: Path, errors: list[str]) -> None:
    expect_nonempty_string(errors, path, data.get("name"), "name")
    template_type = data.get("type")
    if template_type not in VALID_TEMPLATE_TYPES:
        fail(errors, path, "type must be 'organization' or 'agent'")

    version = data.get("version")
    if version is not None and (not isinstance(version, str) or not SEMVER_RE.match(version)):
        fail(errors, path, "version must be semantic versioning (X.Y.Z)")

    category = data.get("category")
    if category is not None and category not in VALID_CATEGORIES:
        fail(errors, path, "category must be one of business, technical, personal, science, travel, hobbies, family")

    if "description" in data:
        expect_nonempty_string(errors, path, data.get("description"), "description")
    if "author" in data:
        expect_nonempty_string(errors, path, data.get("author"), "author")
    if "tags" in data:
        expect_string_list(errors, path, data.get("tags"), "tags")
    if "testedWith" in data:
        validate_tested_with(errors, path, data.get("testedWith"), "testedWith")

    agents = data.get("agents")
    if not isinstance(agents, list) or not agents:
        fail(errors, path, "agents must be a non-empty list")
        agents = []

    agent_ids: set[str] = set()
    for index, agent in enumerate(agents):
        label = f"agents[{index}]"
        if not isinstance(agent, dict):
            fail(errors, path, f"{label} must be an object")
            continue
        agent_id = agent.get("id")
        if not isinstance(agent_id, str) or not KEBAB_RE.match(agent_id):
            fail(errors, path, f"{label}.id must be kebab-case")
        elif agent_id in agent_ids:
            fail(errors, path, f"duplicate agent id {agent_id!r}")
        else:
            agent_ids.add(agent_id)
        expect_nonempty_string(errors, path, agent.get("name"), f"{label}.name")
        expect_nonempty_string(errors, path, agent.get("role"), f"{label}.role")
        for field in ("tags", "skills", "communities", "groups"):
            if field in agent:
                expect_string_list(errors, path, agent.get(field), f"{label}.{field}")
        if "template" in agent and agent["template"] is not None:
            expect_nonempty_string(errors, path, agent.get("template"), f"{label}.template")

    communities = data.get("communities", [])
    community_names: set[str] = set()
    if not isinstance(communities, list):
        fail(errors, path, "communities must be a list")
        communities = []
    for index, community in enumerate(communities):
        label = f"communities[{index}]"
        if not isinstance(community, dict):
            fail(errors, path, f"{label} must be an object")
            continue
        community_name = community.get("name")
        expect_nonempty_string(errors, path, community_name, f"{label}.name")
        expect_nonempty_string(errors, path, community.get("description"), f"{label}.description")
        if isinstance(community_name, str):
            if community_name in community_names:
                fail(errors, path, f"duplicate community name {community_name!r}")
            else:
                community_names.add(community_name)
        for field in ("tags", "channels"):
            if field in community:
                expect_string_list(errors, path, community.get(field), f"{label}.{field}")

    groups = data.get("groups", [])
    group_names: set[str] = set()
    if not isinstance(groups, list):
        fail(errors, path, "groups must be a list")
        groups = []
    for index, group in enumerate(groups):
        label = f"groups[{index}]"
        if not isinstance(group, dict):
            fail(errors, path, f"{label} must be an object")
            continue
        group_name = group.get("name")
        expect_nonempty_string(errors, path, group_name, f"{label}.name")
        expect_nonempty_string(errors, path, group.get("description"), f"{label}.description")
        if isinstance(group_name, str):
            if group_name in group_names:
                fail(errors, path, f"duplicate group name {group_name!r}")
            else:
                group_names.add(group_name)
        community = group.get("community")
        if community is not None:
            expect_nonempty_string(errors, path, community, f"{label}.community")
            if isinstance(community, str) and community not in community_names:
                fail(errors, path, f"{label}.community references missing community {community!r}")
        for field in ("tags", "channels"):
            if field in group:
                expect_string_list(errors, path, group.get(field), f"{label}.{field}")

    parameter_agent_ids = set()
    parameters = data.get("parameters", [])
    if parameters is not None:
        if not isinstance(parameters, list):
            fail(errors, path, "parameters must be a list")
            parameters = []
        for index, parameter in enumerate(parameters):
            label = f"parameters[{index}]"
            if not isinstance(parameter, dict):
                fail(errors, path, f"{label} must be an object")
                continue
            agent_id = parameter.get("agentId")
            label_value = parameter.get("label")
            default = parameter.get("default")
            minimum = parameter.get("min")
            maximum = parameter.get("max")
            if not isinstance(agent_id, str) or not KEBAB_RE.match(agent_id):
                fail(errors, path, f"{label}.agentId must be kebab-case")
            else:
                parameter_agent_ids.add(agent_id)
            expect_nonempty_string(errors, path, label_value, f"{label}.label")
            for numeric_field, numeric_value in (
                ("default", default),
                ("min", minimum),
                ("max", maximum),
            ):
                if not isinstance(numeric_value, int):
                    fail(errors, path, f"{label}.{numeric_field} must be an integer")
            if all(isinstance(item, int) for item in (default, minimum, maximum)):
                if minimum > default or default > maximum:
                    fail(errors, path, f"{label} must satisfy min <= default <= max")

    missing_parameter_agents = sorted(parameter_agent_ids - agent_ids)
    for agent_id in missing_parameter_agents:
        fail(errors, path, f"parameter references missing agent {agent_id!r}")

    for index, agent in enumerate(agents):
        for community in agent.get("communities", []):
            if community not in community_names:
                fail(errors, path, f"agents[{index}].communities references missing community {community!r}")
        for group in agent.get("groups", []):
            if group not in group_names:
                fail(errors, path, f"agents[{index}].groups references missing group {group!r}")

    workflows = data.get("workflows", [])
    workflow_ids: set[str] = set()
    if template_type == "organization" and (not isinstance(workflows, list) or not workflows):
        fail(errors, path, "workflows must be a non-empty list for organization templates")
        workflows = []
    elif not isinstance(workflows, list):
        fail(errors, path, "workflows must be a list")
        workflows = []

    for index, workflow in enumerate(workflows):
        label = f"workflows[{index}]"
        if not isinstance(workflow, dict):
            fail(errors, path, f"{label} must be an object")
            continue

        workflow_id = workflow.get("id")
        if workflow_id is not None:
            if not isinstance(workflow_id, str) or not KEBAB_RE.match(workflow_id):
                fail(errors, path, f"{label}.id must be kebab-case")
            elif workflow_id in workflow_ids:
                fail(errors, path, f"duplicate workflow id {workflow_id!r}")
            else:
                workflow_ids.add(workflow_id)
        expect_nonempty_string(errors, path, workflow.get("name"), f"{label}.name")
        if "description" in workflow:
            expect_nonempty_string(errors, path, workflow.get("description"), f"{label}.description")
        expect_nonempty_string(errors, path, workflow.get("schedule"), f"{label}.schedule")
        if "enabled" in workflow and not isinstance(workflow.get("enabled"), bool):
            fail(errors, path, f"{label}.enabled must be a boolean")
        mode = workflow.get("executionMode")
        if mode is not None and mode not in VALID_EXECUTION_MODES:
            fail(errors, path, f"{label}.executionMode must be automated or managed")
        if "content" in workflow:
            expect_nonempty_string(errors, path, workflow.get("content"), f"{label}.content")
        workflow_type = workflow.get("type")
        if workflow_type is not None and workflow_type not in VALID_WORKFLOW_TYPES:
            fail(errors, path, f"{label}.type must be once, recurring, or conditional")
        scaling = workflow.get("scaling")
        if scaling is not None and scaling not in VALID_WORKFLOW_SCALING:
            fail(errors, path, f"{label}.scaling must be singleton or parallel")
        parallelism = workflow.get("parallelism")
        if parallelism is not None:
            if not isinstance(parallelism, int):
                fail(errors, path, f"{label}.parallelism must be an integer")
            elif parallelism < 1 or parallelism > 10:
                fail(errors, path, f"{label}.parallelism must be between 1 and 10")
        if scaling == "singleton" and isinstance(parallelism, int) and parallelism != 1:
            fail(errors, path, f"{label}.parallelism must be 1 when scaling is singleton")
        if scaling == "parallel" and isinstance(parallelism, int) and parallelism < 2:
            fail(errors, path, f"{label}.parallelism must be at least 2 when scaling is parallel")
        owner = workflow.get("owner")
        if owner is not None:
            if not isinstance(owner, str) or owner not in agent_ids:
                fail(errors, path, f"{label}.owner must reference an existing agent")

        targeting = workflow.get("targeting")
        if targeting is not None:
            if not isinstance(targeting, dict):
                fail(errors, path, f"{label}.targeting must be an object")
            else:
                for field in ("communities", "groups", "tags", "agents"):
                    expect_string_list(errors, path, targeting.get(field, []), f"{label}.targeting.{field}")
                for community in targeting.get("communities", []):
                    if community not in community_names:
                        fail(errors, path, f"{label}.targeting.communities references missing community {community!r}")
                for group in targeting.get("groups", []):
                    if group not in group_names:
                        fail(errors, path, f"{label}.targeting.groups references missing group {group!r}")
                for agent in targeting.get("agents", []):
                    if agent not in agent_ids:
                        fail(errors, path, f"{label}.targeting.agents references missing agent {agent!r}")

        depends_on = workflow.get("dependsOn", [])
        if depends_on is not None:
            expect_string_list(errors, path, depends_on, f"{label}.dependsOn")

    for index, workflow in enumerate(workflows):
        depends_on = workflow.get("dependsOn", [])
        for dependency in depends_on:
            if dependency not in workflow_ids:
                fail(errors, path, f"workflows[{index}].dependsOn references missing workflow {dependency!r}")


def validate_markdown_template(markdown: MarkdownTemplate, path: Path, errors: list[str]) -> None:
    metadata = dict(markdown.metadata)
    metadata["description"] = markdown.description
    validate_core_template(
        {
            **metadata,
            "agents": markdown.agents,
            "communities": markdown.communities,
            "groups": markdown.groups,
            "workflows": [
                {
                    "id": re.sub(r"[^a-z0-9]+", "-", workflow["name"].lower()).strip("-"),
                    "name": workflow["name"],
                    "schedule": workflow["schedule"],
                    "executionMode": workflow["executionMode"],
                    "content": workflow["content"],
                    "owner": workflow.get("owner"),
                    "targeting": {
                        "communities": workflow["targets"]["communities"],
                        "groups": workflow["targets"]["groups"],
                        "tags": workflow["targets"]["tags"],
                        "agents": workflow["targets"]["agents"],
                    },
                    "dependsOn": workflow.get("dependsOn", []),
                }
                for workflow in markdown.workflows
            ],
        },
        path,
        errors,
    )

    workflow_names: set[str] = set()
    for workflow in markdown.workflows:
        if workflow["name"] in workflow_names:
            fail(errors, path, f"duplicate workflow name {workflow['name']!r}")
        workflow_names.add(workflow["name"])
        if workflow.get("schedule") is None:
            fail(errors, path, f"workflow {workflow['name']!r} is missing Schedule metadata")
        if workflow.get("executionMode") is None:
            fail(errors, path, f"workflow {workflow['name']!r} is missing Mode metadata")
        if not workflow["content"].startswith("#"):
            fail(errors, path, f"workflow {workflow['name']!r} content should start with a heading")


def compare_template_pair(
    json_data: dict[str, Any],
    markdown_data: MarkdownTemplate,
    directory: Path,
    errors: list[str],
) -> None:
    for field in ("name", "type", "version", "category", "author"):
        if json_data.get(field) != markdown_data.metadata.get(field):
            fail(
                errors,
                directory,
                f"template.json and TEMPLATE.md differ for top-level field {field!r}",
            )

    json_tags = sorted(json_data.get("tags", []))
    markdown_tags = sorted(markdown_data.metadata.get("tags", []))
    if json_tags != markdown_tags:
        fail(errors, directory, "template.json and TEMPLATE.md differ for top-level tags")

    json_tested_with = sorted(
        (item.get("platform", ""), item.get("version", ""))
        for item in json_data.get("testedWith", [])
    )
    markdown_tested_with = sorted(
        (item.get("platform", ""), item.get("version", ""))
        for item in markdown_data.metadata.get("testedWith", [])
    )
    if json_tested_with != markdown_tested_with:
        fail(errors, directory, "template.json and TEMPLATE.md differ for top-level testedWith")

    if {agent["id"] for agent in json_data.get("agents", [])} != {
        agent["id"] for agent in markdown_data.agents
    }:
        fail(errors, directory, "template.json and TEMPLATE.md differ for agent ids")

    if {item["name"] for item in json_data.get("communities", [])} != {
        item["name"] for item in markdown_data.communities
    }:
        fail(errors, directory, "template.json and TEMPLATE.md differ for community names")

    if {item["name"] for item in json_data.get("groups", [])} != {
        item["name"] for item in markdown_data.groups
    }:
        fail(errors, directory, "template.json and TEMPLATE.md differ for group names")

    # TEMPLATE.md is a human-facing summary, while template.json is the source of truth.
    # Keep top-level identity and structure in sync, but do not fail on workflow count drift
    # when markdown summaries intentionally compress multi-step workflow layouts.


def validate_directory(directory: Path, errors: list[str]) -> None:
    json_path = directory / "template.json"
    markdown_path = directory / "TEMPLATE.md"
    is_internal_special_case = directory.name == "clawmax-system-test"

    if not json_path.exists():
        fail(errors, directory, "missing template.json")
        return
    if not markdown_path.exists():
        fail(errors, directory, "missing TEMPLATE.md")
        return

    try:
        json_data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(errors, json_path, f"invalid JSON: {exc}")
        return
    if is_internal_special_case:
        expect_nonempty_string(errors, json_path, json_data.get("name"), "name")
        expect_nonempty_string(errors, json_path, json_data.get("type"), "type")
        expect_nonempty_string(errors, json_path, json_data.get("version"), "version")
    else:
        validate_core_template(json_data, json_path, errors)

    try:
        markdown_data = parse_markdown_template(markdown_path)
    except ValidationError as exc:
        if is_internal_special_case:
            markdown_data = None
        else:
            fail(errors, markdown_path, str(exc))
            return
    if markdown_data is not None:
        validate_markdown_template(markdown_data, markdown_path, errors)

    if markdown_data is not None:
        compare_template_pair(json_data, markdown_data, directory, errors)


def main() -> int:
    errors: list[str] = []
    for directory in sorted(path for path in TEMPLATES_DIR.iterdir() if path.is_dir()):
        validate_directory(directory, errors)

    if errors:
        print("Template validation failed:\n", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(list(TEMPLATES_DIR.iterdir()))} template directories successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
