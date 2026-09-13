---
name: superflow
description: "Escolha a receita mínima e honesta para registrar, preparar, retomar, revisar, fechar ou reconciliar trabalho no repositório. Use quando o pedido menciona Superflow, uma spec, PRD, fase, andamento, revisão ou fechamento."
---

# Superflow

Superflow escolhe uma receita; não mantém um segundo estado do trabalho.
Comece pelo pedido e pelas fontes do projeto. Não leia toda a biblioteca para
uma solicitação simples.

| Situação observada | Receita |
|---|---|
| Ideia, pedido solto ou escopo ainda em formação | [capture](../../assets/playbooks/capture.md) |
| Entrega autorizada, correção ou feature | [feature](../../assets/playbooks/feature.md) |
| Trabalho existente que precisa continuar | [retomar](../../assets/playbooks/retomar.md) |
| Entrega que pede aceite, prova ou encerramento | [fechar](../../assets/playbooks/fechar.md) |
| Cadastro, fase ou evidência diverge da realidade | [reconciliar](../../assets/playbooks/reconciliar.md) |

Escolha uma receita e leia somente ela antes de continuar. Uma receita pode
pedir uma skill específica quando a situação a exigir.

## Regras de roteamento

- Pedido sem autorização de escrita é investigação, resposta ou plano; não
  crie ticket como reflexo.
- Use capture quando uma ideia precisa sobreviver à conversa. O começo é local:
  GitHub é ferramenta opcional do projeto, nunca o destino padrão.
- Analyst, build e plan são condicionais. Não acrescente fases para parecer
  rigoroso; não as pule quando uma dúvida material, uma decisão de arquitetura
  ou uma sequência com dependências ainda existe.
- Execução e QA acontecem pelas ferramentas e regras do projeto. Elas não são
  skills instaladas separadas.
- Uma confirmação no chat não é prova de entrega. Atualize o cadastro somente
  com fato, decisão ou evidência que você conferiu.
- O QG e o feed são projeções. Não edite uma projeção para corrigir a fonte.

## Limites

Respeite as instruções, permissões, worktree e gates do repositório atual. Uma
receita nunca autoriza publicação, ação destrutiva, mudança de branch ou
mensagem externa por conta própria.
