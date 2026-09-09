### Jornada do superflow — ideia até execução

Use quando o trabalho atravessa fases do superflow e a fase seguinte depende do resultado
da anterior. **Não redecida as fases:** `../references/routing-protocol.md` já decide por
Source, Maturity e Risk. Este playbook só diz como executar a jornada escolhida.

**O default entre fases é `serial`.** `status.json` é mencionado por 11 skills e é o hub
do pacote: dois nós em paralelo, cada um rodando uma skill do superflow, colidem nele.
Paralelo aqui é a exceção que justifica.

| nó | papel | invoca | produz |
|---|---|---|---|
| taskgen | writer | skill `taskgen` | `specs/NNN/` + `PRD.md` |
| analyst | writer | skill `analyst` | `analysis.md` |
| plan | writer | skill `plan` | `implementation_plan.json` |
| execute | writer | skill `execute` | código + `implementation_log.json` |
| qa | fixer | skill `qa` | `qa_report.md` + correções |

**Faceta não é agente.** O `analyst` escreve quatro facetas — Produto, Backend, Frontend,
Copy — e uma Síntese que as amarra, e o contrato dele diz, verbatim, *"not a paste of
three sections"*. Um agente por faceta produz exatamente a colagem que ele proíbe, além de
quatro escritores no mesmo `analysis.md`. **Um artefato, um escritor.**

**Nó que invoca skill não delega.** `podeDelegar: false` em todos: a conta de agentes do
plano só vale se ninguém abrir uma frota por dentro. Quando um nó precisar delegar, o
plano escreve quanto ele pode gastar e isso entra no pior caso.

Corte em runs onde o operador decide: normalmente depois do `analyst` (a análise muda o
plano) e depois do `plan` (o plano muda a execução).

**Devolve:** o pacote em `specs/NNN/`, o que cada fase produziu com o caminho, o que ficou
pendente com dono, e a fase seguinte já desenhada.
