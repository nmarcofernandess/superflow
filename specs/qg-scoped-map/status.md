---
id: qg-scoped-map
title: Mapa QG por escopo e sprint
summary: Visão opcional que combina o estado canônico das specs com um recorte editorial para explicar relações, sequência e paralelismo possível sem criar outro board.
status: pending
---

# Retrato — 23/09/2026

## Intenção

Preservar o norte de uma entrega que atravessa specs. O operador precisa ver o conjunto, focar uma frente e voltar a todas as linhas, sem transformar relações em bloqueios ou copiar estados para um sprint.

## Estado real

PRD, SPEC e plano candidato publicados com um [asset navegável](assets/mapa-sprint.html) e [dados fictícios](assets/example.json). O protótipo demonstra a interação, não é o runtime do QG instalado. A release 0.12.3 permanece inalterada; nenhum comando --scope foi adicionado, nenhum schema público foi alterado e nenhuma versão/tag foi publicada.

## Decisão proposta

Não acrescentar campos a status.md. Manter relações duradouras nele; recorte, agrupamento e precedências editoriais pertencem a um arquivo opcional do projeto, .superflow/scopes/<slug>.json. As etapas são uma leitura da sequência declarada, não autorização, cursor de tarefas, disponibilidade de equipe ou agenda automática.

## Próximo trabalho

Revisar SPEC.md e IMPLEMENTATION.md antes de implementar P01–P06 de plan.json numa PR contra main. Não mergear automaticamente. O aceite precisa provar também lista sem scope, refresh, fontes ausentes, relações cíclicas válidas e isolamento do host. VERIFY.md separa as verificações do exemplo das provas de integração ainda futuras.
