---
name: plan
description: Decompõe uma execução aceita em tasks verificáveis quando a sequência precisa persistir.
---

# Plan

Crie `plan.json` quando sequência e dependências justificarem um cursor persistido. SPEC e plano são independentes: uma sequência pode precisar de plano sem exigir nova arquitetura.

```json
{"tasks":[{"id":"T01","task":"Resultado operacional","status":"pending","depends_on":[],"acceptance":["Comportamento verificável"]}]}
```

Cada task contém exatamente `id`, `task`, `status`, `depends_on` e `acceptance`.

- `status`: `pending | done`.
- `depends_on`: IDs de tasks do mesmo plano; dependências são acíclicas.
- `acceptance`: comportamento e QA necessários para concluir a unidade.
- Marque `done` depois de conferir o aceite e as predecessoras.

Um plano com task pendente está ativo e é o único cursor da sequência. Concluir uma task comum atualiza somente o plano. Plano totalmente concluído permanece registro encerrado: novo trabalho precisa de decisão explícita de escopo e registro.

Para artefato executável temporário, use os campos existentes `task` e `acceptance`: explique por que é temporário, quem pode executá-lo, que nenhum consumidor permanente aponta para a spec e quando será removido. Se for promovido, declare o destino canônico e a atualização dos consumidores. Consulte a [fronteira do pacote](../../assets/references/state-contract.md#fronteira-do-pacote-da-spec).

Mudou a execução: ajuste o plano ativo. Mudou produto ou arquitetura: reconcilie PRD ou SPEC. Mudou direção, autorização ou condição relevante: atualize `Próximo trabalho` no status.
