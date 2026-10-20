---
name: status
description: Use quando mudar direção, autorização, limite, handoff ou aceite global de uma entrega, ou quando for necessário publicar sua orientação no QG.
---

# Status e continuidade

Preserve o [contrato de estado](../../assets/references/state-contract.md). Frontmatter exige `id`, `title`, `summary`, `status`; `relations` é opcional. Estado global só `pending | done`. Summary é a descrição durável da entrega, não contador de tasks.

O corpo mantém **Intenção, Estado real, Rastro, Próximo trabalho e Limites**, adaptados ao conteúdo útil. `## Execução` referencia Plano/Método/Registro conforme [execution-contract](../../assets/references/execution-contract.md), sem duplicar o ledger. `## Documentos` declara anexos opcionais do detalhe. Não adicionar progress/handbook obrigatório.

Resultado de task pertence ao ledger nativo ou ao plan.json legado selecionado. Atualize status quando mudar fase, direção, autorização, bloqueio, integração/deploy, relação, recorte ou handoff, não a cada checkbox. Ao encerrar a autoria, siga [Registro do fechamento](../../assets/references/execution-contract.md#registro-do-fechamento-de-ci-e-integração): causas/correções/tickets/resultados permanecem no Registro apontado; status preserva retrato e próximo passo atuais. Tasks encerradas não concedem automaticamente integração, deploy ou aceite global do PRD.

Antes de limpar a execução, preserve ledger/reports úteis uma vez em `execution/<run>/`, transfira o apontador Registro e promova rulings arquiteturais à SPEC. Siga a retenção do execution-contract: resumos e referências duráveis, sem logs brutos ou cópia de todo o scratch; proofs formais conservam seu contrato próprio. O arquivo terminal não recebe novas tasks.

O drawer padrão publica o corpo inteiro do status. Não esconda segredos em seção “meta” esperando que CSS a proteja. Detalhe opt-in publica os documentos selecionados; fonte ausente é diagnóstico, não “nenhum trabalho”.

Após editar, confira diagnósticos de `check status` no escopo pertinente. Se a projeção faz parte da entrega, gere feed/QG da raiz identificada e siga [geração local e publicação](../../assets/references/commands-contract.md#geração-local-e-publicação). Projeções rastreadas pelo Git entram no fechamento autorizado; geração local não comprova publicação. Confira o status Git dos destinos e identifique qualquer gerado que precise permanecer local. Fonte de worktree não prova integração. Não crie watcher ou servidor por conta própria.
