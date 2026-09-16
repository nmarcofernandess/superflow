---
name: status
description: Cria e mantém o resumo durável, o retrato humano completo e as relações que alimentam o QG.
---

# Status

`status.md` permite compreender e retomar a spec. Leia o [contrato de estado](../../assets/references/state-contract.md) ao criar ou atualizar o pacote.

## Frontmatter

Obrigatórios: `id`, `title`, `summary`, `status`. `status` aceita `pending | done`. `relations` é a lista opcional de objetos `id` e `reason`.

Escreva `summary` para alguém que não lembra do assunto: qual entrega esta spec representa e para quem ela serve. Prefira uma ou duas frases, aproximadamente 120–240 caracteres, explicando jargões necessários. A extensão é sugestão editorial. O tema permanece mesmo depois da conclusão; o andamento pertence ao corpo.

## Receita para o corpo

Use este Markdown como ponto de partida quando não houver orientação específica. Adapte as seções ao conteúdo disponível e preserve a narrativa útil completa.

```markdown
## Intenção

Explique a entrega e por que ela importa, com contexto suficiente para retomar.

## Estado real

Descreva o que existe e o que foi conferido, distinguindo entrega de intenção.

## Rastro

Registre decisões e evidências que explicam como chegamos aqui.

## Próximo trabalho

Explique a próxima direção, a autorização necessária ou a condição ainda vigente.
Se apenas uma parte espera, diga o que pode continuar.

## Limites

Registre restrições de escopo e condições de exceções temporárias relevantes.
```

Uma spec com cadastro e resumo já pode ser apresentada; o corpo cresce conforme houver contexto útil. Relações guardam memória e não determinam bloqueios. Se existir plano ativo, ele guarda o cursor das tasks; o corpo orienta a retomada sem duplicá-lo.

Atualize o status quando mudar direção, autorização, espera relevante, relação, divisão de escopo ou handoff. Concluir uma task comum altera somente o plano aplicável. Exceções temporárias da fronteira do pacote cabem em `Próximo trabalho` ou `Limites`, com condição de encerramento.

Após editar, use `check status` para ler e tratar os diagnósticos no escopo do trabalho. Se houver painel a publicar, siga o [contrato de comandos](../../assets/references/commands-contract.md): `feed` atualiza os painéis online no próximo carregamento; `qg` gera ou atualiza exports offline. Para uma visão compartilhada, prefira uma raiz integrada e atualizada; ensaios podem usar a lane. A publicação segue a escolha e as ferramentas do projeto.
