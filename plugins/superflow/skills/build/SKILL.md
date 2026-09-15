---
name: build
description: Consolida decisões técnicas materiais e reuso em SPEC.md quando a entrega precisa de arquitetura explícita.
---

# Build

Build transforma um PRD aceito numa arquitetura verificável. Use quando há decisões técnicas que precisam persistir; uma execução simples pode seguir sem SPEC.

Leia código, padrões e interfaces reais. Investigue as facetas relevantes e procure reuso antes de propor nova estrutura. Escreva ou atualize `SPEC.md` com integração, contratos de dados, fronteiras de leitura/escrita, decisões, riscos materiais e verificações proporcionais.

Declare o local canônico dos componentes permanentes fora de `specs/**`. Se houver artefato temporário, identifique seu uso e destino conforme a [fronteira do pacote](../../assets/references/state-contract.md#fronteira-do-pacote-da-spec).

Se a arquitetura mudar produto, reconcilie o PRD. O plano é uma decisão independente: só é necessário quando a sequência precisa ser coordenada. O retrato operacional permanece em status.
