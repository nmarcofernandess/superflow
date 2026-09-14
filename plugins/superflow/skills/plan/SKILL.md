---
name: plan
description: Decompõe uma execução aceita em tasks verificáveis no plan.json, com estado binário e aceite local.
---

# Plan

Crie `plan.json` antes da implementação de uma ideia aceita.

```json
{"tasks":[{"id":"T01","task":"Resultado operacional","status":"pending","depends_on":[],"acceptance":["Comportamento verificável"]}]}
```

Cada task contém exatamente `id`, `task`, `status`, `depends_on` e `acceptance`.

- `status`: somente `pending | done`.
- `depends_on`: IDs de tasks do mesmo plano.
- `acceptance`: inclui a QA necessária para concluir a unidade.
- Não use `evidence`, `in_progress`, `skipped`, heartbeat, diário ou scheduler.
- Marque `done` somente depois de conferir o aceite e as predecessoras.

Mudou a execução: ajuste o plano. Mudou produto ou arquitetura: devolva a alteração ao PRD ou à SPEC antes de prosseguir.
