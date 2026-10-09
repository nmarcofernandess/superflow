"""Read-only native PLAN/ledger contracts. No scheduling or execution authority."""
from __future__ import annotations

import re
import stat
from pathlib import Path, PurePosixPath

MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_DETAIL_FILES = 32
CONVENTIONAL_DOCS = ('PRD.md', 'ANALYST.md', 'SPEC.md')
TASK = re.compile(r'^#{1,6}[ \t]+Task[ \t]+([1-9][0-9]*):[ \t]*(\S.*)$')
EVENT = re.compile(r'^Task ([1-9][0-9]*): (.+)$')
COMPLETE = re.compile(r'^complete \(commits [0-9a-f]{7,40}\.\.[0-9a-f]{7,40}, (?:review clean|[1-9][0-9]* parked|tests: .+ → .+)\)$', re.I)


class WorkError(ValueError):
    """An editorial/source contract prevents attributing work evidence."""


def visible_lines(text):
    """Yield numbered lines outside backtick/tilde fences, preserving offsets."""
    fence = None
    for number, line in enumerate(text.splitlines()):
        match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if match:
            token, rest = match.groups()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not rest.strip():
                fence = None
            continue
        if fence is None:
            yield number, line


def section(text, name):
    lines = text.splitlines()
    start = None
    for index, line in visible_lines(text):
        heading = re.match(r'^(#{1,6})\s+(.+?)\s*#*$', line)
        if not heading:
            continue
        level, title = len(heading[1]), heading[2].strip()
        if start is not None and level <= 2:
            return '\n'.join(lines[start:index]).strip()
        if level == 2 and title.casefold() == name.casefold():
            start = index + 1
    return '\n'.join(lines[start:]).strip() if start is not None else ''


def execution_references(text):
    result = {}
    keys = {'Plano': 'plan', 'Método': 'method', 'Registro': 'ledger'}
    for _, line in visible_lines(section(text, 'Execução')):
        match = re.match(r'^- (Plano|Método|Registro):\s*(.*?)\s*$', line)
        if not match:
            continue
        key, value = keys[match[1]], match[2].strip('`')
        if key in result or not value:
            raise WorkError('EXECUTION_REFERENCE: campo duplicado ou vazio: ' + key)
        result[key] = value
    if result.get('method') not in {None, 'sdd', 'inline'}:
        raise WorkError('EXECUTION_METHOD: use sdd ou inline; não inferir o método.')
    return result


def parse_plan(text):
    lines, starts = text.splitlines(), []
    for number, line in visible_lines(text):
        match = TASK.match(line)
        if match:
            starts.append((number, match[1], match[2].strip()))
        elif re.match(r'^#{1,6}\s+Task\s+[0-9]', line):
            raise WorkError('PLAN_HEADING: use Task N: título, com número positivo sem zeros iniciais.')
    if not starts:
        raise WorkError('PLAN_EMPTY: nenhum heading Task N encontrado.')
    tasks, seen = [], set()
    for position, (start, identifier, title) in enumerate(starts):
        if identifier in seen:
            raise WorkError('PLAN_ID: número duplicado: ' + identifier)
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        body = '\n'.join(lines[start:end]).strip()
        fields = {}
        for _, line in visible_lines(body):
            match = re.match(r'^\*\*(Balde|Por que agora|Depends on):?\*\*:?\s*(.*?)\s*$', line)
            if match:
                if match[1] in fields:
                    raise WorkError('PLAN_FIELD: metadado duplicado na Task ' + identifier)
                fields[match[1]] = match[2]
        value = fields.get('Depends on', '')
        dependencies = [part.strip() for part in value.split(',')] if value else []
        if len(dependencies) != len(set(dependencies)) or any(d not in seen for d in dependencies):
            raise WorkError('PLAN_DEPENDENCY: Task ' + identifier + ' requer predecessoras existentes e anteriores na ordem textual.')
        tasks.append({'id': identifier, 'title': title, 'depends_on': dependencies,
                      'bucket': fields.get('Balde'), 'reason': fields.get('Por que agora'),
                      'body_md': body})
        seen.add(identifier)
    return tasks


