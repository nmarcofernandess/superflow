"""Read, validate and project spec sources. No project commands are executed."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
import yaml

OPEN_PHASES = {"inbox", "analyst", "build", "plan", "execute", "qa"}
TERMINAL_PHASES = {"done", "cancelled"}
FIELDS = {"id", "title", "phase", "state", "prd", "updated_at",
          "depends_on", "absorbed_by", "waiting_for", "archived", "evidence"}
TASK_FIELDS = {"id", "behavior", "files", "depends_on", "acceptance", "status", "evidence"}
SOURCE_NAMES = {"status.md", "PRD.md", "SPEC.md", "HANDBOOK.md", "plan.json"}
CONFIG_PATH = ".superflow/config.json"


class ContentError(ValueError):
    """Invalid source content; suitable for a diagnostic snapshot."""


class SourceError(RuntimeError):
    """An operational failure; never publish a partial snapshot."""


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
        return json.loads(text, object_pairs_hook=pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              ContentError("Constante JSON inválida: " + value)))
    except (ValueError, TypeError) as exc:
        raise ContentError(str(exc)) from exc


def text_value(value, field):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ContentError(field + " deve ser uma string não vazia.")
    return value


def strings(value, field):
    if not isinstance(value, list):
        raise ContentError(field + " deve ser uma lista de strings.")
    for item in value:
        text_value(item, field)
    if len(value) != len(set(value)):
        raise ContentError(field + " contém valores repetidos.")
    return value


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def diagnostic(path, code, message, severity="error"):
    return {"path": path, "code": code, "message": message, "severity": severity}


def reference_path(root, reference):
    """Return a local target or None for HTTPS; reject executable URL schemes."""
    text_value(reference, "referência")
    url = urlsplit(reference)
    if url.scheme == "https" and url.netloc:
        return None
    if url.scheme == "file":
        explicit_file = re.match(r"^file://(?:localhost)?/", reference, re.IGNORECASE)
        if not explicit_file or url.netloc not in ("", "localhost"):
            raise ContentError("Referência file deve usar file:/// ou file://localhost/.")
        target = Path(unquote(url.path))
        if not target.is_absolute():
            raise ContentError("Referência file precisa de caminho absoluto.")
        return target
    # A :line suffix is a local code reference, not a URL protocol.
    clean = re.sub(r":\d+(?:-\d+)?$", "", reference.split("#", 1)[0])
    if "://" in clean or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", clean):
        raise ContentError("Referência deve ser local ou HTTPS: " + reference)
    path = Path(unquote(clean))
    if path.is_absolute():
        raise ContentError("Use file:/// para uma referência local absoluta.")
    target = (root / path).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ContentError("Referência relativa fora do repositório: " + reference) from exc
    return target


def read_sources(root):
    """Capture one source collection, including optional PRDs and plans."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise SourceError("Raiz inexistente: " + str(root))
    config_file = root / CONFIG_PATH
    sources = {}
    config = {}
    try:
        if config_file.exists():
            if config_file.is_symlink():
                raise SourceError("Configuração não pode ser um symlink.")
            sources[CONFIG_PATH] = config_file.read_bytes()
            config = parse_json(sources[CONFIG_PATH].decode("utf-8"))
            if not isinstance(config, dict) or set(config) - {"specs_root", "proof_cmd", "ship_cmd"}:
                raise SourceError("Configuração possui campos desconhecidos ou não é objeto.")
            for key, value in config.items():
                text_value(value, key)
        relative_root = config.get("specs_root", "specs")
        if Path(relative_root).is_absolute():
            raise SourceError("specs_root deve ser relativo ao repositório.")
        specs = (root / relative_root).resolve()
        specs.relative_to(root)
        if specs == root:
            raise SourceError("specs_root deve ser uma subpasta do repositório.")
        if specs.exists() and not specs.is_dir():
            raise SourceError("specs_root não é um diretório.")
        for directory, dirs, files in os.walk(specs, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".")
                             and d not in {"node_modules", "__pycache__"}
                             and not (Path(directory) / d).is_symlink())
            for name in sorted(set(files) & SOURCE_NAMES):
                path = Path(directory) / name
                if path.is_symlink():
                    raise SourceError("Fonte não pode ser symlink: " + str(path))
                sources[path.relative_to(root).as_posix()] = path.read_bytes()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SourceError("Não foi possível ler as fontes: " + str(exc)) from exc
    return sources


def fingerprint(sources):
    digest = hashlib.sha256()
    for path, value in sorted(sources.items()):
        digest.update(path.encode("utf-8") + b"\0" + hashlib.sha256(value).digest())
    return digest.hexdigest()


