---
name: status
description: Cria e mantém o retrato humano completo e o frontmatter mínimo que alimentam exclusivamente o QG.
---

# Status

`status.md` é a única fonte do QG e precisa permitir compreender e retomar a spec sem abrir outro documento.

## Frontmatter

Obrigatórios: `id`, `title`, `status`. `status` aceita somente `pending | done`.

Opcionais:

- `depends_on`: lista de objetos `id` e `reason` para dependência real de outra spec;
- `waiting_for`: condição circunstancial concreta, removida quando satisfeita.

Não use fases, estados intermediários, `children`, `evidence`, task, arquivo ou porcentagem.

## Corpo

Markdown livre. Registre apenas o que ajuda compreensão e retomada: intenção, estado real, história relevante, próximo trabalho e limites, com os títulos que fizerem sentido. Corpo vazio é válido; não crie headings vazios nem copie PRD como fallback.

Na migração, incorpore aqui a narrativa útil e completa do handbook. Depois de conferir fidelidade e renderização, delete o handbook. Ele não permanece como arquivo, link ou segunda fonte.
