---
name: status
description: Use quando mudar direção, autorização, limite, handoff ou aceite global de uma entrega, ou quando for necessário publicar sua orientação no QG.
---

# Status e continuidade

Preserve o [contrato de estado](../../assets/references/state-contract.md). Frontmatter exige `id`, `title`, `summary`, `status`; `relations` é opcional. Estado global só `pending | done`. Summary é a descrição durável da entrega, não contador de tasks.

O corpo mantém **Intenção, Estado real, Rastro, Próximo trabalho e Limites**, adaptados ao conteúdo útil. `## Execução` referencia Plano/Método/Registro conforme [execution-contract](../../assets/references/execution-contract.md), sem duplicar o ledger. `## Documentos` declara anexos opcionais do detalhe. Não adicionar progress/handbook obrigatório.

Resultado de task pertence ao ledger nativo ou ao plan.json legado selecionado. Atualize status quando mudar direção, autorização, espera relevante, relação, recorte ou handoff, não a cada checkbox. Nenhum conjunto de tasks encerradas com ressalvas concede automaticamente o aceite global do PRD.

Antes de limpar a execução, preserve ledger/reports úteis uma vez em `execution/<run>/`, transfira o apontador Registro e promova rulings arquiteturais à SPEC. Não apague fontes históricas úteis nem copie todo o scratch. O arquivo terminal não recebe novas tasks.

O drawer padrão publica o corpo inteiro do status. Não esconda segredos em seção “meta” esperando que CSS a proteja. Detalhe opt-in publica os documentos selecionados; fonte ausente é diagnóstico, não “nenhum trabalho”.

Após editar, confira diagnósticos de `check status` no escopo pertinente. Se a projeção faz parte da entrega, publique feed/QG pelo [contrato de comandos](../../assets/references/commands-contract.md), da raiz identificada. Fonte de worktree não prova integração. Não crie watcher ou servidor por conta própria.
