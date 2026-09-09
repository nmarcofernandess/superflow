# Playbooks de rota

Um playbook é **um plano já preenchido que se copia e se edita** — não um formulário
obrigatório. A ordem é sempre: modelo primeiro (`../templates/plano.json`), playbook
depois. Se nenhum encaixa, preenche-se o modelo do zero; isso não é falha do trabalho, é
sinal de que aquela jornada ainda não tem playbook. Se ela se repetir, nasce um.

Cada playbook diz **quando usar**, dá os runs com POR QUÊ / EXTRAI / DoD, e termina em
**Devolve:** — o que a resposta tem de conter. Nenhum deles redecide fase: isso é do
`routing-protocol.md`.

| playbook | quando |
|---|---|
| [pesquisa](pesquisa.md) | não dá para escrever a lista do fan-out ainda |
| [jornada-superflow](jornada-superflow.md) | ideia → PRD → análise → plano → execução |
| [migracao](migracao.md) | N alvos conhecidos, mesma transformação |
| [revisao](revisao.md) | achar defeito e provar que é defeito |
| [grill-loop](grill-loop.md) | apertar até passar numa régua |
