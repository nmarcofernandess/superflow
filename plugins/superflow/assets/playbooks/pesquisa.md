### Pesquisa — descobrir antes de dividir

Use quando **a lista do fan-out ainda não existe**: não se sabe quantos alvos há, quais
importam, nem quanto custa lê-los. Desenhar a leitura agora é chute. Um run só, e ele
termina no operador.

**RUN 1 · Reconhecimento** — 2 a 4 `reader`, `sonnet`, `effort: low`, `parallel`.

- **POR QUÊ** medir o corpus é barato e muda o desenho de tudo que vem depois.
- **EXTRAI** lista nominal de alvos · contagem por alvo · quais se referenciam · o FORA.
- **DoD** todo item do índice tem citação verbatim do pedido, e o FORA está escrito.

Medir é `grep -c`, `rg --files`, `find`, `wc` — sem abrir corpo de arquivo. O número do
fan-out seguinte sai da medição, nunca de "um por domínio". Nenhum agente corrige nada:
`corrige: "—"` em todos.

**Ponte.** `return { alvos[], custoPorAlvo{}, referencias[], fora[] }`.
**Suficiência:** alvo sem contagem faz o run rodar de novo — não atravessa.

**Devolve:** o índice nominal, o que ficou FORA e por quê, o custo medido, e o desenho do
run seguinte já dimensionado pelo que se mediu.
