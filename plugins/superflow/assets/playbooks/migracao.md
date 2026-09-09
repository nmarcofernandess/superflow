### Migração — N alvos conhecidos, mesma transformação

Use quando a lista de alvos **já existe** (veio de um run de pesquisa ou do pedido) e a
transformação é a mesma em todos. Se a lista ainda não existe, o playbook é `pesquisa`.

**Padrão: `pipeline`, não `parallel`.** Cada alvo atravessa transformar → verificar
independente dos outros; a barreira só entra se o passo seguinte precisar do conjunto.

**RUN 1 · Transformar** — um `writer` por alvo, `sonnet`, `effort: medium`.

- **POR QUÊ** a lista está fechada e cada alvo é independente.
- **EXTRAI** o alvo transformado, e o que não coube com o motivo.
- **DoD** todo alvo da lista aparece transformado ou em `faltou[]` com motivo.

Um agente por alvo **só vale com `excecaoMecanica` escrita** — a frase que diz por que os
alvos não se referenciam. Se eles se referenciam, é um agente para o conjunto (L4).

**Isolamento:** só quando dois agentes tocariam o mesmo arquivo. Worktree custa 200–500ms
e disco por agente, e **worktree não herda worktree** — se dois isolados escrevem o mesmo
destino, uma fase posterior integra, ou o trabalho de um se perde calado.

**Nada some por filtragem.** Alvo que falhou continua identificado em `faltou[]`; contar
as lacunas vem antes de descartar os nulos.

**Devolve:** quantos alvos entraram, quantos saíram transformados, a lista nominal do que
faltou com motivo, e como verificar o resultado.
