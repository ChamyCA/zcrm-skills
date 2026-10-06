#!/usr/bin/env python3
"""Mechanical subset of the Phase 8 validation pass (spec FR-014, FR-008 of 009-skills-fix).

BLOCKING checks (exit 1, "FAIL:" lines):
  1. No orphan elements (empty req_ids) anywhere in the canonical YAML.
  2. Every module.field reference in required_fields / mandatory_fields / reads_fields /
     writes_fields / source_fields resolves to a field declared in `modules`.
  3. Every relationship target module exists, and each many_to_one relationship's
     lookup_field_api_name is declared as a field on the owning module.
  4. Every `Module.Field` token in rule trigger/condition/action, KPI formulas and stage
     entry/exit criteria (where Module is a declared module) resolves to a declared field.
  5. Blueprint transition from/to must be in that blueprint's `states`; field `type` must be one
     of the 19 tokens in yaml_to_mermaid.TYPE_TOKENS (imported, single source of truth, same
     list as templates/handoff-spec.yaml); module api_names (and field api_names per module)
     are unique; many_to_one lookup fields are typed lookup/ownerlookup; every required
     top-level key exists (package_version, prospect_slug, generated_at,
     source_register_version, modules, pipelines, blueprints, automation_rules, personas,
     traceability_summary, validation, erd_source, erd_content_hash); a `Module.Field` token
     naming an undeclared module fails; field `is_standard` (optional, default false) must be a
     boolean and `values` (optional) a list of strings.
  6. Blueprints need a declared stage/status picklist field on their module; pipelines need
     Deals.Stage declared. That state-driving field MUST declare `values`, and every blueprint
     state / pipeline stage must be one of them. A field with is_standard: true is exempt from
     nothing: it must still be declared (rules naming undeclared fields fail).

WARN-only checks (printed as "WARN:", do not change exit code):
  - Two or more automation rules write the same field; a rule reads and writes the same field.
  - erd_content_hash differs from the recomputed value (the key is required; a mismatch is only
    a warning). Definition used here:
    "sha256:" + sha256 of json.dumps({"modules": modules}, sort_keys=True,
    separators=(",", ":"), ensure_ascii=False) encoded as UTF-8.
  - Sibling *.md files cite `Module.Field` (backticked) that the YAML does not declare.

Judgment-based checks (naming consistency, [DOCS] citation quality, requirement coverage
narrative, stale open questions, etc.) remain the LLM's responsibility per SKILL.md Phase 8.

CLI:
    python3 validate_package.py <handoff-spec.yaml>

Exit code 0 and prints "PASS" if no blocking failures; otherwise exit code 1.
"""
import hashlib
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yaml_to_mermaid import TYPE_TOKENS  # noqa: E402  (single source of truth for field types)

REF_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\.([A-Za-z][A-Za-z0-9_]*)\b")
STATE_FIELD_NAMES = ("Stage", "Lead_Status", "Status")
LOOKUP_TYPES = {"lookup", "ownerlookup"}
REQUIRED_ARRAYS = ("modules", "pipelines", "blueprints", "automation_rules", "personas")
REQUIRED_SCALARS = ("package_version", "prospect_slug", "generated_at", "source_register_version",
                    "erd_source", "erd_content_hash")
REQUIRED_MAPS = ("traceability_summary", "validation")


