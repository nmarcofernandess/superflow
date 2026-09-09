### Grill loop — apertar até passar na régua

Use quando existe uma **régua concreta** (uma referência, um critério, um exemplo bom) e o
trabalho precisa bater nela. Sem régua escrita antes, não é grill: é opinião em rodadas.

**Duas formas, e elas não são intercambiáveis:**

| | adversarial | iterativo |
|---|---|---|
| forma | N críticos **frescos**, cada um tentando refutar | um crítico que **lembra** as rodadas anteriores |
| serve para | matar achado plausível-mas-errado | apertar a mesma peça em rodadas |
| Claude Code | nativo — todo agente é fresco | **não existe**: o loop mora dentro do prompt de um agente |
| Codex | `spawn_agent {fork_turns: "none"}` | `followup_task` no mesmo agente |

**O pior caso é uma multiplicação, e ela vai no cabeçalho.**
`rodadas × (construtores + críticos) + fixos`. Três rodadas sobre oito peças com um
crítico cada não são 8 agentes: são 51. O número não é proibido — a frase que o explica é
obrigatória, e quem olha decide antes de pagar.

Todo loop declara as três coisas: **condição de parada**, **`maxRounds`**, e **memória do
que já foi refutado**. Sem a memória, o que o crítico matou reaparece na rodada seguinte e
o loop nunca converge.

**Quem critica corrige**, se tem permissão de escrita. Crítico que só aponta transforma
cada reprovação numa volta inteira — foi assim que três rodadas viraram cinco horas.

**Devolve:** a régua usada, o que passou e o que não passou nela, quantas rodadas cada
peça levou, e o que ficou reprovado no fim com o motivo.
