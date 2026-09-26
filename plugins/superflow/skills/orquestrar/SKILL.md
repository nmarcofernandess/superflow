---
name: orquestrar
description: Organiza frentes de trabalho quando o usuário pede orquestração, roadmap, próximos prompts, retomada de vários chats ou um painel de dependências. Confere fontes e estados, separa preparação de envio e conclusão, identifica o próximo passo de cada frente e mantém um HTML offline com prompts copiáveis. Não é gatilho para iniciar execução, delegação ou automações.
---

# Orquestrar frentes no Superflow

Transformar trabalho espalhado em uma rota que permita responder: **o que falta, quem faz, o que libera e qual é o próximo movimento?** Usar esta skill para preparar e acompanhar trabalho, preservando os contratos e arquivos do projeto. O HTML serve ao trabalho; não criar um programa de gestão para resolver uma tarefa pequena.

## 1. Estabelecer o resultado e o limite

Declarar brevemente se o pedido é sondagem, plano, atualização documental ou execução autorizada. Identificar as frentes nomeadas, os entregáveis esperados, quem decide, quem escreve planos e quem executa. Reutilizar papéis já definidos na conversa.

Separar três responsabilidades:

- **Orquestradora:** conferir contexto suficiente, identificar a próxima unidade e deixar ação/prompt completos, fontes acessíveis e destinatário claro. Quando chegar um retorno, revisar sua suficiência e preparar a continuação.
- **Operador:** confirmar envio e andamento externo quando o encaminhamento for manual; tomar apenas as decisões reservadas a ele, com recomendação e contexto já preparados.
- **Trabalho conjunto:** chegar à entrega realmente concluída, com a validação e integração exigidas pelo projeto.

Quando o combinado for levar material a uma IA de planejamento, a preparação termina em **pronto para enviar**, não em resolver toda a arquitetura ou escrever a SPEC profunda. Se a próxima etapa for descobrir o que falta, entregar um prompt de descoberta delimitado. Se faltar uma decisão, preparar recomendação, alternativas pertinentes e material didático. Se o operador já autorizou execução local, seguir até o limite autorizado; não impor handoff externo por rito.

## Fontes e identidade

A spec continua com `status.md` (`pending | done`) e seu plano quando necessário.
A unidade do painel é um **encaminhamento**, não um segundo cadastro de spec ou task.
“Enviado” informa que um pedido foi encaminhado; não substitui o cursor do plano.
“Concluído” fecha apenas o resultado nomeado do encaminhamento. Referenciar a fonte
canônica; não copiar a lista de tasks para este painel. Uma frente pode reunir
vários repositórios por links explícitos sem agregar seus estados automaticamente.

Para um mapa de specs de um projeto, usar o QG oficial com `qg --scope` e o
[contrato de composição](../../assets/references/scope-contract.md). Não reconstruir
títulos, estado ou narrativa em JSON editorial. Para a mesa de próximos envios,
usar o painel existente ou o asset abaixo. São visões de objetos diferentes:
specs e encaminhamentos. Podem coexistir no mesmo HTML por incorporação do QG.
O renderer do QG é o único dono da visualização factual das specs.

## 2. Reconstruir somente o contexto necessário

Começar nas instruções atuais, painel/continuidade existentes, pacote/spec dono, status e código pertinentes. Conferir fatos mutáveis na fonte: branch/HEAD/PR/merge, execução, artefatos, decisões e data da observação são fatos separados. Um relato de tarefa pode orientar a busca, mas não prova integração.

Não omitir uma frente por estar “com o operador”. Mapear seu funcionamento atual, alvo, lacuna, responsável e próxima ação, sem ocupar uma lane alheia. Não substituir o universo de um domínio pelo miniapp que testa seu core. Distinguir melhoria futura de um comportamento atual que já pode ser verificado.

Se fontes divergirem, nomear a discrepância relevante e escolher a menor leitura que a resolve. Se persistir, encaminhar investigação específica; não pintar certeza ou percorrer o repositório inteiro. Contexto indisponível precisa de um pedido concreto de preparação, não um prompt que presume arquivos inacessíveis ao destinatário.

## 3. Decompor por entrega e dependência real

Criar uma unidade por resultado coerente, não por arquivo, fase administrativa ou PR obrigatório. Para cada unidade registrar:

1. ID estável, frente, objetivo e escopo nominal.
2. Estado observado, responsável e destino do trabalho.
3. Fonte e data/revisão quando relevantes; limite do que a evidência demonstra.
4. Lacuna ou decisão pendente.
5. Dependências com a entrada exata que falta e o estágio que a exige.
6. Próxima ação, seu responsável e condição observável de término.
7. Prompt completo quando houver um encaminhamento a fazer.

Distinguir dependência de **pesquisa**, **decisão**, **implementação**, **publicação** e **execução pesada**. Uma reforma futura não bloqueia automaticamente a preparação ou teste do produto atual; uma fila compartilhada serializa recursos, não toda a investigação. Não remover uma célula obrigatória para fazer o restante parecer completo.

Revisar o grafo: IDs únicos, sem ciclos, dependências existentes, saída de um prompt compatível com a entrada do próximo, ownership de arquivos compartilhados explícito. Ordenar o Agora pelo que está liberado e pelo benefício concreto, com poucas ações recomendadas. Manter as demais frentes visíveis.

