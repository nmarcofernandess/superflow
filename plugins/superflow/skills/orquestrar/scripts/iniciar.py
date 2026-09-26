#!/usr/bin/env python3
"""Create a new offline orchestration panel without replacing existing files."""
import argparse
import json
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / 'assets'


def create_panel(destination, title):
    destination = Path(destination).expanduser()
    title = title.strip()
    if not title:
        raise ValueError('O título não pode ficar vazio.')
    targets = [destination / 'ORQUESTRACAO.html', destination / 'CONTINUIDADE.md']
    if any(p.exists() or p.is_symlink() for p in targets):
        raise FileExistsError('Já existe painel ou continuidade no destino. Atualize os arquivos existentes.')
    source = (ASSETS / 'painel.html').read_text(encoding='utf-8')
    payload = dict(title=title, summary='Próximas ações, responsáveis e dependências deste projeto.',
                   observedAt='', demo=False,
                   handoff=[dict(label='Continuidade canônica', href='./CONTINUIDADE.md')],
                   fronts=[], items=[])
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    pattern = r'(<script id="orquestra-data" type="application/json">)\s*.*?\s*(</script>)'
    panel, count = re.subn(pattern, lambda m: m[1] + '\n' + encoded + '\n' + m[2], source, flags=re.S)
    if count != 1:
        raise ValueError('Asset sem um único bloco orquestra-data.')
    continuation = (ASSETS / 'continuidade.md').read_text(encoding='utf-8').replace('{{TITLE}}', title)
    destination.mkdir(parents=True, exist_ok=True)
    written = []
    try:
        for path, content in zip(targets, [panel, continuation]):
            with path.open('x', encoding='utf-8') as handle:
                written.append(path)
                handle.write(content)
    except Exception:
        # Remove only files exclusively created by this invocation.
        for path in written:
            path.unlink()
        raise
    return targets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, type=Path)
    parser.add_argument('--titulo', required=True)
    args = parser.parse_args()
    try:
        for target in create_panel(args.dest, args.titulo):
            print(target)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Não criado: {exc}\n')


if __name__ == '__main__':
    main()
