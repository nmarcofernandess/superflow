---
name: review
description: Use para confrontar produto, arquitetura, plano ou implementação com suas fontes e efeitos reais, sem confundir uma lacuna de evidência com uma regressão demonstrada.
---

# Review

Escolha o objeto: PRD (promessa/aceite), Analyst (fatos/opções/questões comunicadas), SPEC (integração/interfaces/lifecycle), PLAN (decomposição/ordem/verificação), implementação (comportamento e provas).

Procure bugs, regressões, falhas silenciosas e decisões materiais omitidas. Uma arquitetura não está fechada se o planejador precisa reconstruí-la em pesquisas. Um plano não está fechado se o executor precisa escolher novamente a feature ou ignorar uma predecessora pendente.

Use evidência proporcional e mecanismos reais do projeto. Testes escritos não são testes executados; foco é escopo, não executor. Documentos pedem conteúdo/links/renderização pertinentes, não TDD artificial.

Quando SDD/inline já é dono da revisão de implementação, esta skill não impõe uma segunda revisão genérica da mesma task. Preserve o review correspondente ao método. Não multiplique reviewer/fixer por reflexo.

Corrija achados autorizados e confira o delta. Mudança de arquitetura atualiza SPEC, de execução atualiza PLAN, de produto requer a decisão correspondente; resultado fica no ledger. No legado, preserve o plano ativo selecionado. Findings estacionados não viram aceite clínico/global.

Confira a [fronteira do pacote](../../assets/references/state-contract.md#fronteira-do-pacote-da-spec), a retenção do registro antes de cleanup e o sucessor de responsabilidades editoriais. Não crie novo gate para provar que agentes leram instruções.
