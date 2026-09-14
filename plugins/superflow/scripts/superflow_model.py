"""Read and validate Superflow sources with explicit least-privilege boundaries."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
import yaml

CONFIG_PATH = ".superflow/config.json"
PROJECTION_SOURCE_NAMES = {"status.md"}
READY_SOURCE_NAMES = {"status.md", "PRD.md", "SPEC.md", "plan.json"}
SOURCE_NAMES = PROJECTION_SOURCE_NAMES | READY_SOURCE_NAMES
STATUS_FIELDS = {"id", "title", "status", "depends_on", "waiting_for"}
TASK_FIELDS = {"id", "task", "status", "depends_on", "acceptance"}


class ContentError(ValueError):
    """Invalid user-authored content."""


class SourceError(RuntimeError):
    """Operational source failure; publication must preserve the previous output."""


class StatusLoader(yaml.SafeLoader):
    pass


StatusLoader.yaml_implicit_resolvers = {
    key: [(tag, pattern) for tag, pattern in values
          if tag != "tag:yaml.org,2002:timestamp"]
    for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ContentError("As chaves devem ser strings.")
        if key in result:
            raise ContentError("Chave repetida: " + key)
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


StatusLoader.add_constructor("tag:yaml.org,2002:map", unique_mapping)


def parse_status(text):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ContentError("status.md precisa começar com frontmatter ---")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ContentError("Frontmatter sem delimitador final.")
    header = "".join(lines[1:end])
    try:
        for token in yaml.scan(header):
            if isinstance(token, (yaml.tokens.AnchorToken, yaml.tokens.AliasToken,
                                  yaml.tokens.TagToken)):
                raise ContentError("Aliases, anchors e tags explícitas não são permitidos.")
        value = yaml.load(header, Loader=StatusLoader)
    except yaml.YAMLError as exc:
        raise ContentError("YAML inválido: " + str(exc)) from exc
    if not isinstance(value, dict):
        raise ContentError("Frontmatter deve ser um objeto.")
    return value, "".join(lines[end + 1:])


def parse_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContentError("Chave JSON repetida: " + key)
            result[key] = value
        return result
    try:
        return json.loads(
            text,
            object_pairs_hook=pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ContentError("Constante JSON inválida: " + value)),
        )
    except (ValueError, TypeError) as exc:
        raise ContentError(str(exc)) from exc


def text_value(value, field):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ContentError(field + " deve ser uma string não vazia.")
    return value.strip()


def string_list(value, field):
    if not isinstance(value, list):
        raise ContentError(field + " deve ser uma lista de strings.")
    normalized = [text_value(item, field) for item in value]
    if len(normalized) != len(set(normalized)):
        raise ContentError(field + " contém valores repetidos.")
    return normalized


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def diagnostic(path, code, message, severity="error"):
    return {"path": path, "code": code, "message": message, "severity": severity}


def resolve_specs_root(root):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise SourceError("Raiz inexistente: " + str(root))
    config_file = root / CONFIG_PATH
    config = {}
    if config_file.exists():
        if config_file.is_symlink():
            raise SourceError("Configuração não pode ser um symlink.")
        try:
            config = parse_json(config_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ContentError) as exc:
            raise SourceError("Configuração inválida: " + str(exc)) from exc
        if not isinstance(config, dict) or set(config) - {"specs_root", "proof_cmd", "ship_cmd"}:
            raise SourceError("Configuração possui campos desconhecidos ou não é objeto.")
        for key, value in config.items():
            text_value(value, key)
    relative = config.get("specs_root", "specs")
    if Path(relative).is_absolute():
        raise SourceError("specs_root deve ser relativo ao repositório.")
    specs = (root / relative).resolve()
    try:
        specs.relative_to(root)
    except ValueError as exc:
        raise SourceError("specs_root deve ficar dentro do repositório.") from exc
    if specs == root:
        raise SourceError("specs_root deve ser uma subpasta do repositório.")
    if specs.exists() and not specs.is_dir():
        raise SourceError("specs_root não é um diretório.")
    return root, specs, config


def read_sources(root):
    """Read the projection boundary: config plus files named exactly status.md."""
    root, specs, _ = resolve_specs_root(root)
    sources = {}
    config_file = root / CONFIG_PATH
    if config_file.exists():
        sources[CONFIG_PATH] = config_file.read_bytes()
    try:
        for directory, dirs, files in os.walk(specs, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".")
                             and d not in {"node_modules", "__pycache__"}
                             and not (Path(directory) / d).is_symlink())
            if "status.md" not in files:
                continue
            path = Path(directory) / "status.md"
            if path.is_symlink():
                raise SourceError("Fonte não pode ser symlink: " + str(path))
            sources[path.relative_to(root).as_posix()] = path.read_bytes()
    except (OSError, UnicodeError) as exc:
        raise SourceError("Não foi possível ler os status: " + str(exc)) from exc
    return sources


def fingerprint(sources):
    digest = hashlib.sha256()
    for path, value in sorted(sources.items()):
        digest.update(path.encode("utf-8") + b"\0" + hashlib.sha256(value).digest())
    return digest.hexdigest()


def ensure_unchanged(root, sources):
    if fingerprint(read_sources(root)) != fingerprint(sources):
        raise SourceError("SOURCE_CHANGED: status alterados durante a leitura; gere novamente.")


def validate_status(data, body, path):
    unknown = set(data) - STATUS_FIELDS
    if unknown:
        raise ContentError("Campos desconhecidos: " + ", ".join(sorted(unknown)))
    identifier = text_value(data.get("id"), "id")
    title = text_value(data.get("title"), "title")
    status = text_value(data.get("status"), "status")
    if status not in {"pending", "done"}:
        raise ContentError("status deve ser pending ou done.")
    dependencies = data.get("depends_on", [])
    if not isinstance(dependencies, list):
        raise ContentError("depends_on deve ser uma lista de objetos id/reason.")
    normalized_dependencies = []
    seen = set()
    for item in dependencies:
        if not isinstance(item, dict) or set(item) != {"id", "reason"}:
            raise ContentError("Cada depends_on deve conter exatamente id e reason.")
        target = text_value(item["id"], "depends_on.id")
        reason = text_value(item["reason"], "depends_on.reason")
        if target in seen:
            raise ContentError("depends_on contém destino repetido: " + target)
        seen.add(target)
        normalized_dependencies.append({"id": target, "reason": reason})
    waiting = data.get("waiting_for")
    if waiting is not None:
        waiting = text_value(waiting, "waiting_for")
    if status == "done" and waiting:
        raise ContentError("Spec done não pode manter waiting_for.")
    return {
        "id": identifier,
        "title": title,
        "status": status,
        "path": Path(path).parent.as_posix(),
        "depends_on": normalized_dependencies,
        "waiting_for": waiting,
        "body_md": body,
    }


def find_cycles(graph):
    color, cycles = {}, []
    for start in graph:
        if color.get(start):
            continue
        active, positions = [start], {start: 0}
        color[start] = 1
        stack = [(start, iter(graph[start]))]
        while stack:
            node, edges = stack[-1]
            target = next(edges, None)
            if target is None:
                color[node] = 2
                stack.pop()
                positions.pop(node, None)
                active.pop()
            elif target in graph and color.get(target, 0) == 0:
                color[target] = 1
                positions[target] = len(active)
                active.append(target)
                stack.append((target, iter(graph[target])))
            elif color.get(target) == 1:
                cycles.append(active[positions[target]:] + [target])
    return cycles


def validate_plan(value):
    if not isinstance(value, dict) or set(value) != {"tasks"} or not isinstance(value["tasks"], list):
        raise ContentError("plan.json deve conter somente tasks, uma lista.")
    tasks, index = [], {}
    for raw in value["tasks"]:
        if not isinstance(raw, dict) or set(raw) != TASK_FIELDS:
            raise ContentError("Task deve conter exatamente id, task, status, depends_on e acceptance.")
        task = {
            "id": text_value(raw["id"], "task.id"),
            "task": text_value(raw["task"], "task.task"),
            "status": text_value(raw["status"], "task.status"),
            "depends_on": string_list(raw["depends_on"], "task.depends_on"),
            "acceptance": string_list(raw["acceptance"], "task.acceptance"),
        }
        if task["status"] not in {"pending", "done"}:
            raise ContentError("Status de task deve ser pending ou done.")
        if not task["acceptance"]:
            raise ContentError("Task precisa de pelo menos um aceite.")
        if task["id"] in index:
            raise ContentError("ID de task repetido: " + task["id"])
        index[task["id"]] = task
        tasks.append(task)
    for task in tasks:
        for dependency in task["depends_on"]:
            if dependency not in index or dependency == task["id"]:
                raise ContentError("Dependência de task ausente ou própria: " + dependency)
            if task["status"] == "done" and index[dependency]["status"] != "done":
                raise ContentError("Task done requer predecessora done: " + dependency)
    if find_cycles({key: value["depends_on"] for key, value in index.items()}):
        raise ContentError("Ciclo de dependências entre tasks.")
    return tasks


def validate_ready(root, spec_reference):
    """Read only the four files explicitly allowed for an accepted execution."""
    root, specs, _ = resolve_specs_root(root)
    reference = Path(spec_reference)
    target = reference.resolve() if reference.is_absolute() else (specs / reference).resolve()
    try:
        target.relative_to(specs)
    except ValueError as exc:
        raise SourceError("Spec precisa ficar dentro de specs_root.") from exc
    if not target.is_dir() or target.is_symlink():
        raise SourceError("Spec inexistente ou inválida: " + str(target))
    contents = {}
    for name in sorted(READY_SOURCE_NAMES):
        path = target / name
        if not path.is_file() or path.is_symlink():
            raise ContentError("Execução aceita exige " + name + ".")
        try:
            contents[name] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise SourceError("Não foi possível ler " + name + ": " + str(exc)) from exc
        if not contents[name].strip():
            raise ContentError(name + " não pode estar vazio.")
    status, body = parse_status(contents["status.md"])
    validate_status(status, body, str(target / "status.md"))
    validate_plan(parse_json(contents["plan.json"]))
    return target


def build_snapshot(root, sources=None):
    root = Path(root).expanduser().resolve()
    sources = read_sources(root) if sources is None else sources
    records, diagnostics = [], []
    for path, raw in sorted(sources.items()):
        if not path.endswith("/status.md"):
            continue
        try:
            data, body = parse_status(raw.decode("utf-8"))
            records.append(validate_status(data, body, path))
        except (ContentError, UnicodeError) as exc:
            diagnostics.append(diagnostic(path, "INVALID_STATUS", str(exc)))

    by_id, by_path = {}, {record["path"]: record for record in records}
    for record in records:
        if record["id"] in by_id:
            diagnostics.append(diagnostic(record["path"], "DUPLICATE_ID", "ID repetido: " + record["id"]))
        else:
            by_id[record["id"]] = record
    for record in records:
        parent = Path(record["path"]).parent
        while parent.as_posix() not in by_path and parent != parent.parent:
            parent = parent.parent
        record["parent_id"] = by_path[parent.as_posix()]["id"] if parent.as_posix() in by_path else None
        record["blockers"] = []
        if record["waiting_for"]:
            record["blockers"].append({"kind": "waiting", "reason": record["waiting_for"]})
        for dependency in record["depends_on"]:
            target = by_id.get(dependency["id"])
            if target is None or target is record:
                diagnostics.append(diagnostic(
                    record["path"], "INVALID_DEPENDENCY",
                    "Dependência ausente ou própria: " + dependency["id"],
                ))
                record["blockers"].append({"kind": "dependency", **dependency})
            elif target["status"] != "done":
                record["blockers"].append({"kind": "dependency", **dependency})
                if record["status"] == "done":
                    diagnostics.append(diagnostic(
                        record["path"], "UNFINISHED_DEPENDENCY",
                        "Spec done depende de entrega pendente: " + dependency["id"],
                    ))
    graph = {record["id"]: [item["id"] for item in record["depends_on"]] for record in records}
    for cycle in find_cycles(graph):
        diagnostics.append(diagnostic("", "DEPENDENCY_CYCLE", " → ".join(cycle)))

    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    revision = result.stdout.strip() if result.returncode == 0 else None
    snapshot = {
        "schema_version": "superflow.feed.v3",
        "generated_at": utc_now(),
        "snapshot_id": fingerprint(sources),
        "source_revision": revision,
        "records": records,
        "diagnostics": diagnostics,
    }
    return snapshot, sources


def has_errors(snapshot):
    return any(item["severity"] == "error" for item in snapshot["diagnostics"])
