---
name: qg
description: Gera o QG Superflow — HTML autocontido, snapshot do disco, a partir dos status.json. Use quando o dono pedir o quartel-general, o mapa das specs, a triagem visual, ou para ver o que existe / o que falta / o que pode avançar. Nunca chama LLM para ler specs. Regenere; não edite o HTML para atualizar estado.
---

# QG — snapshot do disco

O QG é a superfície onde o dono vê o que existe, o que falta e o que pode
avançar. **Quem responde "quais são os pacotes" é o disco**, não uma lista
digitada. O HTML gerado **é** o retrato: carrega data e `read_base`. Não finja
acompanhamento ao vivo.

## Gerar

A partir da raiz do consumidor (ou de qualquer path de walk-up):

```bash
python3 plugins/superflow/scripts/superflow_qg.py .
```

Atualizar um QG é rodar o mesmo comando de novo. Mudança em `status.json`
aparece na próxima geração.

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
- Handbook e `phases` podem divergir. Os dois lado a lado. Sem badge de erro.
- Grafo: só `depends_on` e `children_source`. Sem raspar prosa. Sem inventar aresta.
- Sem caminho absoluto de máquina no HTML.