def parse_ledger(text, plan_path, tasks, root=None):
    lines = text.splitlines()
    prefix = '# SDD ledger — plan: '
    if not lines or not lines[0].startswith(prefix):
        raise WorkError('LEDGER_IDENTITY: cabeçalho nativo ausente.')
    identity = lines[0][len(prefix):].strip()
    if root is not None and Path(identity).is_absolute():
        try:
            identity = Path(identity).relative_to(Path(root).resolve()).as_posix()
        except ValueError:
            raise WorkError('LEDGER_IDENTITY: o registro pertence a outra raiz.') from None
    if identity != plan_path:
        raise WorkError('LEDGER_IDENTITY: o registro não identifica o plano selecionado.')
    state = {task['id']: {'state': 'unobserved', 'events': [], 'completion': None} for task in tasks}
    last = None
    for _, line in visible_lines(text):
        match = EVENT.match(line)
        if not match:
            if line.startswith(('Final review:', 'Final:')):
                last = line
            continue
        identifier, event = match.groups()
        if identifier not in state:
            raise WorkError('LEDGER_TASK: registro cita task inexistente: ' + identifier)
        item = state[identifier]
        item['events'].append(event)
        last = line
        if COMPLETE.fullmatch(event):
            concerns = any('parked' in e or 'deferred' in e for e in item['events'])
            item['state'] = 'complete_with_concerns' if concerns else 'complete'
            item['completion'] = event
        elif event.startswith('fix round') or item['completion'] is None:
            item['state'] = 'checkpoint'
            item['completion'] = None
        elif 'parked' in event or 'deferred' in event:
            item['state'] = 'complete_with_concerns'
    completed = {key for key, value in state.items() if value['state'].startswith('complete')}
    for task in tasks:
        if task['id'] in completed and any(dep not in completed for dep in task['depends_on']):
            raise WorkError('LEDGER_DEPENDENCY: conclusão sem predecessora concluída: ' + task['id'])
    next_task = next((task['id'] for task in tasks if task['id'] not in completed), None)
    return {'identity': identity, 'tasks': state, 'next_task': next_task, 'last_checkpoint': last}


def safe_path(root, reference, spec_path, kind):
    if not isinstance(reference, str) or not reference or '\x00' in reference or '\\' in reference:
        raise WorkError('SOURCE_PATH: caminho relativo inválido.')
    value = PurePosixPath(reference)
    if value.is_absolute() or '..' in value.parts or ':' in reference or str(value) != reference:
        raise WorkError('SOURCE_PATH: caminho não normalizado ou fora da raiz.')
    parts = value.parts
    in_spec = reference.startswith(spec_path.rstrip('/') + '/')
    if kind == 'ledger':
        allowed = (reference.startswith(spec_path.rstrip('/') + '/execution/') or
                   (len(parts) >= 4 and parts[:2] == ('.superpowers', 'sdd')))
        if not allowed or value.name != 'progress.md':
            raise WorkError('SOURCE_PATH: registro deve ser progress.md no workspace SDD ou execution da spec.')
    elif (not in_spec or value.name == 'status.md' or
          (value.suffix not in {'.md', '.html'} and value.name != 'plan.json')):
        raise WorkError('SOURCE_PATH: documento deve estar no pacote da spec.')
    if any(part.startswith('.') for part in parts if part != '.superpowers'):
        raise WorkError('SOURCE_PATH: arquivos ocultos não são fontes do detalhe.')
    root = Path(root).resolve()
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise WorkError('SOURCE_SYMLINK: links simbólicos não são fontes do detalhe.')
    if path.exists() and not stat.S_ISREG(path.stat().st_mode):
        raise WorkError('SOURCE_TYPE: a fonte não é um arquivo regular.')
    return path


def choose_plan(root, spec_path, body, sources=None):
    refs = execution_references(body)
    if refs.get('plan'):
        candidate = refs['plan']
        safe_path(root, candidate, spec_path, 'document')
        if PurePosixPath(candidate).name not in {'PLAN.md', 'plan.json'}:
            raise WorkError('PLAN_SELECTION: Plano deve identificar PLAN.md ou plan.json.')
        return candidate
    candidates = [spec_path + '/' + name for name in ('PLAN.md', 'plan.json')]
    found = [p for p in candidates if sources.get(p) is not None] if sources is not None else [
        p for p in candidates if safe_path(root, p, spec_path, 'document').exists()]
    if len(found) > 1:
        raise WorkError('PLAN_AMBIGUOUS: declare Plano em ## Execução; existem dois formatos.')
    return found[0] if found else None


def requested_paths(root, record):
    spec_path, body = record['path'], record['body_md']
    paths = [(spec_path + '/' + name, 'document') for name in (*CONVENTIONAL_DOCS, 'PLAN.md', 'plan.json')]
    refs = execution_references(body)
    if refs.get('plan'):
        paths.append((refs['plan'], 'document'))
    if refs.get('ledger'):
        paths.append((refs['ledger'], 'ledger'))
    for _, line in visible_lines(section(body, 'Documentos')):
        match = re.match(r'^- [^:]+:\s*`?([^`]+?)`?\s*$', line)
        if match:
            paths.append((match[1], 'document'))
    paths = list(dict.fromkeys(paths))
    if len(paths) > MAX_DETAIL_FILES:
        raise WorkError('SOURCE_LIMIT: detalhe excede 32 fontes; selecione os anexos necessários.')
    for reference, kind in paths:
        safe_path(root, reference, spec_path, kind)
    return paths