def ensure_unchanged(root, sources):
    if fingerprint(read_sources(root)) != fingerprint(sources):
        raise SourceError("SOURCE_CHANGED: fontes alteradas durante a leitura; gere novamente.")


def validate_status(data, body, path):
    unknown = set(data) - FIELDS
    if unknown:
        raise ContentError("Campos desconhecidos: " + ", ".join(sorted(unknown)))
    for key in ("id", "title", "phase", "prd", "updated_at"):
        text_value(data.get(key), key)
    phase = data["phase"]
    if phase not in OPEN_PHASES | TERMINAL_PHASES:
        raise ContentError("Fase desconhecida: " + phase)
    if phase in OPEN_PHASES and (not isinstance(data.get("state"), str)
                                or data["state"] not in {"pending", "in_progress", "paused"}):
        raise ContentError("Fase aberta exige state pending/in_progress/paused.")
    if phase in TERMINAL_PHASES and "state" in data:
        raise ContentError("Fase terminal não possui state.")
    if data["prd"] not in {"gathering", "ready"}:
        raise ContentError("prd deve ser gathering ou ready.")
    if phase in {"build", "plan", "execute", "qa", "done"} and data["prd"] != "ready":
        raise ContentError("Esta fase exige PRD ready.")
    try:
        stamp = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("timezone ausente")
    except ValueError as exc:
        raise ContentError("updated_at precisa ser ISO-8601 com timezone.") from exc
    record = dict(data, path=Path(path).parent.as_posix(), body_md=body)
    record.setdefault("state", None)
    for key in ("depends_on", "evidence"):
        record[key] = strings(data.get(key, []), key)
    for key in ("absorbed_by", "waiting_for"):
        record[key] = text_value(data[key], key) if key in data else None
    record["archived"] = data.get("archived", False)
    if type(record["archived"]) is not bool:
        raise ContentError("archived deve ser boolean.")
    if record["waiting_for"] and (phase in TERMINAL_PHASES or record["state"] == "in_progress"):
        raise ContentError("Espera não combina com execução ativa ou fase terminal.")
    if (record["archived"] or record["absorbed_by"]) and record["state"] == "in_progress":
        raise ContentError("Spec arquivada/absorvida não pode estar em execução.")
    if phase in TERMINAL_PHASES and not record["evidence"]:
        raise ContentError("Fase terminal exige evidence da entrega ou decisão.")
    return record


def find_cycles(graph):
    """Iterative DFS avoids recursion limits on large collections."""
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


def validate_plan(value, record, prd):
    if not isinstance(value, dict) or set(value) != {"tasks"} or not isinstance(value["tasks"], list):
        raise ContentError("plan.json deve conter somente tasks, uma lista.")
    tasks = value["tasks"]
    index = {}
    for task in tasks:
        if not isinstance(task, dict):
            raise ContentError("Task deve ser objeto.")
        status = task.get("status")
        allowed = TASK_FIELDS | ({"skip_reason"} if status == "skipped" else set())
        if set(task) != allowed:
            raise ContentError("Task deve ter os sete campos documentados; skipped exige skip_reason.")
        for key in ("id", "behavior"):
            text_value(task[key], key)
        for key in ("files", "depends_on", "acceptance", "evidence"):
            strings(task[key], key)
        if not task["acceptance"] or any(not re.search(r"(?<!\w)" + re.escape(ac) + r"(?!\w)", prd)
                                         for ac in task["acceptance"]):
            raise ContentError("Task precisa referenciar um aceite existente no PRD.")
        if not isinstance(status, str) or status not in {"pending", "in_progress", "done", "skipped"}:
            raise ContentError("Status de task inválido.")
        if status == "skipped":
            text_value(task["skip_reason"], "skip_reason")
        if status == "done" and not task["evidence"]:
            raise ContentError("Task done precisa de evidence.")
        if status == "in_progress" and (
            record["phase"] != "execute" or record["state"] != "in_progress"
            or record["waiting_for"] or record["archived"] or record["absorbed_by"]
        ):
            raise ContentError("Task in_progress exige spec execute/in_progress disponível.")
        if task["id"] in index:
            raise ContentError("ID de task repetido: " + task["id"])
        index[task["id"]] = task
    for task in tasks:
        for dependency in task["depends_on"]:
            if dependency not in index or dependency == task["id"]:
                raise ContentError("Dependência de task ausente ou própria: " + dependency)
            if task["status"] in {"in_progress", "done"} and index[dependency]["status"] != "done":
                raise ContentError("Task ativa/concluída requer predecessor done.")
    if find_cycles({key: value["depends_on"] for key, value in index.items()}):
        raise ContentError("Ciclo de dependências entre tasks.")
    if record["phase"] in {"qa", "done", "cancelled"} or record["absorbed_by"]:
        if any(task["status"] in {"pending", "in_progress"} for task in tasks):
            raise ContentError("Fechamento, QA ou absorção exige plano sem tasks abertas.")
    if record["phase"] == "execute" and record["state"] == "in_progress":
        if not any(task["status"] == "in_progress" for task in tasks):
            raise ContentError("Plano em execução precisa de uma task in_progress.")
    return tasks