def compute_erd_hash(model: dict) -> str:
    blob = json.dumps({"modules": model.get("modules", [])}, sort_keys=True,
                      separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _field_index(model: dict) -> set[str]:
    fields = set()
    for module in model.get("modules", []):
        mod = module["api_name"]
        for field in module.get("fields", []):
            fields.add(f"{mod}.{field['api_name']}")
    return fields


def _module_index(model: dict) -> set[str]:
    return {m["api_name"] for m in model.get("modules", [])}


def _state_field(module: dict):
    """Declared field holding this module's stage/state, or None."""
    fields = {f["api_name"]: f for f in module.get("fields", [])}
    explicit = module.get("state_field")
    if explicit:
        return fields.get(explicit)
    for n in STATE_FIELD_NAMES:
        if n in fields:
            return fields[n]
    for n, f in fields.items():
        if f.get("type") == "picklist" and ("Stage" in n or "Status" in n):
            return f
    return None


def _values(field: dict):
    v = field.get("values")
    if not isinstance(v, list) or not v:
        return None
    return [x for x in v if isinstance(x, str)]


def validate(model: dict, warnings: list[str] | None = None, base_dir: str | None = None) -> list[str]:
    warns = warnings if warnings is not None else []
    if not isinstance(model, dict):
        return ["handoff spec is not a YAML mapping"]
    model = dict(model)
    head = [f"missing required top-level array: {k}"
            for k in REQUIRED_ARRAYS if not isinstance(model.get(k), list)]
    head += [f"missing required top-level key: {k}"
             for k in REQUIRED_SCALARS if model.get(k) is None]
    head += [f"missing required top-level key: {k} (must be a mapping)"
             for k in REQUIRED_MAPS if not isinstance(model.get(k), dict)]
    for k in REQUIRED_ARRAYS:  # normalize so later checks cannot crash on a missing/null key
        if not isinstance(model.get(k), list):
            model[k] = []
    return head + _validate(model) + _extended(model, warns, base_dir)


def _extended(model: dict, warns: list[str], base_dir: str | None) -> list[str]:
    fails: list[str] = []
    field_index = _field_index(model)
    module_index = _module_index(model)
    mods = {m["api_name"]: m for m in model.get("modules", [])}

    # Duplicate module / field api_names, and field type tokens.
    seen_mods: set[str] = set()
    for m in model.get("modules", []):
        if m["api_name"] in seen_mods:
            fails.append(f"duplicate module api_name: {m['api_name']}")
        seen_mods.add(m["api_name"])
        seen_fields: set[str] = set()
        for f in m.get("fields", []):
            if f["api_name"] in seen_fields:
                fails.append(f"duplicate field api_name: {m['api_name']}.{f['api_name']}")
            seen_fields.add(f["api_name"])
            if f.get("type") not in TYPE_TOKENS:
                fails.append(
                    f"invalid field type: {m['api_name']}.{f['api_name']} has type "
                    f"{f.get('type')!r} (allowed: {', '.join(sorted(TYPE_TOKENS))})"
                )
            if "is_standard" in f and not isinstance(f["is_standard"], bool):
                fails.append(f"invalid is_standard: {m['api_name']}.{f['api_name']} must be true or false")
            if "values" in f and not (isinstance(f["values"], list)
                                      and all(isinstance(x, str) for x in f["values"])):
                fails.append(f"invalid values: {m['api_name']}.{f['api_name']} values must be a list of strings")

    # Relationship lookup fields must be declared on the owning module and typed lookup.
    for m in model.get("modules", []):
        ftypes = {f["api_name"]: f.get("type") for f in m.get("fields", [])}
        for rel in m.get("relationships", []):
            lf = rel.get("lookup_field_api_name")
            if rel.get("cardinality") == "many_to_one" and lf:
                if lf not in ftypes:
                    fails.append(
                        f"undeclared lookup field: {m['api_name']}.{lf} (relationship to "
                        f"{rel.get('target_module')}) is not declared in {m['api_name']}.fields"
                    )
                elif ftypes[lf] not in LOOKUP_TYPES:
                    fails.append(
                        f"lookup field not typed lookup: {m['api_name']}.{lf} has type "
                        f"{ftypes[lf]!r} but backs a many_to_one relationship to {rel.get('target_module')}"
                    )

    def scan(text, where):
        for mod, fld in REF_RE.findall(text or ""):
            if mod not in module_index:
                fails.append(f"undeclared module reference: {mod}.{fld} used in {where}")
            elif f"{mod}.{fld}" not in field_index:
                fails.append(f"undeclared field reference: {mod}.{fld} used in {where}")

    for r in model.get("automation_rules", []):
        for k in ("trigger", "condition", "action"):
            scan(r.get(k), f"rule {r.get('rule_id')}.{k}")
    for p in model.get("personas", []):
        for k in p.get("kpis", []):
            scan(k.get("formula"), f"KPI {k.get('name')}")
    for p in model.get("pipelines", []):
        for st in p.get("stages", []):
            scan(st.get("entry_criteria"), f"stage {st.get('name')}")
            scan(st.get("exit_criteria"), f"stage {st.get('name')}")

    # Blueprint states / pipeline stages vs. declared state field and its values.
    for bp in model.get("blueprints", []):
        mod = mods.get(bp.get("module"))
        if mod is None:
            fails.append(f"blueprint targets unknown module {bp.get('module')}")
            continue
        states = bp.get("states", [])
        for t in bp.get("transitions", []):
            for end in ("from", "to"):
                if t.get(end) not in states:
                    fails.append(
                        f"blueprint transition {t.get('from')}->{t.get('to')} on {bp['module']}: "
                        f"{end} state {t.get(end)!r} is not in the blueprint's states"
                    )
        sf = _state_field(mod)
        if sf is None:
            fails.append(
                f"undeclared state field: blueprint on {bp['module']} has states but "
                f"{bp['module']} declares no stage/status picklist field (e.g. {bp['module']}.Stage)"
            )
            continue
        vals = _values(sf)
        if vals is None:
            fails.append(f"missing values: {bp['module']}.{sf['api_name']} drives blueprint states "
                         f"but declares no `values` list")
        else:
            for st in bp.get("states", []):
                if st not in vals:
                    fails.append(f"blueprint state {st!r} not in {bp['module']}.{sf['api_name']} values")
    if model.get("pipelines"):
        deals = mods.get("Deals")
        sf = _state_field(deals) if deals else None
        if sf is None:
            fails.append("undeclared state field: pipelines defined but Deals.Stage is not declared in modules")
        else:
            vals = _values(sf)
            if vals is None:
                fails.append(f"missing values: Deals.{sf['api_name']} drives pipeline stages "
                             f"but declares no `values` list")
            else:
                for p in model["pipelines"]:
                    for st in p.get("stages", []):
                        if st.get("name") not in vals:
                            fails.append(f"pipeline stage {st.get('name')!r} not in Deals.{sf['api_name']} values")

    # Conflicting writers / self-retrigger (WARN).
    writers: dict[str, list[str]] = {}
    for r in model.get("automation_rules", []):
        for f in r.get("writes_fields", []):
            writers.setdefault(f, []).append(r["rule_id"])
        for f in sorted(set(r.get("reads_fields", [])) & set(r.get("writes_fields", []))):
            warns.append(f"possible loop: rule {r['rule_id']} reads and writes {f}")
    for f, ids in writers.items():
        if len(set(ids)) > 1:
            warns.append(f"conflicting writers: {f} written by {', '.join(ids)}")

    # erd_content_hash (WARN).
    h = model.get("erd_content_hash") or ""
    if not h or h.endswith("...") or "mock" in h:
        warns.append("erd_content_hash is empty or a placeholder")
    else:
        calc = compute_erd_hash(model)
        if h != calc:
            warns.append(f"erd_content_hash mismatch: file has {h}, recomputed {calc}")

    # Fields cited in sibling docs but not declared (WARN).
    if base_dir:
        pat = re.compile(r"`([A-Z][A-Za-z0-9_]*)\.([A-Za-z][A-Za-z0-9_]*)`")
        try:
            names = sorted(n for n in os.listdir(base_dir) if n.endswith(".md"))
        except OSError:
            names = []
        for n in names:
            try:
                with open(os.path.join(base_dir, n), encoding="utf-8") as fh:
                    txt = fh.read()
            except OSError:
                continue
            seen = set()
            for mod, fld in pat.findall(txt):
                if mod in module_index and f"{mod}.{fld}" not in field_index and (mod, fld) not in seen:
                    seen.add((mod, fld))
                    warns.append(f"{n} cites {mod}.{fld} but it is not declared in the YAML")
    return fails


def _validate(model: dict) -> list[str]:
    failures: list[str] = []
    field_index = _field_index(model)
    module_index = _module_index(model)

    for module in model.get("modules", []):
        if not module.get("req_ids"):
            failures.append(f"orphan module: {module['api_name']} has empty req_ids")
        for field in module.get("fields", []):
            if not field.get("req_ids"):
                failures.append(
                    f"orphan field: {module['api_name']}.{field['api_name']} has empty req_ids"
                )
        for rel in module.get("relationships", []):
            if not rel.get("req_ids"):
                failures.append(
                    f"orphan relationship: {module['api_name']} -> {rel['target_module']} has empty req_ids"
                )
            if rel["target_module"] not in module_index:
                failures.append(
                    f"dangling reference: {module['api_name']} relationship targets unknown module {rel['target_module']}"
                )

    for pipeline in model.get("pipelines", []):
        for stage in pipeline.get("stages", []):
            if not stage.get("req_ids"):
                failures.append(f"orphan pipeline stage: {stage['name']} has empty req_ids")
            for f in stage.get("required_fields", []):
                if f not in field_index:
                    failures.append(f"dangling reference: pipeline stage {stage['name']} requires unknown field {f}")

    for blueprint in model.get("blueprints", []):
        for transition in blueprint.get("transitions", []):
            if not transition.get("req_ids"):
                failures.append(
                    f"orphan blueprint transition: {blueprint['module']} {transition['from']}->{transition['to']} has empty req_ids"
                )
            for f in transition.get("mandatory_fields", []):
                if f not in field_index:
                    failures.append(
                        f"dangling reference: blueprint transition {transition['from']}->{transition['to']} requires unknown field {f}"
                    )

    for rule in model.get("automation_rules", []):
        if not rule.get("req_ids"):
            failures.append(f"orphan automation rule: {rule['rule_id']} has empty req_ids")
        for f in rule.get("reads_fields", []) + rule.get("writes_fields", []):
            if f not in field_index:
                failures.append(f"dangling reference: rule {rule['rule_id']} references unknown field {f}")

    for persona in model.get("personas", []):
        if not persona.get("req_ids"):
            failures.append(f"orphan persona: {persona['persona']} has empty req_ids")
        for kpi in persona.get("kpis", []):
            if not kpi.get("req_ids"):
                failures.append(f"orphan KPI: {kpi['name']} has empty req_ids")
            for f in kpi.get("source_fields", []):
                if f not in field_index:
                    failures.append(f"dangling reference: KPI {kpi['name']} references unknown field {f}")

    return failures


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_package.py <handoff-spec.yaml>", file=sys.stderr)
        return 2
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        model = yaml.safe_load(f)

    warns: list[str] = []
    failures = validate(model, warns, os.path.dirname(os.path.abspath(sys.argv[1])))
    for w in warns:
        print(f"WARN: {w}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
