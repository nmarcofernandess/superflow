"""Optional editorial scopes. Spec state is always resolved from the feed."""
from __future__ import annotations

from collections import deque
from pathlib import Path
from superflow_model import ContentError, SourceError, parse_json


def _object(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys() or value.keys() - set(required) - set(optional):
        raise ContentError('Objeto de escopo com campos ausentes ou desconhecidos.')


def _text(value):
    if not isinstance(value, str) or not value.strip():
        raise ContentError('Texto de escopo deve ser não vazio.')


def parse_scope(text):
    scope = parse_json(text)
    _object(scope, ('schema_version', 'id', 'title', 'goal', 'members'), ('groups', 'edges'))
    if scope['schema_version'] != 'superflow.scope.v1':
        raise ContentError('Versão de escopo incompatível.')
    for key in ('id', 'title', 'goal'):
        _text(scope[key])
    for key in ('members', 'groups', 'edges'):
        scope.setdefault(key, [])
        if not isinstance(scope[key], list):
            raise ContentError(key + ' deve ser lista.')
    groups, members, edges = set(), set(), set()
    for group in scope['groups']:
        _object(group, ('id', 'title'))
        for value in group.values():
            _text(value)
        if group['id'] in groups:
            raise ContentError('Grupo repetido.')
        groups.add(group['id'])
    for member in scope['members']:
        _object(member, ('spec_id',), ('group', 'focus'))
        for value in member.values():
            _text(value)
        if member['spec_id'] in members or ('group' in member and member['group'] not in groups):
            raise ContentError('Membro repetido ou grupo desconhecido.')
        members.add(member['spec_id'])
    for edge in scope['edges']:
        _object(edge, ('from', 'to', 'kind', 'reason'))
        for value in edge.values():
            _text(value)
        key = (edge['from'], edge['to'], edge['kind'])
        if (edge['kind'] not in ('after', 'context', 'evidence') or edge['from'] not in members
                or edge['to'] not in members or edge['from'] == edge['to'] or key in edges):
            raise ContentError('Aresta inválida, repetida ou fora dos membros.')
        edges.add(key)
    return scope


def read_scope(root, relative_path):
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise SourceError("Escopo deve ter path relativo não vazio.")
    root, relative = Path(root).resolve(), Path(relative_path)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise SourceError('Escopo deve ter path relativo dentro do projeto.')
    path = root
    for part in relative.parts:
        path /= part
        if path.is_symlink():
            raise SourceError('Escopo não aceita symlink.')
    try:
        path.resolve().relative_to(root)
        raw = path.read_bytes()
        scope = parse_scope(raw.decode('utf-8'))
    except (OSError, ValueError, UnicodeError, ContentError) as exc:
        raise SourceError('Escopo inválido: ' + str(exc)) from exc
    return scope, {relative.as_posix(): raw}


def ensure_scopes_unchanged(root, sources):
    for name, expected in sources.items():
        _, current = read_scope(root, name)
        if current[name] != expected:
            raise SourceError('Escopo mudou durante a publicação: ' + name)


def project_scope(feed, scope):
    """Resolve references without treating relations or completion as readiness."""
    records = {}
    for record in feed['records']:
        records.setdefault(record['id'], []).append(record)
    members = {m['spec_id']: m for m in scope['members']}
    resolved = {key: records[key][0] if len(records.get(key, [])) == 1 else None for key in members}
    edges = [dict(edge, origins=['scope']) for edge in scope['edges']]
    outside, diagnostics = [], []
    for key, record in resolved.items():
        if record is None:
            diagnostics.append({'code': 'AMBIGUOUS_MEMBER' if records.get(key) else 'MISSING_MEMBER', 'id': key})
            continue
        for relation in record['relations']:
            if relation['id'] not in members:
                outside.append({'from': key, 'to': relation['id'], 'reason': relation['reason']})
                continue
            existing = next((e for e in edges if e['kind'] == 'context' and {e['from'], e['to']} == {key, relation['id']}), None)
            origin = 'status:' + key
            if existing:
                existing['origins'].append(origin)
                existing.setdefault('context_reasons', []).append(relation['reason'])
            else:
                edges.append({'from': key, 'to': relation['id'], 'kind': 'context', 'reason': relation['reason'], 'origins': [origin]})
    after = [e for e in edges if e['kind'] == 'after']
    active = {e[k] for e in after for k in ('from', 'to')}
    isolated = [key for key in members if key not in active]
    degree = {key: 0 for key in active}
    rank = dict.fromkeys(active, 0)
    children = {key: [] for key in active}
    for edge in after:
        degree[edge['to']] += 1
        children[edge['from']].append(edge['to'])
    queue = deque(key for key in members if key in active and degree[key] == 0)
    visited = 0
    while queue:
        key = queue.popleft()
        visited += 1
        for child in children[key]:
            rank[child] = max(rank[child], rank[key] + 1)
            degree[child] -= 1
            if degree[child] == 0:
                queue.append(child)
    levels = []
    if visited != len(active):
        diagnostics.append({'code': 'ORDER_CYCLE', 'ids': [key for key in members if degree.get(key, 0)]})
        levels = None
    elif any(resolved[key] is None for key in active):
        diagnostics.append({'code': 'UNRESOLVED_PRECEDENCE'})
        levels = None
    else:
        for level in range(max(rank.values(), default=-1) + 1):
            levels.append([key for key in members if key in active and rank[key] == level])
    return {'members': resolved, 'edges': edges, 'levels': levels, 'isolated': isolated,
            'outside': outside, 'diagnostics': diagnostics}
