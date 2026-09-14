---
name: review
description: Compara produto, arquitetura, plano ou implementação com seus contratos e resolve achados dentro do escopo autorizado.
---

# Review

Escolha o objeto e os contratos que o governam:

- PRD: promessa, escopo e aceite;
- SPEC: arquitetura, fronteiras e gates;
- plan: cobertura, dependências e verificabilidade;
- implementação: comportamento, integração e provas do projeto.

Procure bugs, regressões, falhas silenciosas, leitura/escrita excessiva e contratos sem gate. Corrija achados autorizados, repita a verificação afetada e continue até o critério terminal.

Review não cria fase nem arquivo de log obrigatório. Se um achado reabrir trabalho, a task volta para `pending`; o status recebe somente o contexto necessário à retomada.
