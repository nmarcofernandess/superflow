# Contrato de comandos

```text
python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo>
python3 -I <plugin>/scripts/superflow.py --root <repo> check status
python3 -I <plugin>/scripts/superflow.py --root <repo> check ready <spec>
python3 -I <plugin>/scripts/superflow.py --root <repo> feed --output <feed.json>
python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>
```

`new` cria apenas PRD e status. `check status`, feed e QG leem somente status. `check ready` possui uma fronteira explícita separada e lê apenas PRD, status, SPEC e plano da spec-alvo.

Os comandos nunca executam proof, teste, CI ou ship. Exit codes: 0 válido, 1 conteúdo inválido e 2 falha operacional. Feed/QG escrevem por arquivo temporário e não substituem saída anterior numa falha operacional.