def build_snapshot(root, sources=None):
    root = Path(root).resolve()
    sources = read_sources(root) if sources is None else sources
    records, diagnostics = [], []
    for path, raw in sorted(sources.items()):
        if not path.endswith("/status.md"):
            continue
        try:
            data, body = parse_status(raw.decode("utf-8"))
            record = validate_status(data, body, path)
            prd_path = record["path"] + "/PRD.md"
            prd = sources.get(prd_path, b"").decode("utf-8")
            if record["prd"] == "ready" and not prd.strip():
                raise ContentError("PRD ready exige PRD.md não vazio; revisão confere o aceite.")
            record["tasks"] = []
            plan_path = record["path"] + "/plan.json"
            if plan_path in sources:
                record["tasks"] = validate_plan(
                    parse_json(sources[plan_path].decode("utf-8")), record, prd)
            records.append(record)
        except (ContentError, UnicodeError) as exc:
            diagnostics.append(diagnostic(path, "INVALID_SPEC", str(exc)))

    by_id, by_path = {}, {r["path"]: r for r in records}
    for record in records:
        key = record["id"]
        if key in by_id:
            diagnostics.append(diagnostic(record["path"], "DUPLICATE_ID", "ID repetido: " + key))
        by_id[key] = record
    for record in records:
        path = record["path"]
        parent = Path(path).parent
        while parent.as_posix() not in by_path and parent != parent.parent:
            parent = parent.parent
        record["parent_id"] = by_path[parent.as_posix()]["id"] if parent.as_posix() in by_path else None
        record["blockers"] = []
        if record["waiting_for"]:
            record["blockers"].append({"kind": "human", "ref": None, "reason": record["waiting_for"]})
        for kind, targets in (("dependency", record["depends_on"]),
                              ("absorption", [record["absorbed_by"]] if record["absorbed_by"] else [])):
            for target in targets:
                other = by_id.get(target)
                if not other or target == record["id"]:
                    diagnostics.append(diagnostic(path, "INVALID_RELATION", "Destino ausente/próprio: " + target))
                    record["blockers"].append({"kind": kind, "ref": target, "reason": "Referência inválida"})
                elif kind == "absorption" and other["phase"] == "cancelled":
                    diagnostics.append(diagnostic(path, "CANCELLED_ABSORBER", "Resolvedora cancelada: " + target))
                elif other["phase"] != "done":
                    record["blockers"].append({"kind": kind, "ref": target, "reason": "Entrega pendente"})
                    if record["phase"] == "done":
                        diagnostics.append(diagnostic(path, "UNFINISHED_DEPENDENCY", "Entrega pendente: " + target))
        for ref in record["evidence"] + [ref for t in record["tasks"] for ref in t["evidence"]]:
            try:
                target = reference_path(root, ref)
                if target is not None and not target.exists():
                    raise ContentError("Evidência local não encontrada: " + ref)
            except (ContentError, ValueError) as exc:
                diagnostics.append(diagnostic(path, "INVALID_EVIDENCE", str(exc)))
    graph = {r["id"]: r["depends_on"] + ([r["absorbed_by"]] if r["absorbed_by"] else []) for r in records}
    for cycle in find_cycles(graph):
        diagnostics.append(diagnostic("", "RELATION_CYCLE", " → ".join(cycle)))

    # Supporting documents are not silently promoted to executable tickets.
    # Warnings expose candidates for reconciliation without treating every report as a spec.
    candidate_dirs = {str(Path(p).parent) for p in sources
                      if Path(p).name in {"PRD.md", "SPEC.md", "HANDBOOK.md", "plan.json"}}
    for directory in sorted(candidate_dirs):
        if directory + "/status.md" not in sources:
            diagnostics.append(diagnostic(directory, "UNREGISTERED_DOCUMENTS",
                                          "Documentos sem status.md; conferir cadastro ou acervo.", "warning"))
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) if (
                                root / ".git").exists() else None
    revision = result.stdout.strip() if result is not None and result.returncode == 0 else None
    snapshot = {"schema_version": "superflow.feed.v2", "generated_at": utc_now(),
                "snapshot_id": fingerprint(sources), "source_revision": revision,
                "records": records, "diagnostics": diagnostics}
    return snapshot, sources


def has_errors(snapshot):
    return any(item["severity"] == "error" for item in snapshot["diagnostics"])
