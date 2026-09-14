# Contrato mínimo

Toda ideia nasce com `PRD.md` e `status.md`. Antes da primeira implementação aceita, também precisa de `SPEC.md` e `plan.json`.

## Status

```yaml
---
id: minha-spec
title: Minha spec
status: pending
depends_on:
  - id: outra-spec
    reason: Precisa do contrato entregue pela outra spec.
waiting_for: Resposta humana concreta.
---
```

Obrigatórios: `id`, `title`, `status`. Estado aceita somente `pending | done`.

`depends_on` é opcional e liga outra spec por ID e motivo. `waiting_for` é uma espera circunstancial e não cria aresta. O corpo é Markdown livre e guarda o retrato humano completo.

Não existem fases, estados intermediários, children, evidence, task, arquivo ou porcentagem no status.

Feed e QG descobrem e leem exclusivamente arquivos chamados `status.md`. Hierarquia é derivada do path entre specs registradas. Uma mãe done pode ter minispec pendente.

## Plano

```json
{"tasks":[{"id":"T01","task":"Resultado operacional","status":"pending","depends_on":[],"acceptance":["Comportamento verificável"]}]}
```

Cada task contém exatamente cinco campos. Status aceita somente `pending | done`. Dependências são locais e acíclicas. Acceptance inclui a QA da unidade. Provas permanecem nos mecanismos do projeto.

## Narrativa legada

Na migração, o conteúdo útil e completo do handbook entra no corpo do status. Depois da conferência de fidelidade e renderização, o handbook é deletado. Ele não permanece como fonte, link ou fallback.
