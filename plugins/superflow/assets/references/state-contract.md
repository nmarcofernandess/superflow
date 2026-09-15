# Contrato mínimo

Toda spec possui `PRD.md` e `status.md`. `SPEC.md` registra arquitetura quando há decisões técnicas que precisam persistir; `plan.json` registra uma sequência quando ela precisa ser coordenada. Os dois são independentes e condicionais.

## Status

```yaml
---
id: importar-planilha
title: Importar despesas de uma planilha
summary: Importação de despesas de arquivos CSV, com prévia para conferir os valores antes de gravar.
status: pending
relations:
  - id: categorias
    reason: Define as categorias reconhecidas na importação.
---
```

Obrigatórios: `id`, `title`, `summary`, `status`. Estado aceita somente `pending | done`. O resumo apresenta o tema durável da spec a quem não lembra dela. Sugestão editorial: uma ou duas frases, aproximadamente 120–240 caracteres, sem limite rígido. Explique termos técnicos necessários; descreva a entrega, sem informar seu andamento.

`relations` é opcional: cada objeto contém `id` e `reason`. Uma relação guarda contexto, continuidade ou outro vínculo relevante; não decide bloqueio, ordem, conclusão ou arquivamento. O destino deve existir, ser diferente da própria spec e não se repetir. Ciclos e vínculos entre specs concluídas e abertas são válidos. O vínculo inverso é derivado na projeção; uma relação não exige registro espelhado.

O corpo Markdown guarda o retrato humano completo. A receita da skill `status` orienta intenção, estado real, rastro, próximo trabalho e limites. Corpo vazio é válido: cadastro e resumo já permitem apresentar a spec.

`## Próximo trabalho` explica direção, autorização e condições relevantes, inclusive o que pode avançar enquanto outra parte espera. Não há campo `next` ou `waiting_for`. Quando existe plano ativo, ele é o único cursor das tasks: o status não repete sua lista nem precisa mudar a cada task concluída. Atualize o retrato quando mudar direção, autorização, espera relevante, relação, divisão de escopo ou handoff.

Feed e QG descobrem e leem exclusivamente arquivos chamados `status.md`. Hierarquia é derivada do path entre specs registradas. Uma mãe concluída pode ter minispec aberta e aparecer como contexto dela. O QG oferece Em aberto, Concluídas, busca, famílias, relações e narrativa integral; relações podem abrir specs fora da visão atual.

## Plano

```json
{"tasks":[{"id":"T01","task":"Resultado operacional","status":"pending","depends_on":[],"acceptance":["Comportamento verificável"]}]}
```

Cada task contém exatamente cinco campos. Status aceita somente `pending | done`. Dependências são locais e acíclicas; uma task é concluída após conferir o aceite e suas predecessoras. `acceptance` inclui a QA da unidade. Provas permanecem nos mecanismos do projeto.

Um plano está ativo quando existe e possui ao menos uma task `pending`. Para continuar, leia a orientação do status e escolha uma task pendente com predecessoras concluídas. Um plano totalmente concluído permanece registro da execução encerrada; novo trabalho exige decisão explícita de escopo e de como registrá-lo, sem reabertura silenciosa.

## Fronteira do pacote da spec

`specs/**` contém registros e materiais autocontidos da entrega. A arquitetura permanente do projeto define os locais de runtime, instalação, manutenção, configuração operacional, testes, gates e fixtures compartilhadas. Esses consumidores não importam nem executam arquivos da spec como dependência permanente.

Ferramentas cuja finalidade é administrar, validar ou apresentar specs podem ler os artefatos declarados do pacote, como faz o Superflow ao apresentar status no QG.

HTMLs, receipts e proofs históricos podem permanecer na spec quando nenhum consumidor operacional depender deles. Um artefato que precise continuar operando depois da entrega é promovido ao local canônico do projeto, com seus consumidores atualizados antes do fechamento.

Scripts descartáveis usados durante a própria execução são removidos antes de `done`. Se precisarem permanecer para reprodução contínua, passam a compor o harness permanente do projeto e recebem um destino canônico.

Quando uma task precisar de artefato executável temporário, descreva em `task` e `acceptance` por que é temporário, quem o executa, a ausência de consumidores permanentes e sua condição de remoção ou promoção, incluindo o destino e a atualização dos consumidores. Isso é orientação de autoria e revisão proporcional ao trabalho.
