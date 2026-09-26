# Estados, dependências e retomada

## Estados do encaminhamento

Não são os estados da spec nem das tasks de `plan.json`. A conclusão de um
encaminhamento não altera `status.md`. `evidence` aponta as fontes canônicas;
`fronts` agrupa o trabalho humano sem criar outro cadastro de specs. O painel
pode reunir fontes de vários projetos; o mapa QG `--scope` continua por projeto.
Não atribuir `done` de spec a partir deste JSON.

| ID do asset | Nome | Critério |
|---|---|---|
| preparation | Em preparação | Ainda falta contexto ou redação sob responsabilidade da orquestradora. |
| prepared_waiting | Prompt preparado | Texto completo, mas envio precisa de uma entrada/decisão nomeada. |
| ready_to_send | Pronto para enviar | Prompt completo, destinatário adequado, fontes acessíveis e entradas necessárias disponíveis. |
| sent_awaiting | Enviado / aguardando | Envio confirmado pelo operador ou ferramenta autorizada; registrar chat/data. |
| decision_pending | Decisão pendente | Pergunta, recomendação, consequências e material prontos para o decisor. Sem esse material, ainda é preparação. |
| in_review | Em revisão | Entrega recebida, aguardando conferência de suficiência. |
| ready_to_implement | Pronto para implementar | Escopo/plano suficientes, entradas e autorizações aplicáveis satisfeitas; implementação ainda não começou. |
| in_progress | Em execução | Executor e unidade identificados, trabalho em andamento. |
| done | Concluído | Resultado e validação conferidos; integração provada quando era parte da entrega. |

`stalledReason` é alerta transversal: causa + quem destrava, sem converter automaticamente para outro estado. Falha, silêncio ou base movida não significam produto quebrado nem abandono. Classificar o que falta observar.

Nem toda unidade percorre todos os estados. Um ajuste local autorizado pode ir de preparação a execução. Uma pesquisa encerrada pode ir de revisão a concluído. Uma decisão pode devolver o plano para preparação. Não exigir etapas ou aprovações que o pedido não exige.

## Dependência precisa dizer onde limita

Exemplos:

- “Pesquisa B pode começar; implementação aguarda a interface entregue por A.”
- “Prompt B está escrito, mas depende do resultado A para poder ser enviado.”
- “Core passou; página composta aguarda a fonte transversal C.”
- “Testes focais independentes usam a mesma fila, então executar em série.”

Não bloquear o domínio inteiro por um caso nem inferir aplicabilidade por proximidade. Um miniapp sem exportação não recebe essa dependência só porque outros módulos exportam.

## Contrato leve do HTML

Editar somente o JSON no elemento `script#orquestra-data` para mudanças de conteúdo. Proteger `<` dentro de strings como `\u003c` ao serializar, para não encerrar o elemento script. Textos são renderizados como texto, não HTML. Não colocar segredos ou dados pessoais.

Campos da raiz:

- `title`, `summary`: nome e propósito do acompanhamento.
- `observedAt`: data da última conferência; vazia significa ainda não conferido.
- `demo`: true apenas no asset demonstrativo.
- `handoff`: lista de `{label, href}` para fontes/continuidade canônicas acessíveis.
- `fronts`: `{id, title, summary}`; IDs estáveis com letras minúsculas, números e hífen.
- `items`: lista das unidades abaixo, na ordem de leitura sugerida.

Unidade:

```json
{
  "id": "core-plan",
  "front": "core",
  "title": "Preparar o plano do core atual",
  "state": "ready_to_send",
  "owner": "Operador envia → planejador",
  "summary": "Objeto concreto desta próxima unidade.",
  "nextAction": "Enviar este prompt ao planejador; devolver os arquivos para revisão.",
  "doneWhen": "Plano suficiente e revisado para o executor indicado.",
  "dependsOn": [],
  "evidence": [{"label": "Fonte e revisão conferidas", "href": "./status.md"}],
  "prompt": "Texto completo e específico a ser encaminhado.",
  "stalledReason": ""
}
```

`dependsOn` contém `{id, stage, reason}`. `stage` explicita se limita envio, decisão, implementação ou publicação; é texto legível, não máquina de aprovação. O HTML apresenta as arestas, não deduz status de dependentes. `evidence` pode apontar status, código, PR, relatório ou decisão, conforme a tese; link sozinho não prova que foi lido. `done` exige evidência pertinente e não prova toda a frente.

Sem serviço, API, banco, localStorage ou sync. O HTML é fotografia publicada pela IA; não observa automaticamente Git/chats. Não representa uma nova SPEC. Fontes do projeto continuam donas de sua verdade.

## Quando voltar uma entrega

1. Conferir o que foi entregue e a sua condição terminal.
2. Separar documento, teste, observação visual, PR, merge e deploy.
3. Reconciliar o status dono se autorizado; atualizar o painel com fonte e data.
4. Liberar só os sucessores cujas entradas chegaram; preparar o próximo prompt que faltar.
5. Registrar no arquivo curto de continuidade decisões atuais, responsáveis e próxima retomada.

## Checkpoints mínimos do método

- Prompt copiado, sem envio confirmado → permanece pronto para enviar.
- PR draft documental recebida → em revisão, não produto concluído.
- Plano insuficiente → achado nominal e prompt de correção, sem pesquisar o universo de novo.
- Decisão técnica profunda aberta → prompt de análise; não preencher com escolha improvisada.
- Entrega comprovada de uma unidade → verde nessa unidade; frente continua aberta se tiver outras.
- Usuário informa “enviei” → registrar enviado sem pedir a confirmação novamente.
