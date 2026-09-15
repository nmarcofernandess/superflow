---
name: review
description: Compara produto, arquitetura, plano ou implementação com seus contratos e resolve achados dentro do escopo autorizado.
---

# Review

Escolha o objeto e os contratos que o governam:

- PRD: promessa, escopo e aceite;
- SPEC, quando existir: arquitetura, interfaces e fronteiras;
- plano, quando existir: cobertura, dependências e verificabilidade;
- implementação: comportamento, integração e provas do projeto.

Procure bugs, regressões, falhas silenciosas, leitura/escrita excessiva e afirmações importantes sem verificação proporcional ao risco. Mudança de comportamento pede uma verificação relevante antes e depois; documentos podem ser conferidos por leitura, links ou renderização. Use os mecanismos reais do projeto.

Confira se algum consumidor operacional permanente passou a depender de arquivo da spec. A [fronteira do pacote](../../assets/references/state-contract.md#fronteira-do-pacote-da-spec) orienta a remoção do descartável ou promoção do que permanece.

Corrija achados autorizados e repita a verificação afetada. Review não cria fase nem log obrigatório. Em plano ativo, ajuste as tasks afetadas; em trabalho já encerrado, explicite o novo recorte antes de registrar sua execução. Atualize status quando o achado mudar a orientação de retomada.
