---
name: analyst
description: Use ao começar ou retomar a exploração de uma entrega, quando uma resposta do usuário ou nova pesquisa precisar ser integrada ao entendimento técnico e às decisões abertas.
---

# Analyst vivo

Analyst é investigação e conversa persistente, não apenas a ação de produzir um relatório. Aplique o mesmo método no primeiro turno, nas respostas do usuário, nos retornos de pesquisadores e depois de compactação.

## Entrada e memória

Leia PRD/status e o Analyst existente. Numa nova entrega ativa, mantenha um `ANALYST.md` por recorte coeso, com [esta anatomia](../../assets/templates/ANALYST.md). Índice, questões abertas e entendimento integrado ficam no topo. Componentes, dados e fluxos relacionados crescem como capítulos da mesma lousa, não como Analysts mestres/filhos por reflexo.

Uma ideia guardada para depois não autoriza investigação. Um plano já aprovado não precisa repetir Analyst. Correção avulsa delimitada pode usar análise curta sem criar um pacote novo.

## Ciclo de trabalho

1. Explicite a promessa conhecida e a dúvida que poderia alterar a solução. Diferencie fato, inferência, proposta e decisão aceita.
2. Leia código, interfaces, dados, patterns e fontes externas pertinentes. Investigue antes de devolver ao usuário algo resolvível pelas fontes.
3. Examine integrações, negativos, lifecycle e consumidores. Para componentes, compare composição/reuso/extensão/criação e declare estado, props, gestos e limites. “Usar patterns” não substitui a análise do encaixe.
4. Apresente alternativas reais, consequências e recomendação quando existir escolha material. Não fabrique duas opções ou uma pergunta para preencher rito.
5. Integre respostas e pesquisas no entendimento atual. Atualize as seções atingidas e as decisões abertas; alternativas vencidas permanecem apenas com razões úteis, identificadas como substituídas.
6. Persista os achados relevantes **antes de responder**. Não prometa anotá-los depois. O arquivo registra razões e evidências auditáveis, não uma transcrição de raciocínio interno privado.
7. No chat, informe: o que ficou claro; a pergunta/recomendação que depende do usuário, ou que nenhuma decisão humana falta; e a próxima ação autorizada. Pergunta material no arquivo não equivale a pergunta comunicada.

O usuário decide políticas de produto e escolhas reservadas a ele. A IA resolve detalhes técnicos dentro dos critérios aceitos. Não transforme autorização de investigar em autorização de implementar.

## Research e integração

Use pesquisadores somente quando houver benefício e capacidade real; um escritor integra seus resultados na lousa. Research separado é opcional: preserve inventário, experimento caro ou evidência extensa com fonte/revisão/método/limites. Essa fotografia não vira outro contrato vivo a atualizar a cada edição. Pesquisa curta pode ser destilada diretamente no Analyst com paths/símbolos recuperáveis.

Uma decisão aceita que muda a promessa atualiza PRD. Uma alteração arquitetural aceita após Build reconcilia a região da SPEC; uma proposta nova ainda em debate não a revoga. Mudou sequência em execução: reconciliar PLAN e ruling pertinente. Status recebe mudança de autorização, direção ou handoff, não cópias de toda a análise.

## Saída

Quando a análise estiver madura, apresente o desenho e eventuais limites. Havendo autorização para consolidar, Build passa as decisões a limpo na SPEC. Não avance automaticamente para Build/Plan/código se o pedido era debater. Nenhum teto de linhas justifica omitir uma decisão material.