def collect_detail_sources(root, records, selected):
    """None represents a missing source, so later appearance changes the snapshot."""
    sources = {}
    for identifier in selected:
        matches = [r for r in records if r['id'] == identifier]
        if len(matches) != 1:
            continue
        record = matches[0]
        try:
            paths = requested_paths(root, record)
        except WorkError:
            continue  # project_detail reports the contract error; no partial disclosure
        for reference, kind in paths:
            try:
                path = safe_path(root, reference, record['path'], kind)
                if not path.exists():
                    sources[reference] = None
                    continue
                with path.open('rb') as handle:
                    raw = handle.read(MAX_SOURCE_BYTES + 1)
                sources[reference] = raw
            except OSError as exc:
                raise WorkError('SOURCE_READ: não foi possível ler a fonte declarada: ' + reference) from exc
    return sources


def project_detail(root, record, sources, legacy_parser):
    detail = {'schema_version': 'superflow.detail.v1', 'root_name': Path(root).resolve().name,
              'documents': [], 'decisions_md': '', 'tasks': [], 'ledger': None,
              'method': None, 'plan_path': None, 'issues': [], 'state': 'unavailable'}
    try:
        paths = requested_paths(root, record)
        refs = execution_references(record['body_md'])
        detail['method'] = refs.get('method')
        chosen = choose_plan(root, record['path'], record['body_md'], sources)
        detail['plan_path'] = chosen
        texts = {}
        for reference, kind in paths:
            raw = sources.get(reference)
            if raw is None:
                if (reference in {chosen, refs.get('ledger')} or
                    PurePosixPath(reference).name not in (*CONVENTIONAL_DOCS, 'PLAN.md', 'plan.json')):
                    detail['issues'].append('SOURCE_MISSING: ' + reference)
                continue
            if len(raw) > MAX_SOURCE_BYTES:
                raise WorkError('SOURCE_LIMIT: fonte maior que 2 MiB: ' + reference)
            try:
                texts[reference] = raw.decode('utf-8')
            except UnicodeError:
                raise WorkError('SOURCE_ENCODING: fonte não é UTF-8: ' + reference) from None
            if kind != 'ledger' and (PurePosixPath(reference).name not in {'PLAN.md', 'plan.json'} or reference == chosen):
                detail['documents'].append({'path': reference, 'name': PurePosixPath(reference).name,
                                            'content': texts[reference]})
        analyst = texts.get(record['path'] + '/ANALYST.md', '')
        detail['decisions_md'] = '\n\n'.join('## ' + title + '\n' + content for title in (
            'Leitura de retomada', 'Índice da análise', 'Decisões abertas', 'Entendimento integrado atual')
            if (content := section(analyst, title)))
        if chosen and chosen in texts:
            if chosen.endswith('/plan.json'):
                tasks = legacy_parser(texts[chosen])
                detail['tasks'] = [dict(t, title=t['task'], bucket=None, reason=None,
                    body_md='\n'.join(t['acceptance']), evidence_state='legacy_' + t['status']) for t in tasks]
                detail['state'] = 'legacy'
            else:
                detail['tasks'] = parse_plan(texts[chosen])
                detail['state'] = 'plan_only'
                ledger_path = refs.get('ledger')
                if ledger_path and ledger_path in texts:
                    detail['ledger'] = dict(parse_ledger(texts[ledger_path], chosen, detail['tasks'], root), path=ledger_path)
                    detail['state'] = 'observed'
                elif not ledger_path:
                    detail['issues'].append('LEDGER_UNDECLARED: resultados não atribuídos; declare Registro em ## Execução.')
        elif chosen:
            detail['issues'].append('PLAN_MISSING: plano declarado indisponível.')
        else:
            detail['state'] = 'analysis'
        if refs.get('ledger') and (not chosen or chosen.endswith('/plan.json')):
            detail['issues'].append('LEDGER_UNATTRIBUTED: registro nativo não atribuído a plano Markdown selecionado.')
    except (WorkError, ValueError, TypeError) as exc:
        detail['issues'].append(str(exc))
        detail['ledger'] = None
        detail['state'] = 'unavailable'
    return detail
