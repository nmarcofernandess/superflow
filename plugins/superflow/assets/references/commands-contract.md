# Contrato de comandos

```text
python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo> --summary <resumo>
python3 -I <plugin>/scripts/superflow.py --root <repo> check status
python3 -I <plugin>/scripts/superflow.py --root <repo> check spec <spec>
python3 -I <plugin>/scripts/superflow.py --root <repo> feed --output <feed.json>
python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>
```

`new` exige um resumo humano e cria apenas PRD e status. `check status`, feed e QG leem somente status. `check spec` valida PRD e status obrigatórios e SPEC/plano quando presentes na spec-alvo. A integridade dos destinos de `relations` é conferida pelos status da coleção. Validar os arquivos não decide prontidão, autorização nem necessidade de artefatos condicionais.

O snapshot `superflow.feed.v4` inclui `summary` e `relations`. As relações preservam contexto; o QG deriva os vínculos inversos sem controlar execução.

Os comandos nunca executam proof, teste, CI ou ship. Exit codes: 0 válido, 1 conteúdo inválido e 2 falha operacional. Feed/QG escrevem por arquivo temporário e não substituem saída anterior numa falha operacional.
