// Task board da sprint ativa — dados de exemplo documentando o schema.
//
// USO: copie board.html + este arquivo (renomeado para board-data.js) para a
// pasta da sprint. board-data.js é o ÚNICO arquivo que a execução reescreve;
// board.html nunca é editado na sprint. O humano abre board.html via file://
// e dá refresh após cada atualização (script clássico funciona em file://;
// fetch/ES modules não).
//
// CONTRATO DE ATUALIZAÇÃO (piggyback, não ritual novo):
// - Plan (ou Execute na primeira task) cria o board a partir das tasks do plano.
// - Execute reescreve este arquivo no MESMO boundary em que atualiza
//   status.json: terminou task, inseriu pitstop, bloqueou. Status mudou e
//   board não = boundary não terminou.
// - QA fecha a última estação.
// - O board é PROJEÇÃO: PLAN/status/WARLOG continuam canônicos. Divergência
//   se resolve regenerando o board a partir deles, nunca o contrário.
//
// ESTADOS (exatamente estes 5):
// - "done"    entregue e verificado
// - "active"  em execução agora (vira o "VOCÊ ESTÁ AQUI" pulsante)
// - "queued"  na fila, ainda não começou
// - "blocked" parado aguardando decisão/dependência (diga o porquê em note)
// - "added"   pitstop: task/conversa/descoberta inserida no meio da corrida
//
// CAMPOS por task:
// - name (obrigatório)     nome curto da task
// - delivers (obrigatório) o RESULTADO que a task entrega, não a atividade
//                          ("CLI dry-run com gates verdes", nunca "fazer CLI")
// - state (obrigatório)    um dos 5 acima
// - note (opcional)        contexto curto: motivo do bloqueio, o que o pitstop
//                          decidiu, link mental para o humano

const BOARD = {
  spec: "001-exemplo-slug",
  sprint: "S1 — Exportação CSV filtrada",
  updated: "2026-07-19 14:30",
  next: "Rodar a prova de rota depois do teste focado passar",
  tasks: [
    {
      name: "Contrato do filtro",
      delivers: "Fonte de verdade única do filtro reutilizada pelo export",
      state: "done",
    },
    {
      name: "Action de export",
      delivers: "CSV com exatamente os registros visíveis, com teste focado",
      state: "active",
      note: "teste vermelho escrito; implementando o mínimo pra ficar verde",
    },
    {
      name: "Pitstop — decisão de encoding",
      delivers: "UTF-8 com BOM confirmado pro Excel; registrado no PRD",
      state: "added",
    },
    {
      name: "Botão na toolbar",
      delivers: "Export acionável na tela sem alterar filtros existentes",
      state: "queued",
    },
    {
      name: "Prova de rota",
      delivers: "PNG+JSON da jornada real; QA fecha a sprint",
      state: "queued",
    },
  ],
};
