#!/usr/bin/env python3
"""Write the consolidated Superflow status feed.

One census walks the scanned tree and writes `.superflow/status.json` plus
`.superflow/status.md`. Later HTML tools read that feed. They do not walk
package `status.json` files again.

Exit codes: 0 wrote the feed, 1 contract error.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATE = SCRIPT_DIR / "validate_superflow.py"

ABSENT = "Não contém"
CONTRACT_PLAN = "implementation_plan.json"

KIND_PACKAGE = "package"
KIND_DECLARED_CHILD = "declared_child"
KIND_UNREGISTERED = "unregistered"

EDGE_HIERARCHY = "hierarchy"
EDGE_DEPENDS = "depends_on"

EXIT_OK = 0
EXIT_CONTRACT = 1

FEED_JSON = "status.json"
FEED_MD = "status.md"


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
    labels: list[str] = []
    for child in visible_children(path):
        labels.append(f"{child.name}/" if child.is_dir() else child.name)
    return labels


def folder_is_empty(path: Path) -> bool:
    return not visible_children(path)


def holds_packages(path: Path) -> bool:
    return any(child.is_dir() and (child / "status.json").exists() for child in visible_children(path))


def contains_run_sh(path: Path) -> bool:
    try:
        return any(child.is_file() for child in path.rglob("run.sh"))
    except OSError:
        return False


def find_unregistered_folders(specs_root: Path, package_rels: set[str]) -> list[dict]:
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


def annotate_duplicates(records: list[dict]) -> list[dict]:
    projected = [dict(record) for record in records]
    id_hits: dict[str, list[dict]] = defaultdict(list)
    for record in projected:
        diags = [d for d in (record.get("diagnostics") or []) if not str(d).startswith("id duplicado:")]
        record["diagnostics"] = diags
        if record.get("presence") == "incompatible" and not diags:
            record["presence"] = "ok"
        id_hits[record["id"]].append(record)
    for record in projected:
        hits = id_hits[record["id"]]
        if len(hits) < 2:
            continue
        record["diagnostics"] = list(record.get("diagnostics") or []) + [f"id duplicado: {record['id']}"]
        if record["presence"] == "ok":
            record["presence"] = "incompatible"
    return projected


def census(specs_root: Path) -> dict:
    packages: dict[str, dict] = {}
    declared_from: dict[str, str] = {}

    for status_file in sorted(specs_root.rglob("status.json")):
        rel_parts = status_file.resolve().relative_to(specs_root.resolve()).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
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

    scoped = annotate_duplicates(list(packages.values()))
    scoped.sort(key=lambda r: r["rel"])
    unregistered.sort(key=lambda r: r["rel"])

    id_hits: dict[str, list[dict]] = defaultdict(list)
    for record in scoped:
        id_hits[record["id"]].append(record)

    edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    by_rel = {record["rel"]: record for record in scoped}

    for record in scoped:
        src = record["rel"]
        source = record.get("children_source")
        if source:
            mother = specs_root / record["rel"]
            children, _ = declared_child_dirs(mother, source, specs_root)
            for child in children:
                child_rel = posix_rel(child, specs_root)
                other = by_rel.get(child_rel)
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


def resolve_specs_root(start: Path, cfg, specs_override: str | None) -> Path:
    if specs_override:
        return Path(specs_override).expanduser()
    if cfg.specs_root is not None:
        return cfg.specs_root
    if start.name == "specs" or (start / "status.json").exists() or any(start.glob("*/status.json")):
        return start
    raise SystemExit("CONTRACT: could not resolve a specs root (pass --specs)")


def resolve_feed_dir(cfg, start: Path) -> Path:
    if cfg.superflow_dir is not None:
        return cfg.superflow_dir
    root = start.resolve()
    if root.name == "specs" and not (root / "status.json").exists():
        root = root.parent
    return root / ".superflow"


def feed_paths(feed_dir: Path) -> tuple[Path, Path]:
    return feed_dir / FEED_JSON, feed_dir / FEED_MD


def dump_feed(feed: dict) -> str:
    return json.dumps(feed, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def render_status_md(feed: dict) -> str:
    packages = feed["packages"]
    unregistered = feed["unregistered"]
    edges = feed["edges"]
    lines = [
        "# Superflow status",
        "",
        (
            f"gerado {feed['generated_at']} · base {feed['read_base']} · "
            f"{len(packages)} pacotes · {len(unregistered)} pastas sem registro"
        ),
        "",
        "## Pacotes",
        "",
    ]
    if not packages:
        lines.append(f"- {ABSENT}")
    for record in packages:
        phase = record.get("current_phase") or ABSENT
        lines.append(
            f"- `{record['id']}` · `{record['rel']}` · {record.get('presence') or ABSENT} · {phase}"
        )
    lines.extend(["", "## Sem registro", ""])
    if not unregistered:
        lines.append(f"- {ABSENT}")
    for item in unregistered:
        contents = ", ".join(item.get("contents") or []) or ABSENT
        lines.append(f"- `{item['rel']}` · {contents}")
    lines.extend(["", "## Arestas", ""])
    if not edges:
        lines.append(f"- {ABSENT}")
    for edge in edges:
        lines.append(f"- `{edge['src']}` → `{edge['dst']}` · {edge['kind']}")
    lines.append("")
    return "\n".join(lines)


def atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def write_feed(
    specs_root: Path,
    feed_dir: Path,
    *,
    stamp: str,
    read_base: str,
) -> dict:
    counted = census(specs_root)
    feed = {
        "generated_at": stamp,
        "read_base": read_base,
        "packages": counted["packages"],
        "unregistered": counted["unregistered"],
        "edges": counted["edges"],
    }
    feed_dir.mkdir(parents=True, exist_ok=True)
    json_path, md_path = feed_paths(feed_dir)
    json_tmp = json_path.with_name(f"{json_path.name}.tmp")
    md_tmp = md_path.with_name(f"{md_path.name}.tmp")
    json_tmp.write_text(dump_feed(feed), encoding="utf-8")
    md_tmp.write_text(render_status_md(feed), encoding="utf-8")
    json_tmp.replace(json_path)
    md_tmp.replace(md_path)
    return feed


def load_feed(path: Path) -> dict:
    data, err = read_json(path)
    if err or not isinstance(data, dict):
        raise SystemExit("CONTRACT: .superflow/status.json missing or incompatible")
    packages = data.get("packages")
    unregistered = data.get("unregistered")
    edges = data.get("edges")
    if not isinstance(packages, list) or not isinstance(unregistered, list) or not isinstance(edges, list):
        raise SystemExit("CONTRACT: feed must carry packages, unregistered, and edges lists")
    generated_at = data.get("generated_at")
    read_base = data.get("read_base")
    if not isinstance(generated_at, str) or not generated_at.strip():
        raise SystemExit("CONTRACT: feed generated_at must be a string")
    if not isinstance(read_base, str) or not read_base.strip():
        raise SystemExit("CONTRACT: feed read_base must be a string")
    parsed_packages = []
    for item in packages:
        if not isinstance(item, dict):
            raise SystemExit("CONTRACT: feed package must be an object")
        pkg_id = item.get("id")
        rel = item.get("rel")
        if not isinstance(pkg_id, str) or not pkg_id.strip():
            raise SystemExit("CONTRACT: feed package id must be a non-empty string")
        if not isinstance(rel, str) or not rel.strip():
            raise SystemExit("CONTRACT: feed package rel must be a non-empty string")
        parsed_packages.append(item)
    parsed_unregistered = []
    for item in unregistered:
        if not isinstance(item, dict):
            raise SystemExit("CONTRACT: feed unregistered item must be an object")
        rel = item.get("rel")
        if not isinstance(rel, str) or not rel.strip():
            raise SystemExit("CONTRACT: feed unregistered rel must be a non-empty string")
        parsed_unregistered.append(item)
    parsed_edges = []
    for item in edges:
        if not isinstance(item, dict):
            raise SystemExit("CONTRACT: feed edge must be an object")
        src = item.get("src")
        dst = item.get("dst")
        kind = item.get("kind")
        if not isinstance(src, str) or not isinstance(dst, str) or not isinstance(kind, str):
            raise SystemExit("CONTRACT: feed edge src, dst, and kind must be strings")
        parsed_edges.append(item)
    return {
        "generated_at": generated_at,
        "read_base": read_base,
        "packages": parsed_packages,
        "unregistered": parsed_unregistered,
        "edges": parsed_edges,
    }


def project_feed(feed: dict, scope: set[str] | None) -> dict:
    packages = annotate_duplicates(close_scope(list(feed["packages"]), scope))
    keep = {record["rel"] for record in packages}
    unregistered = list(feed["unregistered"])
    if scope:
        unregistered = [
            item
            for item in unregistered
            if item["rel"] in scope
            or any(item["rel"] == token or item["rel"].startswith(token.rstrip("/") + "/") for token in scope)
        ]
    edges = [
        edge
        for edge in feed["edges"]
        if edge.get("src") in keep and edge.get("dst") in keep
    ]
    packages.sort(key=lambda r: r["rel"])
    unregistered.sort(key=lambda r: r["rel"])
    edges.sort(key=lambda e: (e["kind"], e["src"], e["dst"]))
    return {
        "generated_at": feed["generated_at"],
        "read_base": feed["read_base"],
        "packages": packages,
        "unregistered": unregistered,
        "edges": edges,
    }


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

    feed_dir = resolve_feed_dir(cfg, start)
    stamp = args.stamp or date.today().isoformat()
    read_base = git_read_base(specs_root)
    feed = write_feed(specs_root, feed_dir, stamp=stamp, read_base=read_base)
    json_path, md_path = feed_paths(feed_dir)
    print(json_path.as_posix())
    print(md_path.as_posix())
    print(f"{len(feed['packages'])} packages")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
