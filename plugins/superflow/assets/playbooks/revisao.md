### Revisão — achar defeito e provar que é defeito

Use para varrer em busca de defeitos quando achado plausível-mas-errado custa caro. A
forma é `pipeline`: cada dimensão acha e verifica sem esperar as outras.

**RUN 1 · Achar e verificar** — uma dimensão por `reader`, depois verificação por
`fixer`, `opus`, `effort: high`.

- **POR QUÊ** achado sem verificação independente vira lista que ninguém confia.
- **EXTRAI** achados confirmados, com endereço `arquivo:linha` e o cenário de falha.
- **DoD** todo achado ou foi confirmado, ou foi refutado com o motivo — nenhum fica no meio.

**O verificador corrige.** Ele tem o material na mão; devolver lista para outro consertar
é a volta mais cara que existe (L3). Se a revisão for auditoria somente-leitura, declare
`somenteLeitura: true` — e aí ele **registra** em `qa-v<N>.md`, sem tocar no objeto.

**Lentes distintas batem redundância.** Três céticos idênticos acham o mesmo; correção,
segurança, desempenho e reprodutibilidade acham coisas diferentes. Quando um achado pode
falhar de mais de um jeito, dê uma lente a cada verificador.

**Barreira só para deduplicar.** Se dois achadores podem achar o mesmo defeito, junte
antes de verificar — verificar duplicata é pagar duas vezes. Fora disso, `pipeline`.

**Devolve:** os achados confirmados em ordem de gravidade, o que foi refutado e por quê,
o que não deu para verificar, e o que foi corrigido de fato.
