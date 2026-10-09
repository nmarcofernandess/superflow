---
name: superflow
description: Use para registrar uma ideia, iniciar ou retomar uma entrega, reconciliar suas fontes e acompanhar seu fechamento.
---

# Superflow

Comece pela intenção e pelo `status.md` da entrega. Leia só a receita e os contratos pertinentes; não pré-carregue a biblioteca inteira.

## Três entradas claras

- **Guardar ideia para depois:** criar/atualizar PRD e status e parar. Nenhuma pesquisa ou implementação implícita.
- **Criar a spec e trabalhar na entrega:** PRD inicial honesto → Analyst vivo → Build/SPEC consolidada → PLAN nativo Superpowers → execução autorizada → revisão/provas/integração do projeto. A profundidade varia, não a autoridade de cada arquivo.
- **Executar/retomar plano aprovado:** conferir estado, fontes e autorização e continuar do ledger/plano. Não repetir design por haver chat novo ou compactação.

Uma correção avulsa delimitada fora de nova spec pode seguir diretamente o aceite autorizado do projeto. Não estimar antecipadamente a complexidade para pular análise necessária; também não lançar agentes, criar alternativas falsas ou exigir HTML para toda entrega.

## Autoridades

PRD guarda promessa; Analyst mantém exploração/diálogo; SPEC fecha arquitetura; PLAN.md declara sequência; ledger registra execução; status orienta retomada/aceite global. HTML/QG apresenta as fontes, sem segunda lista de tasks. O [contrato de execução](../../assets/references/execution-contract.md) define seleção de plano, método, retrofit e retenção.

Estado global continua `pending | done`; relações são contexto, não bloqueio automático. Legado plan.json permanece legível e explicitamente selecionado quando coexistir com PLAN.md. Não reabra pacote concluído silenciosamente.

Uma pergunta material deve chegar ao usuário com recomendação. Persistir arquivo é parte da preparação autorizada, não precisa esperar um GO reservado à implementação. Não ampliar autorização: planos, testes, push, merge, release e instalação são atos distintos.

## Projeção e orquestração

`new`, `check`, `feed` e `qg` são ferramentas determinísticas; não executam código de produto nem autorizam ações externas. QG padrão lê status; detalhe exige `qg_details` com IDs explícitos. Confirme conteúdo publicável antes de habilitar fontes.

Para encaminhamentos entre frentes, use [orquestrar](../orquestrar/SKILL.md). Ela não é scheduler de tasks. Não crie lane lateral por reflexo; uma transferência identifica sucessor editorial, fontes integradas e próximo movimento, não apenas remoção de worktree.

Preserve a [fronteira do pacote](../../assets/references/state-contract.md#fronteira-do-pacote-da-spec). O consumidor continua dono de testes, proofs, CI e ship. As receitas em `../../assets/playbooks/` são capture, feature, retomar, reconciliar e fechar.
