---
name: qg
description: Gera o QG Superflow — HTML autocontido a partir de .superflow/status.json. Use quando o dono pedir o quartel-general, o mapa das specs, a triagem visual, ou para ver o que existe / o que falta / o que pode avançar. Nunca chama LLM para ler specs. Regenere o feed, depois o HTML. Não edite o HTML para atualizar estado.
---

# QG — snapshot do feed

O QG é a superfície onde o dono vê o que existe, o que falta e o que pode
avançar. **Quem responde "quais são os pacotes" é `.superflow/status.json`**,
não uma lista digitada e não um walk do HTML. O HTML gerado **é** o retrato
do feed: carrega data e `read_base`. Não finja acompanhamento ao vivo.

## Gerar

A partir da raiz do consumidor (ou de qualquer path de walk-up), grave o
feed e depois o HTML:

```bash
python3 plugins/superflow/scripts/superflow_status.py .
python3 plugins/superflow/scripts/superflow_qg.py .
```

A leaf `status.json` change appears only after the feed is written again.

Destino: resolução do contrato (CLI → env → walk-up → default), pasta
`.superflow/qg/`. Não reimplemente o walk-up.

```bash
python3 plugins/superflow/scripts/superflow_qg.py . --dest .superflow/qg --out qg.html
```

## Recorte (parâmetro de geração)

Default = tudo que está tipado no disco. Filtro é manual. O plugin não classifica
o artefato como global ou local.

```bash
python3 plugins/superflow/scripts/superflow_qg.py . --scope 105-colisao-de-identidade
python3 plugins/superflow/scripts/superflow_qg.py . --scope 105-colisao-de-identidade,122-fronteira-conteudo-metadado
python3 plugins/superflow/scripts/superflow_qg.py . --scope-file recorte.json
```

Vários HTMLs, cada um com `--out` e `--dest` próprios.

## Abas

- **Mapa** (sempre): **Tasks** e **Graph**, o mesmo censo.
- **Sprint**: só com `--sprint`. Composição humana, nunca segunda autoridade.

```bash
python3 plugins/superflow/scripts/superflow_qg.py . --sprint .superflow/sprints/operacao.json
```

`--stamp YYYY-MM-DD` declara o carimbo (duas gerações iguais = HTML idêntico).

## Leis

- Determinístico. Sem LLM.
- Campo opcional ausente = `Não contém`. Conteúdo incompatível = diagnóstico na página.
- Filho declarado com `status.json` ilegível **aparece** com diagnóstico.
- Pasta de primeiro nível sem `status.json` e com conteúdo **aparece**, mesmo
  sem PRD/SPEC/analysis. O detector pergunta se é pacote e se tem conteúdo,
  não se o arquivo tem um nome da lista. Artefato interno (harness, plans,
  context) não vira bloco próprio.
- Handbook e `phases` podem divergir. Os dois lado a lado. Sem badge de erro.
- Grafo: só `depends_on` e `children_source`. Sem raspar prosa. Sem inventar aresta.
- Sem caminho absoluto de máquina no HTML.
