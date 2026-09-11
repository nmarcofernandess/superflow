#!/usr/bin/env python3
"""Generate a Superflow QG: a deterministic, self-contained HTML snapshot.

The QG presents what exists on disk. It never calls an LLM. Tasks and Graph
consume one census. Sprint is an opt-in human composition, never a second
authority of spec state.

Exit codes: 0 wrote the snapshot, 1 contract error.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent
VALIDATE = SCRIPT_DIR / "validate_superflow.py"
BOARD_HTML = PLUGIN_ROOT / "assets" / "task-board" / "board.html"

ABSENT = "Não contém"
CONTRACT_PLAN = "implementation_plan.json"

KIND_PACKAGE = "package"
KIND_DECLARED_CHILD = "declared_child"
KIND_UNREGISTERED = "unregistered"

EDGE_HIERARCHY = "hierarchy"
EDGE_DEPENDS = "depends_on"

EXIT_OK = 0
EXIT_CONTRACT = 1


def _validator():
    import importlib.util

    spec = importlib.util.spec_from_file_location("validate_superflow", VALIDATE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


V = _validator()


def posix_rel(path: Path, root: Path) -> str:
    resolved = path.resolve()
    base = root.resolve()
    if resolved == base:
        return "."
    return resolved.relative_to(base).as_posix()


def path_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def script_safe_dumps(data: object) -> str:
    return (
        json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def read_json(path: Path) -> tuple[object | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"{path.name} ilegível: {exc.msg} (linha {exc.lineno})"
    except OSError as exc:
        return None, f"{path.name} ilegível: {exc.strerror or exc}"


def git_read_base(start: Path) -> str:
    try:
        ref = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=start,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        sha = subprocess.run(
            ["git", "rev-parse", "--short=9", "HEAD"],
            cwd=start,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "disk"
    if not ref or not sha:
        return "disk"
    return f"{ref}@{sha}"


def load_board_css() -> str:
    if not BOARD_HTML.is_file():
        raise SystemExit("CONTRACT: missing assets/task-board/board.html")
    text = BOARD_HTML.read_text(encoding="utf-8")
    match = re.search(r"<style>(.*?)</style>", text, re.S)
    if not match:
        raise SystemExit("CONTRACT: board.html has no <style> block")
    css = match.group(1).strip()
    if "--paper" not in css or "--ink" not in css:
        raise SystemExit("CONTRACT: board.html must keep --paper and --ink")
    if "--papel" in css or "--tinta" in css:
        raise SystemExit("CONTRACT: board.html must not use --papel/--tinta")
    return css


def contract_tracks_plan(status: dict) -> Path | None:
    artifacts = status.get("artifacts") if isinstance(status.get("artifacts"), dict) else {}
    source = status.get("task_source") if isinstance(status.get("task_source"), dict) else {}
    plan = artifacts.get("plan")
    path = source.get("path")
    if plan == CONTRACT_PLAN:
        return Path(CONTRACT_PLAN)
    if isinstance(path, str) and Path(path).name == CONTRACT_PLAN:
        return Path(path)
    return None


def collect_tasks(pkg: Path, status: dict) -> tuple[list[dict] | None, list[str]]:
    rel = contract_tracks_plan(status)
    if rel is None:
        return None, []
    plan_path = (pkg / rel).resolve()
    if not plan_path.is_file():
        return [], [f"plano acompanhado ausente: {rel.as_posix()}"]
    data, err = read_json(plan_path)
    if err:
        return [], [err]
    if not isinstance(data, dict):
        return [], [f"{rel.name} incompatível: esperado objeto JSON"]
    tasks: list[dict] = []
    for sub in V.iter_plan_subtasks(data):
        name = str(sub.get("id") or "").strip() or ABSENT
        state = sub.get("status")
        if not isinstance(state, str) or not state.strip():
            state = ABSENT
        tasks.append({"id": name, "name": name, "state": state})
    if not tasks:
        return [], [f"{rel.name} incompatível: plano sem subtasks"]
    return tasks, []


def handbook_view(status: dict) -> tuple[dict | None, list[str]]:
    if "handbook" not in status:
        return None, []
    block = status.get("handbook")
    if block is None:
        return None, []
    if not isinstance(block, dict):
        return None, ["handbook incompatível: esperado objeto ou ausente"]
    next_useful = block.get("next_useful")
    useful: list[dict] = []
    diags: list[str] = []
    if next_useful is None:
        useful_field: list[dict] | None = None
    elif not isinstance(next_useful, list):
        useful_field = None
        diags.append("handbook.next_useful incompatível: esperado lista")
    else:
        useful_field = useful
        for item in next_useful:
            if not isinstance(item, dict):
                diags.append("handbook.next_useful incompatível: entrada que não é objeto")
                continue
            useful.append(
                {
                    "id": str(item.get("id") or ABSENT),
                    "kind": str(item.get("kind") or ABSENT),
                }
            )
    return {
        "selo": block["selo"] if isinstance(block.get("selo"), str) and block.get("selo") else None,
        "next_useful": useful_field,
        "read_base": block["read_base"]
        if isinstance(block.get("read_base"), str) and block.get("read_base")
        else None,
        "read_at": block["read_at"] if isinstance(block.get("read_at"), str) and block.get("read_at") else None,
        "index_action": block["index_action"]
        if isinstance(block.get("index_action"), str) and block.get("index_action")
        else None,
        "archivable": block["archivable"]
        if isinstance(block.get("archivable"), str) and block.get("archivable")
        else None,
    }, diags


def phases_view(status: dict) -> tuple[dict | None, list[str]]:
    if "phases" not in status:
        return None, []
    phases = status.get("phases")
    if phases is None:
        return None, []
    if not isinstance(phases, dict):
        return None, ["phases incompatível: esperado objeto"]
    out: dict[str, str] = {}
    diags: list[str] = []
    for name, value in phases.items():
        if isinstance(value, str) and value.strip():
            out[str(name)] = value
        else:
            diags.append(f"phases.{name} incompatível: esperado string de estado")
            out[str(name)] = "incompatível"
    return out, diags


def depends_view(status: dict) -> tuple[list[str] | None, list[str]]:
    if "depends_on" not in status:
        return None, []
    deps = status.get("depends_on")
    if deps is None:
        return [], []
    if not isinstance(deps, list) or any(not isinstance(item, str) for item in deps):
        return None, ["depends_on incompatível: esperado lista de ids"]
    return list(deps), []


def children_source_view(status: dict) -> tuple[dict | None, list[str]]:
    if "children_source" not in status:
        return None, []
    source = status.get("children_source")
    if source is None:
        return None, []
    if not isinstance(source, dict):
        return None, ["children_source incompatível: esperado objeto"]
    glob = source.get("glob")
    if not isinstance(glob, str) or not glob.strip():
        return None, ["children_source incompatível: glob ausente"]
    campaign = source.get("campaign")
    return {
        "glob": glob,
        "campaign": campaign if isinstance(campaign, str) else None,
    }, []


def declared_child_dirs(mother: Path, source: dict, specs_root: Path) -> tuple[list[Path], list[str]]:
    glob = source.get("glob")
    if not isinstance(glob, str) or not glob.strip():
        return [], []
    pattern = glob.strip()
    if Path(pattern).is_absolute():
        return [], ["children_source incompatível: glob absoluto"]
    if ".." in Path(pattern).parts:
        return [], ["children_source incompatível: glob sai do pacote"]
    seen: dict[Path, None] = {}
    try:
        matches = sorted(mother.glob(pattern))
    except (NotImplementedError, ValueError, OSError):
        return [], ["children_source incompatível: glob inválido"]
    specs = specs_root.resolve()
    mother_root = mother.resolve()
    diags: list[str] = []
    for match in matches:
        pkg = match.parent if match.name == "status.json" else match
        if not path_inside(pkg, specs):
            continue
        if not path_inside(pkg, mother_root):
            diags.append("children_source incompatível: glob sai do pacote")
            continue
        seen.setdefault(pkg.resolve(), None)
    parts = Path(pattern).parts
    if len(parts) >= 2 and parts[-1] == "status.json" and parts[-2] == "*":
        parent = mother.joinpath(*parts[:-2]) if len(parts) > 2 else mother
        if not path_inside(parent, mother_root):
            diags.append("children_source incompatível: glob sai do pacote")
        elif parent.is_dir() and path_inside(parent, specs):
            for child in sorted(p for p in parent.iterdir() if p.is_dir()):
                if not path_inside(child, specs):
                    continue
                if not path_inside(child, mother_root):
                    diags.append("children_source incompatível: glob sai do pacote")
                    continue
                seen.setdefault(child.resolve(), None)
    return list(seen), list(dict.fromkeys(diags))


def empty_record(rel: str, pkg_id: str, kind: str) -> dict:
    return {
        "id": pkg_id,
        "rel": rel,
        "kind": kind,
        "title": None,
        "presence": "missing_status",
        "diagnostics": [],
        "phases": None,
        "current_phase": None,
        "handbook": None,
        "tasks": None,
        "depends_on": None,
        "children_source": None,
        "campaign": None,
        "parent": None,
    }


def read_package(pkg: Path, specs_root: Path, kind: str) -> dict:
    rel = posix_rel(pkg, specs_root)
    record = empty_record(rel, pkg.name, kind)
    status_path = pkg / "status.json"
    if not status_path.exists():
        record["diagnostics"] = ["Não contém status.json"]
        record["presence"] = "missing_status"
        return record
    data, err = read_json(status_path)
    if err:
        record["diagnostics"] = [err]
        record["presence"] = "unreadable"
        return record
    if not isinstance(data, dict):
        record["diagnostics"] = ["status.json incompatível: esperado objeto"]
        record["presence"] = "incompatible"
        return record

    pkg_id = data.get("id")
    record["id"] = pkg_id if isinstance(pkg_id, str) and pkg_id.strip() else pkg.name
    title = data.get("title")
    record["title"] = title if isinstance(title, str) and title.strip() else None
    campaign = data.get("campaign")
    record["campaign"] = campaign if isinstance(campaign, str) and campaign.strip() else None
    current = data.get("current_phase")
    record["current_phase"] = current if isinstance(current, str) and current.strip() else None

    diags: list[str] = []
    phases, phase_diags = phases_view(data)
    record["phases"] = phases
    diags.extend(phase_diags)
    handbook, hb_diags = handbook_view(data)
    record["handbook"] = handbook
    diags.extend(hb_diags)
    tasks, task_diags = collect_tasks(pkg, data)
    record["tasks"] = tasks
    diags.extend(task_diags)
    depends, dep_diags = depends_view(data)
    record["depends_on"] = depends
    diags.extend(dep_diags)
    children, child_diags = children_source_view(data)
    record["children_source"] = children
    diags.extend(child_diags)

    record["diagnostics"] = diags
    if diags:
        record["presence"] = "incompatible"
    else:
        record["presence"] = "ok"
    return record


def parent_rel(rel: str, known: set[str]) -> str | None:
    if rel in {".", ""}:
        return None
    parts = rel.split("/")
    for i in range(len(parts) - 1, 0, -1):
        candidate = "/".join(parts[:i])
        if candidate in known:
            return candidate
    return None


def close_scope(records: list[dict], tokens: set[str] | None) -> list[dict]:
    if not tokens:
        return records
    keep: set[str] = set()
    by_rel = {r["rel"]: r for r in records}

    def matches(record: dict) -> bool:
        rel = record["rel"]
        pkg_id = record["id"]
        for token in tokens:
            if pkg_id == token or rel == token:
                return True
            if rel.startswith(token.rstrip("/") + "/"):
                return True
        return False

    for record in records:
        if matches(record):
            keep.add(record["rel"])

    changed = True
    while changed:
        changed = False
        for record in records:
            if record["rel"] in keep:
                continue
            parent = record.get("parent")
            if parent and parent in keep:
                keep.add(record["rel"])
                changed = True
                continue
            for other in records:
                if other["rel"] not in keep:
                    continue
                source = other.get("children_source")
                if not source:
                    continue
                if record["rel"].startswith(other["rel"].rstrip("/") + "/"):
                    keep.add(record["rel"])
                    changed = True
                    break

    return [by_rel[rel] for rel in sorted(keep) if rel in by_rel]


def visible_children(path: Path) -> list[Path]:
    try:
        return sorted(
            (child for child in path.iterdir() if not child.name.startswith(".")),
            key=lambda child: child.name,
        )
    except OSError:
        return []


def summarize_contents(path: Path) -> list[str]:
    """Immediate names only. Internal dirs stay content, not new blocks."""
    labels: list[str] = []
    for child in visible_children(path):
        labels.append(f"{child.name}/" if child.is_dir() else child.name)
    return labels


def folder_is_empty(path: Path) -> bool:
    return not visible_children(path)


def holds_packages(path: Path) -> bool:
    """A shelf that already stores packages (archived/). Those packages speak for themselves."""
    return any(child.is_dir() and (child / "status.json").exists() for child in visible_children(path))


def contains_run_sh(path: Path) -> bool:
    try:
        return any(child.is_file() for child in path.rglob("run.sh"))
    except OSError:
        return False


def find_unregistered_folders(specs_root: Path, package_rels: set[str]) -> list[dict]:
    """First-level non-package non-empty folders. Not a filename allowlist.

    Declared children are already in the package census. Nested artifact
    directories (harness, plans, context…) are listed inside this block.
    """
    found: list[dict] = []
    try:
        top = [child for child in specs_root.iterdir() if child.is_dir() and not child.name.startswith(".")]
    except OSError:
        return found
    for child in sorted(top, key=lambda item: item.name):
        rel = posix_rel(child, specs_root)
        if rel in package_rels or rel == ".":
            continue
        if folder_is_empty(child):
            continue
        if holds_packages(child):
            continue
        found.append(
            {
                "rel": rel,
                "kind": KIND_UNREGISTERED,
                "contents": summarize_contents(child),
                "has_run_sh": contains_run_sh(child),
            }
        )
    return found


def census(specs_root: Path, scope: set[str] | None) -> dict:
    packages: dict[str, dict] = {}
    declared_from: dict[str, str] = {}

    for status_file in sorted(specs_root.rglob("status.json")):
        pkg = status_file.parent
        rel = posix_rel(pkg, specs_root)
        packages[rel] = read_package(pkg, specs_root, KIND_PACKAGE)

    for rel, record in list(packages.items()):
        source = record.get("children_source")
        if not source:
            continue
        mother = specs_root / rel
        children, glob_diags = declared_child_dirs(mother, source, specs_root)
        if glob_diags:
            record["diagnostics"] = list(record.get("diagnostics") or []) + glob_diags
            if record["presence"] == "ok":
                record["presence"] = "incompatible"
        for child in children:
            child_rel = posix_rel(child, specs_root)
            declared_from[child_rel] = rel
            if child_rel not in packages:
                packages[child_rel] = read_package(child, specs_root, KIND_DECLARED_CHILD)

    unregistered = find_unregistered_folders(specs_root, set(packages))

    known = set(packages)
    for rel, record in packages.items():
        record["parent"] = parent_rel(rel, known)
        record["declared_by"] = declared_from.get(rel)

    scoped = close_scope(list(packages.values()), scope)
    if scope:
        unregistered = [
            item
            for item in unregistered
            if item["rel"] in scope
            or any(item["rel"] == token or item["rel"].startswith(token.rstrip("/") + "/") for token in scope)
        ]

    scoped.sort(key=lambda r: r["rel"])
    unregistered.sort(key=lambda r: r["rel"])

    id_hits: dict[str, list[dict]] = defaultdict(list)
    for record in scoped:
        id_hits[record["id"]].append(record)
    for record in scoped:
        hits = id_hits[record["id"]]
        if len(hits) < 2:
            continue
        record["diagnostics"] = list(record.get("diagnostics") or []) + [f"id duplicado: {record['id']}"]
        if record["presence"] == "ok":
            record["presence"] = "incompatible"

    edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for record in scoped:
        src = record["rel"]
        source = record.get("children_source")
        if source:
            mother = specs_root / record["rel"]
            children, _ = declared_child_dirs(mother, source, specs_root)
            for child in children:
                child_rel = posix_rel(child, specs_root)
                other = next((r for r in scoped if r["rel"] == child_rel), None)
                if other is None or other["rel"] == src:
                    continue
                key = (EDGE_HIERARCHY, src, other["rel"])
                if key in seen:
                    continue
                seen.add(key)
                edges.append({"src": src, "dst": other["rel"], "kind": EDGE_HIERARCHY})
        deps = record.get("depends_on")
        if isinstance(deps, list):
            for dep in deps:
                targets = id_hits.get(dep, [])
                if len(targets) != 1:
                    continue
                dst = targets[0]["rel"]
                if dst == src:
                    continue
                key = (EDGE_DEPENDS, src, dst)
                if key in seen:
                    continue
                seen.add(key)
                edges.append({"src": src, "dst": dst, "kind": EDGE_DEPENDS})

    edges.sort(key=lambda e: (e["kind"], e["src"], e["dst"]))
    return {
        "packages": scoped,
        "unregistered": unregistered,
        "edges": edges,
    }


def parse_scope(raw: str | None, scope_file: Path | None) -> set[str] | None:
    tokens: list[str] = []
    if raw:
        tokens.extend(part.strip() for part in raw.split(",") if part.strip())
    if scope_file is not None:
        text = scope_file.read_text(encoding="utf-8")
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, list):
            tokens.extend(str(item).strip() for item in loaded if str(item).strip())
        else:
            tokens.extend(line.strip() for line in text.splitlines() if line.strip())
    cleaned = {token.replace("\\", "/").strip("/") for token in tokens if token}
    return cleaned or None


def load_sprint(path: Path | None) -> dict | None:
    if path is None:
        return None
    data, err = read_json(path)
    if err:
        return {"name": path.name, "items": [], "diagnostics": [err], "next": None}
    if not isinstance(data, dict):
        return {"name": path.name, "items": [], "diagnostics": ["sprint incompatível: esperado objeto"], "next": None}
    items = data.get("items") or data.get("packages") or []
    sequence: list[dict] = []
    diags: list[str] = []
    if not isinstance(items, list):
        diags.append("sprint.items incompatível: esperado lista")
        items = []
    for item in items:
        if isinstance(item, str):
            sequence.append({"id": item, "note": None})
        elif isinstance(item, dict) and isinstance(item.get("id"), str):
            note = item.get("note")
            sequence.append({"id": item["id"], "note": note if isinstance(note, str) else None})
        else:
            diags.append("sprint.items incompatível: entrada sem id")
    name = data.get("name")
    nxt = data.get("next")
    return {
        "name": name if isinstance(name, str) and name.strip() else path.stem,
        "items": sequence,
        "diagnostics": diags,
        "next": nxt if isinstance(nxt, str) and nxt.strip() else None,
    }


def metro_state(record: dict | None) -> str:
    if record is None:
        return "queued"
    if record.get("presence") in {"unreadable", "incompatible", "missing_status"}:
        return "blocked"
    phases = record.get("phases") or {}
    if str(phases.get("qa") or "").lower() == "complete":
        return "done"
    if any(str(value).lower() == "blocked" for value in phases.values()):
        return "blocked"
    if str(record.get("current_phase") or "").lower() in {"execute", "plan", "review", "qa"}:
        if str(phases.get(record["current_phase"]) or "").lower() == "running":
            return "active"
    if any(str(value).lower() == "running" for value in phases.values()):
        return "active"
    return "queued"


def snapshot(
    specs_root: Path,
    *,
    scope: set[str] | None,
    stamp: str,
    read_base: str,
    sprint: dict | None,
    dest_name: str,
) -> dict:
    counted = census(specs_root, scope)
    by_id = {r["id"]: r for r in counted["packages"]}
    if sprint is not None:
        for item in sprint["items"]:
            record = by_id.get(item["id"])
            item["state"] = metro_state(record)
            item["present"] = record is not None
            if record is None:
                sprint.setdefault("diagnostics", []).append(
                    f"{item['id']}: fora do recorte ou sem pacote"
                )
    return {
        "generated_at": stamp,
        "read_base": read_base,
        "scope": sorted(scope) if scope else "all",
        "dest_name": dest_name,
        "packages": counted["packages"],
        "unregistered": counted["unregistered"],
        "edges": counted["edges"],
        "sprint": sprint,
    }


QG_LAYOUT_CSS = """
.tabs { display: flex; gap: 0; margin: 28px 0 0; border-bottom: 1px solid var(--ink); }
.tab { font-family: var(--mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
  background: transparent; border: 1px solid var(--ink); border-bottom: none; color: var(--ink);
  padding: 8px 16px; cursor: pointer; }
.tab[aria-selected="true"] { background: var(--ink); color: var(--paper); }
.subtabs { display: flex; gap: 10px; margin: 16px 0 0; }
.subtab { font-family: var(--mono); font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase;
  background: var(--paper); border: 1px solid var(--ink); color: var(--ink); padding: 6px 12px; cursor: pointer; }
.subtab[aria-selected="true"] { background: var(--accent); border-color: var(--accent); color: #fff; }
.panel[hidden] { display: none; }
.counts { font-family: var(--mono); font-size: 12px; letter-spacing: .06em; color: var(--muted); margin-top: 14px; }
.pkg { border: 1px solid var(--ink); background: var(--paper-2); margin-top: 12px; }
.pkg > summary { cursor: pointer; list-style: none; padding: 12px 16px; display: flex; gap: 12px;
  align-items: baseline; flex-wrap: wrap; }
.pkg > summary::-webkit-details-marker { display: none; }
.pkg .pid { font-family: var(--mono); font-weight: 700; letter-spacing: .04em; }
.pkg .ptitle { color: var(--ink-soft); }
.pkg .chip { font-family: var(--mono); font-size: 10px; letter-spacing: .08em; text-transform: uppercase;
  border: 1px solid currentColor; padding: 2px 8px; }
.pkg .chip.ok { color: var(--accent); }
.pkg .chip.bad { color: var(--alert); }
.pkg .chip.miss { color: var(--muted); }
.pkg .body { padding: 0 16px 16px; border-top: 1px solid var(--hair); }
.kv { display: grid; grid-template-columns: 14ch 1fr; gap: 6px 16px; margin-top: 12px; font-size: 15px; }
.kv dt { font-family: var(--mono); font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.absent { color: var(--muted); font-style: italic; }
.tasks { margin-top: 10px; }
.task { display: flex; justify-content: space-between; gap: 12px; padding: 6px 0;
  border-bottom: 1px solid var(--hair); font-size: 15px; }
.task .st { font-family: var(--mono); font-size: 10.5px; letter-spacing: .08em; text-transform: uppercase; }
.children { margin-top: 12px; }
.graph-wrap { overflow: auto; }
svg.qg-graph { display: block; min-width: 720px; }
svg.qg-graph .n { cursor: pointer; }
svg.qg-graph.foco .e { opacity: .12; }
svg.qg-graph.foco .e.on { opacity: 1; }
svg.qg-graph.foco .n { opacity: .22; }
svg.qg-graph.foco .n.on { opacity: 1; }
.legend { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 12px;
  font-family: var(--mono); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: var(--ink-soft); }
.legend i { display: inline-block; width: 22px; height: 0; border-top: 2px solid currentColor; margin-right: 6px; vertical-align: middle; }
.legend .dep { color: var(--accent); border-top-style: dashed; }
.legend .hier { color: var(--ink); }
.unreg-list { margin-top: 36px; }
.unreg { border: 1.5px dashed var(--ink); background: var(--paper-2); padding: 14px 16px; margin-top: 12px; }
.unreg h3 { font-family: var(--mono); font-size: 15px; letter-spacing: .02em; margin-bottom: 8px; }
.unreg p { font-size: 15px; color: var(--ink-soft); margin-top: 6px; max-width: 62ch; }
.unreg .kind { font-family: var(--mono); font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.unreg .gate { border-left: 2px solid var(--accent); padding-left: 12px; margin-top: 10px; color: var(--ink); }
"""


def esc(text: object) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def field_or_absent(value: object) -> str:
    if value is None:
        return f'<span class="absent">{esc(ABSENT)}</span>'
    if value == []:
        return f'<span class="absent">lista vazia</span>'
    return ""


def presence_chip(record: dict) -> str:
    presence = record.get("presence")
    if presence == "ok":
        return '<span class="chip ok">ok</span>'
    if presence == "missing_status":
        return f'<span class="chip miss">{esc(ABSENT)} status</span>'
    return '<span class="chip bad">incompatível</span>'


def render_tasks_list(tasks: list[dict] | None) -> str:
    if tasks is None:
        return f'<p class="absent">{esc(ABSENT)}</p>'
    if not tasks:
        return f'<p class="absent">{esc(ABSENT)}</p>'
    rows = []
    for task in tasks:
        rows.append(
            f'<div class="task"><span>{esc(task.get("name") or task.get("id") or ABSENT)}</span>'
            f'<span class="st">{esc(task.get("state") or ABSENT)}</span></div>'
        )
    return '<div class="tasks">' + "".join(rows) + "</div>"


def render_handbook(block: dict | None) -> str:
    if block is None:
        return f'<span class="absent">{esc(ABSENT)}</span>'
    selo = block.get("selo") or ABSENT
    useful = block.get("next_useful")
    if useful is None:
        nxt = ABSENT
    elif not useful:
        nxt = "lista vazia"
    else:
        nxt = ", ".join(f"{item.get('id') or ABSENT} ({item.get('kind') or ABSENT})" for item in useful)
    bits = [
        f"selo {esc(selo)}",
        f"next_useful {esc(nxt)}",
    ]
    if block.get("read_base"):
        bits.append(f"base {esc(block['read_base'])}")
    return " · ".join(bits)


def render_phases(phases: dict | None) -> str:
    if phases is None:
        return f'<span class="absent">{esc(ABSENT)}</span>'
    if not phases:
        return f'<span class="absent">{esc(ABSENT)}</span>'
    return ", ".join(f"{esc(name)}={esc(state)}" for name, state in phases.items())


def render_deps(deps: list[str] | None) -> str:
    if deps is None:
        return f'<span class="absent">{esc(ABSENT)}</span>'
    if not deps:
        return f'<span class="absent">lista vazia</span>'
    return ", ".join(esc(item) for item in deps)


def render_diagnostics(diags: list[str]) -> str:
    if not diags:
        return ""
    lines = "".join(f"<div>{esc(line)}</div>" for line in diags)
    return f'<div class="err" data-qg-diag="1">{lines}</div>'


def render_package(record: dict, children_of: dict[str, list[dict]]) -> str:
    kids = children_of.get(record["rel"], [])
    body = [
        render_diagnostics(record.get("diagnostics") or []),
        '<dl class="kv">',
        f"<dt>Caminho</dt><dd><code>{esc(record['rel'])}</code></dd>",
        f"<dt>Fases</dt><dd>{render_phases(record.get('phases'))}</dd>",
        f"<dt>Fase atual</dt><dd>{esc(record.get('current_phase') or ABSENT) if record.get('current_phase') else field_or_absent(None)}</dd>",
        f"<dt>Handbook</dt><dd>{render_handbook(record.get('handbook'))}</dd>",
        f"<dt>Dependências</dt><dd>{render_deps(record.get('depends_on'))}</dd>",
        f"<dt>Tasks</dt><dd>{render_tasks_list(record.get('tasks'))}</dd>",
        "</dl>",
    ]
    if kids:
        nested = "".join(render_package(child, children_of) for child in kids)
        body.append(f'<div class="children">{nested}</div>')
    title = record.get("title")
    title_html = f'<span class="ptitle">{esc(title)}</span>' if title else ""
    return (
        f'<details class="pkg" data-id="{esc(record["id"])}" data-rel="{esc(record["rel"])}">'
        f"<summary><span class=\"pid\">{esc(record['id'])}</span>{title_html}{presence_chip(record)}</summary>"
        f'<div class="body">{"".join(body)}</div></details>'
    )


def graph_layout(packages: list[dict]) -> tuple[dict[str, tuple[float, float]], int, int]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in packages:
        top = record["rel"].split("/")[0] if record["rel"] != "." else record["id"]
        groups[top].append(record)
    pos: dict[str, tuple[float, float]] = {}
    y = 48.0
    width = 1180.0
    cols = 6
    col_w = 180.0
    row_h = 30.0
    left = 70.0
    for group in sorted(groups):
        items = groups[group]
        rows = max(1, (len(items) + cols - 1) // cols)
        for i, record in enumerate(items):
            col = i % cols
            row = i // cols
            pos[record["rel"]] = (left + col * col_w + col_w / 2, y + row * row_h + 12)
        y += rows * row_h + 28
    return pos, int(width), int(y + 20)


def render_graph(packages: list[dict], edges: list[dict]) -> str:
    if not packages:
        return f'<p class="absent">{esc(ABSENT)}</p>'
    pos, width, height = graph_layout(packages)
    parts = [
        f'<svg class="qg-graph" viewBox="0 0 {width} {height}" width="100%" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace,Menlo,monospace" font-size="11">',
        "<defs>",
        '<marker id="m-depends_on" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M0,0 L8,4 L0,8 z" fill="#0E9F6E"/></marker>',
        '<marker id="m-hierarchy" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M0,0 L8,4 L0,8 z" fill="#161815"/></marker>',
        "</defs>",
    ]
    for edge in edges:
        if edge["src"] not in pos or edge["dst"] not in pos:
            continue
        x1, y1 = pos[edge["src"]]
        x2, y2 = pos[edge["dst"]]
        dx = x2 - x1
        cx1 = x1 + dx * 0.35
        cx2 = x1 + dx * 0.65
        dash = "2 3" if edge["kind"] == EDGE_DEPENDS else ""
        color = "#0E9F6E" if edge["kind"] == EDGE_DEPENDS else "#161815"
        width_s = "1.2" if edge["kind"] == EDGE_DEPENDS else "1.5"
        parts.append(
            f'<path class="e e-{esc(edge["kind"])}" data-a="{esc(edge["src"])}" data-b="{esc(edge["dst"])}" '
            f'd="M{x1:.0f},{y1:.0f} C{cx1:.0f},{y1:.0f} {cx2:.0f},{y2:.0f} {x2:.0f},{y2:.0f}" '
            f'fill="none" stroke="{color}" stroke-width="{width_s}" stroke-dasharray="{dash}" '
            f'marker-end="url(#m-{esc(edge["kind"])})">'
            f'<title>{esc(edge["src"])} → {esc(edge["dst"])} · {esc(edge["kind"])}</title></path>'
        )
    for record in packages:
        if record["rel"] not in pos:
            continue
        x, y = pos[record["rel"]]
        nw = 96 if len(record["id"]) <= 16 else 120
        label = record["id"] if len(record["id"]) <= 18 else record["id"][:17] + "…"
        stroke = "#C2493F" if record.get("presence") != "ok" else "#161815"
        parts.append(
            f'<g class="n" data-id="{esc(record["rel"])}" tabindex="0">'
            f'<rect x="{x - nw / 2:.0f}" y="{y - 11:.0f}" width="{nw:.0f}" height="22" rx="2" '
            f'fill="#FFFFFC" stroke="{stroke}" stroke-width="1.2"/>'
            f'<text x="{x:.0f}" y="{y + 4:.0f}" text-anchor="middle" fill="#161815">{esc(label)}</text>'
            f'<title>{esc(record["id"])} · {esc(record["rel"])}</title></g>'
        )
    parts.append("</svg>")
    return "".join(parts)


def render_sprint(sprint: dict) -> str:
    diags = render_diagnostics(sprint.get("diagnostics") or [])
    items = sprint.get("items") or []
    if not items:
        metro = f'<p class="absent">{esc(ABSENT)}</p>'
    else:
        stations = []
        for item in items:
            state = item.get("state") or "queued"
            note = f'<div class="note">{esc(item["note"])}</div>' if item.get("note") else ""
            missing = "" if item.get("present") else f'<div class="note">{esc(ABSENT)} neste recorte</div>'
            stations.append(
                f'<div class="est {esc(state)}"><div class="rail"><div class="dot"></div><div class="line"></div></div>'
                f'<div class="info"><div class="nome">{esc(item["id"])}'
                f'<span class="tag">{esc(state)}</span></div>{note}{missing}</div></div>'
            )
        metro = f'<figure class="fig" data-fig="sprint · composição humana"><div class="metro">{"".join(stations)}</div></figure>'
    nxt = ""
    if sprint.get("next"):
        nxt = (
            f'<div class="next"><span class="lab">Próxima ação</span>'
            f'<span>{esc(sprint["next"])}</span></div>'
        )
    return f'{diags}{nxt}{metro}<p class="counts">Aba de operação. Não é autoridade de estado das specs.</p>'


FOCUS_JS = """
(function () {
  var svg = document.querySelector("svg.qg-graph");
  if (!svg) return;
  var edges = [].slice.call(svg.querySelectorAll("path.e"));
  var nodes = [].slice.call(svg.querySelectorAll("g.n"));
  function foco(id) {
    if (!id) {
      svg.classList.remove("foco");
      edges.forEach(function (e) { e.classList.remove("on"); });
      nodes.forEach(function (n) { n.classList.remove("on"); });
      return;
    }
    svg.classList.add("foco");
    var viz = {};
    viz[id] = 1;
    edges.forEach(function (e) {
      var on = e.getAttribute("data-a") === id || e.getAttribute("data-b") === id;
      e.classList.toggle("on", on);
      if (on) { viz[e.getAttribute("data-a")] = 1; viz[e.getAttribute("data-b")] = 1; }
    });
    nodes.forEach(function (n) { n.classList.toggle("on", !!viz[n.getAttribute("data-id")]); });
  }
  var pinned = null;
  nodes.forEach(function (n) {
    n.addEventListener("mouseenter", function () { if (!pinned) foco(n.getAttribute("data-id")); });
    n.addEventListener("mouseleave", function () { if (!pinned) foco(null); });
    n.addEventListener("click", function () {
      var id = n.getAttribute("data-id");
      pinned = (pinned === id) ? null : id;
      foco(pinned);
    });
  });
})();
"""


NAV_JS = """
(function () {
  function select(group, name) {
    document.querySelectorAll('[data-tab-group="' + group + '"]').forEach(function (btn) {
      btn.setAttribute("aria-selected", btn.getAttribute("data-tab") === name ? "true" : "false");
    });
    document.querySelectorAll('[data-panel-group="' + group + '"]').forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-panel") !== name;
    });
  }
  document.querySelectorAll("[data-tab]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      select(btn.getAttribute("data-tab-group"), btn.getAttribute("data-tab"));
    });
  });
})();
"""


def render_html(data: dict) -> str:
    packages = data["packages"]
    children_of: dict[str, list[dict]] = defaultdict(list)
    roots: list[dict] = []
    for record in packages:
        parent = record.get("parent")
        if parent and any(other["rel"] == parent for other in packages):
            children_of[parent].append(record)
        else:
            roots.append(record)
    for key in children_of:
        children_of[key].sort(key=lambda r: r["rel"])
    roots.sort(key=lambda r: r["rel"])

    task_tree = "".join(render_package(record, children_of) for record in roots)
    if not task_tree:
        task_tree = f'<p class="absent">{esc(ABSENT)}</p>'

    unreg_html = ""
    if data["unregistered"]:
        cards = []
        for item in data["unregistered"]:
            contents = item.get("contents") or []
            has_what = ", ".join(contents) if contents else ABSENT
            gate = ""
            if item.get("has_run_sh"):
                gate = (
                    '<p class="gate">Contém <code>run.sh</code>. Se esta pasta for movida ou '
                    "renomeada, quebra o script que o package.json do consumidor executa "
                    "por caminho relativo — gate de release.</p>"
                )
            cards.append(
                f'<article class="unreg" data-unregistered="{esc(item["rel"])}" data-qg-kind="unregistered">'
                f'<div class="kind">pasta sem registro · não é pacote</div>'
                f"<h3><code>{esc(item['rel'])}</code></h3>"
                f"<p>Não contém <code>status.json</code>. Não é pacote incompatível: "
                f"não chegou a ser pacote.</p>"
                f"<p>Contém: {esc(has_what)}.</p>"
                f"<p>Se esta pasta é um pacote, escreva <code>status.json</code> aqui "
                f"(id, route, phase_budget, confidence, current_phase, "
                f"decision.prd_status=gathering). Se é acervo de outro pacote, "
                f"o registro mora na pasta da mãe.</p>"
                f"{gate}</article>"
            )
        unreg_html = (
            f'<section class="unreg-list" data-qg-unregistered="1">'
            f'<p class="counts" data-qg-unregistered-count="{len(data["unregistered"])}">'
            f'{len(data["unregistered"])} pastas sem registro</p>'
            f"{''.join(cards)}</section>"
        )

    graph_html = (
        f'<figure class="fig graph-wrap" data-fig="grafo · relações registradas">'
        f'{render_graph(packages, data["edges"])}</figure>'
        f'<div class="legend"><span class="hier"><i></i>hierarquia (children_source)</span>'
        f'<span class="dep"><i></i>dependência (depends_on)</span>'
        f"<span>referência histórica: sem campo neste recorte</span>"
        f"<span>prioridade de sprint: aba Sprint, quando existir</span></div>"
    )

    sprint_tab = ""
    sprint_panel = ""
    if data.get("sprint") is not None:
        sprint_tab = (
            '<button class="tab" type="button" data-tab-group="main" data-tab="sprint" aria-selected="false">Sprint</button>'
        )
        sprint_panel = (
            f'<section class="panel" data-panel-group="main" data-panel="sprint" hidden>'
            f'<header class="cover"><div class="kicker">Operação específica</div>'
            f'<h1>{esc(data["sprint"].get("name") or "Sprint")}</h1></header>'
            f'{render_sprint(data["sprint"])}</section>'
        )

    scope_label = "todas as specs tipadas" if data["scope"] == "all" else ", ".join(data["scope"])
    payload = script_safe_dumps(data)
    css = load_board_css() + "\n" + QG_LAYOUT_CSS
    n_pkg = len(packages)
    n_unreg = len(data["unregistered"])
    n_edge = len(data["edges"])
    n_dep = sum(1 for e in data["edges"] if e["kind"] == EDGE_DEPENDS)
    n_hier = sum(1 for e in data["edges"] if e["kind"] == EDGE_HIERARCHY)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QG · Superflow</title>
<!--
  QG — snapshot gerado. Não edite o HTML para atualizar estado.
  Regenere a partir dos status.json. Template de apresentação: board.html do plugin.
-->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div class="page">
  <div class="doc-plate">
    <span>QG · {esc(scope_label)}</span>
    <span>gerado {esc(data["generated_at"])} · base {esc(data["read_base"])}</span>
  </div>
  <header class="cover">
    <div class="kicker">Quartel-general · snapshot</div>
    <h1>O que existe neste recorte</h1>
    <p class="next"><span class="lab">Isto não é ao vivo</span>
      Retrato do disco no carimbo acima. Tasks e Graph leem o mesmo censo.</p>
  </header>
  <nav class="tabs">
    <button class="tab" type="button" data-tab-group="main" data-tab="mapa" aria-selected="true">Mapa</button>
    {sprint_tab}
  </nav>
  <section class="panel" data-panel-group="main" data-panel="mapa">
    <div class="subtabs">
      <button class="subtab" type="button" data-tab-group="mapa" data-tab="tasks" aria-selected="true">Tasks</button>
      <button class="subtab" type="button" data-tab-group="mapa" data-tab="graph" aria-selected="false">Graph</button>
    </div>
    <p class="counts" data-qg-counts="1">{n_pkg} pacotes · {n_unreg} pastas sem registro · {n_edge} arestas ({n_hier} hierarquia, {n_dep} depends_on)</p>
    <section class="panel" data-panel-group="mapa" data-panel="tasks">
      {task_tree}
      {unreg_html}
    </section>
    <section class="panel" data-panel-group="mapa" data-panel="graph" hidden>
      {graph_html}
    </section>
  </section>
  {sprint_panel}
  <footer>
    <span>superflow · qg</span>
    <span>fonte: status.json · destino {esc(data["dest_name"])} · projeção, não fonte de verdade</span>
  </footer>
</div>
<script type="application/json" id="qg-snapshot">
{payload}
</script>
<script>
{NAV_JS}
{FOCUS_JS}
</script>
</body>
</html>
"""


