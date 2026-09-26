---
id: qg-scoped-map
title: Mapa QG por escopo e sprint
summary: Mapa e sequência opcionais no QG único, com fontes editoriais separadas dos estados canônicos e método de orquestração integrado.
status: done
---

# Retrato — 26/09/2026

## Estado real

P01–P06 implementados e validados para 0.13.0; candidata publicada na [PR #22](https://github.com/nmarcofernandess/superflow/pull/22). A conclusão técnica não é recibo de instalação. O ajuste visual da PR #21 está incorporado. Mapa, sequência, foco e drawer usam o renderer do QG; a lista sem scope permanece padrão. A skill orquestrar mantém o estado de encaminhamentos separado de status.md.

## Contrato

O contrato operacional é [scope-contract.md](../../plugins/superflow/assets/references/scope-contract.md). O feed continua v4 e status.md continua a fonte do estado das specs. O arquivo opcional .superflow/scopes/<slug>.json declara membros e relações editoriais, sem autorização de execução ou estado duplicado.

PRD, SPEC e IMPLEMENTATION registram a decisão que originou a implementação. O protótipo em assets permanece demonstrativo; o CLI e o componente são a entrega funcional.

## Verificação

Ver [VERIFY.md](VERIFY.md) para testes executados e limites. Publicação e instalação são etapas distintas da validação local.
