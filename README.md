# Superflow

Superflow ajuda a registrar e conduzir trabalho de forma proporcional. A fonte
da promessa é o PRD; análise, arquitetura e plano entram somente quando a
situação precisa deles.

    pedido
      -> PRD
      -> analyst, build ou plan quando necessário
      -> execução, review e QA do projeto
      -> aceite e estado factual

O plugin não é um executor, board, campanha, sprint ou sistema paralelo de
provas. Ele usa fontes do repositório e suas ferramentas nativas.

## O que o plugin exporta

| Skill | Responsabilidade |
|---|---|
| superflow | Escolhe uma receita curta sem pré-carregar toda a biblioteca. |
| prd | Cria ou amadurece a promessa, escopo e aceite. |
| analyst | Faz recon, examina facetas relevantes e devolve o PRD corrigido. |
| build | Fecha arquitetura e reuso em SPEC quando há decisão técnica material. |
| plan | Cria plan.json quando sequência e dependências justificam. |
| review | Examina desenho ou diff com evidência e rechecagem. |
| status | Mantém fase, espera, evidência e relações factuais. |

As cinco receitas são capture, feature, retomar, fechar e reconciliar. Execute
e QA permanecem etapas do fluxo, operadas pelas regras e ferramentas do projeto,
sem skills separadas.

## Estado e arquivos

Um pacote pode conter:

    specs/<id-ou-slug>/
      status.md
      PRD.md
      SPEC.md
      analysis.md
      plan.json
      progress.md

Somente status.md e PRD.md surgem no comando new. Os demais são condicionais.
Os [contratos](plugins/superflow/assets/references/) de estado, comandos e
qualidade acompanham o pacote.

## Comandos

O runtime é Python 3.9 ou superior e usa modo isolado:

    python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo>
    python3 -I <plugin>/scripts/superflow.py --root <repo> check
    python3 -I <plugin>/scripts/superflow.py --root <repo> feed --output <feed.json>
    python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>

New cria o cadastro inicial; check é somente leitura; feed e QG são projeções
geradas a partir da mesma fotografia. Eles nunca executam proof, ship ou outro
comando configurado pelo repositório.

O QG abre em **Em aberto**, com specs em acordeões e minispecs aninhadas.
A narrativa completa de `status.md` aparece dentro da spec; tarefas ficam em
**Plano**. A busca cobre o conteúdo completo e abre a cadeia até a minispec.
**Concluídas** e **Arquivadas** são visões separadas: filtrar não altera arquivos
nem arquiva nada. Uma spec concluída pode aparecer como contexto de filhos abertos.

## Instalação

Instale uma release identificada por tag e confira a versão declarada nos
manifestos antes de usar:

    codex plugin marketplace add nmarcofernandess/superflow --ref v0.8.0
    codex plugin add superflow@superflow

Em Claude Code:

    claude plugin marketplace add nmarcofernandess/superflow@v0.8.0
    claude plugin install superflow@superflow

Para atualizar um marketplace já cadastrado, use `codex plugin marketplace upgrade superflow` seguido de `codex plugin add superflow@superflow`, ou `claude plugin marketplace update superflow` seguido de `claude plugin update superflow@superflow`. Se o marketplace estiver preso a uma tag antiga, altere a referência na configuração do host antes de atualizar.

Após atualizar, abra uma nova task para recarregar o inventário de skills.

## Migração de versões anteriores

O contrato anterior de status.json, HANDBOOK, implementation_plan,
implementation_log, review_log, WARLOG, board, sprint e campanha não é mais
superfície ativa. Um repositório consumidor não é migrado automaticamente: o
censo decide o destino de cada documento, preserva história e só então cria
status.md, PRD.md e plan.json onde houver pacote real.

Arquivos históricos continuam sendo história do consumidor. Não os copie para o
plugin novo e não use fallback silencioso para fazê-los parecer estado atual.

## Desenvolvimento

A fonte do plugin é plugins/superflow. O gate do repositório valida o conjunto
exato de sete diretórios de skills, referências internas e conteúdo do pacote.
Leia o [README do plugin](plugins/superflow/README.md) para uso e migração; leia
a [SPEC atual](SPEC-superflow-plugin.md) para as decisões técnicas.