def resolve_specs_root(start: Path, cfg, specs_override: str | None) -> Path:
    if specs_override:
        return Path(specs_override).expanduser()
    if cfg.specs_root is not None:
        return cfg.specs_root
    if start.name == "specs" or (start / "status.json").exists() or any(start.glob("*/status.json")):
        return start
    raise SystemExit("CONTRACT: could not resolve a specs root (pass --specs)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "start",
        nargs="?",
        default=".",
        help="Walk-up start for .superflow/ (CLI → env → parents → default).",
    )
    parser.add_argument("--superflow-dir", help="Runtime .superflow directory. Never version a machine path.")
    parser.add_argument("--specs", help="Specs root. Default comes from config.specs.")
    parser.add_argument("--dest", help="Output directory. Default is the resolved .superflow/qg/.")
    parser.add_argument("--out", default="qg.html", help="File name inside dest. Default qg.html.")
    parser.add_argument("--scope", help="Comma-separated package ids or relative paths. Default: everything typed.")
    parser.add_argument("--scope-file", help="JSON list or newline list of ids/paths.")
    parser.add_argument(
        "--sprint",
        nargs="?",
        const="",
        default=None,
        help="Include the Sprint tab. Optional path to a sprint JSON (human composition).",
    )
    parser.add_argument("--stamp", help="Declared date stamp (YYYY-MM-DD). Default: today.")
    args = parser.parse_args()

    start = Path(args.start).expanduser()
    if not start.exists():
        print(f"CONTRACT: path does not exist: {start}", file=sys.stderr)
        return EXIT_CONTRACT

    cfg = V.load_superflow_config(start, args.superflow_dir)
    V.apply_superflow_config(cfg)
    try:
        specs_root = resolve_specs_root(start, cfg, args.specs)
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_CONTRACT
    if not specs_root.exists():
        print("CONTRACT: specs root does not exist", file=sys.stderr)
        return EXIT_CONTRACT

    dest = V.resolve_qg_dir(cfg, args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    out_path = dest / args.out

    scope = parse_scope(args.scope, Path(args.scope_file) if args.scope_file else None)
    sprint = None
    if args.sprint is not None:
        sprint_path = Path(args.sprint) if args.sprint else None
        sprint = load_sprint(sprint_path) if sprint_path else {
            "name": "Sprint",
            "items": [],
            "diagnostics": [],
            "next": None,
        }

    stamp = args.stamp or date.today().isoformat()
    read_base = git_read_base(specs_root)
    data = snapshot(
        specs_root,
        scope=scope,
        stamp=stamp,
        read_base=read_base,
        sprint=sprint,
        dest_name=out_path.name,
    )
    html_text = render_html(data)
    if re.search(r"/Users/[^/\s]+/", html_text):
        print("CONTRACT: generated HTML must not contain a machine-absolute path", file=sys.stderr)
        return EXIT_CONTRACT
    out_path.write_text(html_text, encoding="utf-8")
    print(out_path.as_posix())
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