## 4. Usar estados com significado

Ler [estados-e-handoffs.md](references/estados-e-handoffs.md) quando classificar uma unidade ou receber um retorno. Separar **prompt preparado, mas aguardando entrada** de **pronto para enviar**. Separar também enviado, em revisão, pronto para implementar, em execução e concluído.

Não avançar estado porque alguém copiou um prompt, porque o tempo passou, porque há uma PR ou porque um plano parece bonito. Conclusão pertence à unidade exata: terminar a preparação documental não conclui o produto. Manter “parado/sem encaminhamento” como alerta transversal com causa e destravador; tempo sozinho não prova abandono.

Em retomadas, cobrar o envio ou retorno que falta de maneira objetiva. Não criar lembrete, heartbeat ou serviço por conta própria. Não exigir que o operador confirme novamente algo já autorizado ou informado.

## 5. Preparar prompts que possam sair desta conversa

Usar [prompt-de-encaminhamento.md](references/prompt-de-encaminhamento.md) como estrutura, preenchida com nomes, fontes e limites reais. O destinatário precisa receber um pedido utilizável sem reconstruir este chat.

Nomear objetivo, estágio, fontes acessíveis, arquivos sob responsabilidade, predecessores, decisões vigentes, entregáveis e ponto de parada. Pedir atualização dos status/planos donos quando fizer parte da entrega, sem criar uma segunda autoridade.

Preservar a capacidade do destinatário: GPT online pode pesquisar, revisar e escrever arquivos, mas não declarar execução local de código/typecheck/CI. Um executor local pode implementar e verificar dentro da autorização. Se houver Superflow, preservar seus pacotes; se for pedido plano Superpowers/TDD, o planejador o escreve nos artefatos canônicos, sem duplicar árvores. Não tornar esses sistemas dependências obrigatórias do plugin.

Evitar comandos inventados, dados sintéticos vendidos como prova, `TODO/TBD`, “testar tudo” e escolhas técnicas profundas improvisadas. Quando faltar informação para um plano mecânico, o próprio próximo prompt deve obtê-la. Não obrigar TDD para documento ou tarefa que não o exige.

## 6. Manter uma casa canônica e um painel legível

**Se já houver painel e continuidade, editá-los no lugar autorizado.** Não rodar o inicializador sobre eles nem substituir o painel do projeto pelo exemplo. Preservar mudanças locais alheias. Links/atalhos no Desktop podem apontar para a casa canônica; não manter cópias concorrentes.

Para uma instalação nova, usar os assets desta skill:

- [painel.html](assets/painel.html): HTML autocontido, sem CDN, com visão Agora, uma aba por frente, conexões, estados, fontes, prompts copiáveis e handoff. O conteúdo inicial é explicitamente demonstrativo.
- [continuidade.md](assets/continuidade.md): memória operacional curta, com decisões vigentes, fontes e limites; não diário inteiro.
- [iniciar.py](scripts/iniciar.py): gerar uma versão vazia em destino novo, sem sobrescrever arquivo existente.

Resolver paths relativos à pasta desta skill, nunca ao cwd por suposição. Exemplo com paths resolvidos:

```bash
python3 <pasta-da-skill>/scripts/iniciar.py --dest <destino-novo> --titulo "Projeto"
```

O inicializador gera `ORQUESTRACAO.html` e `CONTINUIDADE.md`; não faz descoberta nem comprova estados. Preencher o bloco `orquestra-data` do HTML com o resultado da análise. Não criar JSON externo concorrente: esse bloco é apenas os dados da apresentação, derivados das fontes do projeto. O formato e as transições estão no documento de estados. O layout é um asset substituível; preservar o método mesmo quando trocar a interface.

No painel, mostrar Agora, Trabalhando e Aguardando, mais frentes e dependências. Verde apenas para a entrega conferida; texto/ícone junto da cor. Recolher prompts longos e detalhes técnicos. Mostrar claramente o que falta para liberar a próxima etapa. Manter links profundos, cópia integral, teclado e leitura mobile. Não alterar estado no browser por clique.

Ao incorporar retornos, retirar prompts consumidos da fila de envio; preservar links de entrega e decisões relevantes. Git ou histórico já existente guarda o passado. Atualizar status canônico e derivados pelo mecanismo do projeto quando pertinente; não escrever manualmente um feed gerado.

## 7. Conferir e entregar

Fazer uma passada final contra todas as frentes nomeadas: há uma ação, owner e condição de término para cada lacuna? Há algo sem destinatário, sem entrada acessível ou parado? Não exigir que todo plano futuro esteja pronto para concluir a preparação atual.

Validar o que mudou: conteúdo, dependências, links e cópia; abrir desktop/mobile se o layout foi alterado. Não rodar CI de produto para validar um painel documental. Não iniciar tasks, enviar mensagens, delegar, fazer merge, limpar worktrees ou publicar remotamente sem autorização aplicável.

Começar a devolutiva do painel com:

**Cada frente tem estado comprovado, próximo passo e responsável — ou há algo faltando ou parado?**

Responder à pergunta com fatos, indicar os arquivos e o pequeno conjunto de próximos envios. Declarar separadamente edição, validação, commit/push/integração quando ocorrerem. Terminar quando a próxima ação autorizada estiver entregue; não prolongar com revisão recursiva.
