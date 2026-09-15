# Contrato de comandos

```text
python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo> --summary <resumo>
python3 -I <plugin>/scripts/superflow.py --root <repo> check status
python3 -I <plugin>/scripts/superflow.py --root <repo> check spec <spec>
python3 -I <plugin>/scripts/superflow.py --root <repo> feed --output <feed.json>
python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>
```

`new` exige um resumo humano e cria apenas PRD e status. Um diagnóstico em outra spec não impede a criação; o comando ainda recusa entrada inválida, ID conhecido ou destino físico já ocupado. `check status`, feed e QG leem somente status. `check spec` confere PRD e status obrigatórios e SPEC/plano quando presentes na spec-alvo. A integridade dos destinos de `relations` é conferida pelos status da coleção. Inspecionar os arquivos não decide prontidão, autorização nem necessidade de artefatos condicionais.

O snapshot `superflow.feed.v4` inclui `summary` e `relations`. As relações preservam contexto; o QG deriva os vínculos inversos sem controlar execução.

Os comandos nunca executam proof, teste, CI ou ship. `check`, feed e QG relatam conteúdo incompleto ou inválido como `warning` e terminam com exit 0; esses diagnósticos não afirmam validade nem bloqueiam a operação do projeto. Exit 1 indica que `new` recusou a entrada ou uma colisão antes de escrever. Exit 2 indica falha operacional. Feed/QG escrevem por arquivo temporário e não substituem saída anterior numa falha operacional.

## QG em outro HTML

Use `qg --embed --output <fragmento.html>` e insira o fragmento no HTML antes de abri-lo. O fragmento contém seu snapshot e o mesmo renderer do QG standalone; não faz fetch nem exige servidor. Shadow DOM isola seus seletores CSS e IDs. O drawer preserva a URL e a âncora do hospedeiro.

O consumidor escolhe o projeto com `--root` e seu `specs_root` configurado. Regenerar substitui o snapshot inteiro: remoções e renomeações aparecem como estão nas fontes, sem tentar adivinhar identidade. Relações inválidas continuam nos diagnósticos. O adaptador do HTML hospedeiro decide onde substituir o fragmento; não precisa interpretar status nem duplicar o layout.
