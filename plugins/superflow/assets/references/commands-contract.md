# Contrato de comandos

Os comandos são operações Python portáteis sobre uma raiz explícita. A interface
é:

    python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo>
    python3 -I <plugin>/scripts/superflow.py --root <repo> check
    python3 -I <plugin>/scripts/superflow.py --root <repo> feed --output <feed.json>
    python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>

Python 3.9 ou superior é pré-requisito. A opção -I evita depender de
site-packages, PYTHONPATH ou instalação global. A configuração opcional
.superflow/config.json pode declarar specs_root, proof_cmd e ship_cmd; estes
quatro comandos nunca executam proof, ship ou comandos configurados.

| Comando | Efeito |
|---|---|
| new | Cria pacote inexistente com status.md programático e PRD.md a partir do template. Falha sem deixar cadastro parcial ou sobrescrever pacote. |
| check | Lê e valida estrutura, relações e planos. É somente leitura. |
| feed | Produz fotografia normalizada do corpus. Sem output, usa .superflow/feed.json. |
| qg | Produz HTML autocontido a partir de uma única fotografia. Sem output, usa .superflow/qg.html. |

Exit codes: 0 para conteúdo válido, 1 para conteúdo inválido e 2 para falha
operacional. Feed e QG diagnosticam conteúdo inválido com paths; falha
operacional não substitui uma saída anterior por fotografia parcial. Escritas
usam temporário e replace, e reconferem o conjunto de fontes antes de publicar.

As projeções mostram o corpus completo. Filtro, busca, paginação e detalhe não
mudam relações, diagnósticos ou contagens globais. O QG não depende de sprint,
board, rede, servidor, CDN ou fonte remota.
