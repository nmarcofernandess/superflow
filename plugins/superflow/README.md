# Superflow plugin

Este pacote oferece uma fonte pequena de trabalho vivo: PRD para promessa,
status.md para cadastro factual e plan.json quando a sequência precisa ser
controlada. O projeto continua dono de suas ferramentas, testes, CI, ship e
evidências.

## Fluxo

O status exige `id`, `title`, `summary` e `status`; `relations` é opcional.
O resumo explica o tema, e o corpo descreve o retrato e o próximo trabalho.
Relações guardam contexto, sem controlar execução; o plano com tasks pendentes
é o único cursor da sequência quando existir.

    pedido -> PRD
                 -> analyst para dúvida material
                 -> build para arquitetura necessária
                 -> plan para sequência necessária
                 -> execução -> review -> QA ou proof -> done

Nenhuma fase é obrigatória por formato. Uma correção simples pode usar PRD
conciso, execução direta e uma verificação útil. Uma entrega não vira done só
porque há prosa, arquivo arquivado ou mensagem de sucesso.

## Skills

- superflow escolhe a receita adequada.
- prd escreve a promessa, escopo e aceite verificável.
- analyst faz recon, examina facetas relevantes e decide reuso, adaptação ou
  criação com evidência.
- build fecha uma SPEC quando decisões de arquitetura são necessárias.
- plan escreve plan.json para unidades verificáveis e dependências locais.
- review confronta desenho ou diff com fontes e efeitos reais.
- status mantém o retrato completo, a orientação de continuidade e as relações entre specs sem
  inferir sucesso.

## Receitas

| Receita | Use quando | Saída |
|---|---|---|
| [capture](assets/playbooks/capture.md) | uma ideia ou pedido ainda está sendo definido | pacote local e próxima preparação explícita |
| [feature](assets/playbooks/feature.md) | há entrega autorizada | entrega verificada ou bloqueio real |
| [retomar](assets/playbooks/retomar.md) | é preciso continuar trabalho existente | próxima ação baseada em fontes atuais |
| [fechar](assets/playbooks/fechar.md) | a entrega pede aceite | aceite próprio conferido ou trabalho restante explícito |
| [reconciliar](assets/playbooks/reconciliar.md) | cadastro e realidade divergem | fonte e projeção coerentes |

Este README é o índice único das receitas; não há README paralelo na pasta de
playbooks.

## Referências e templates

| Recurso | Consulta |
|---|---|
| [state contract](assets/references/state-contract.md) | Ao editar status.md, relações ou plan.json. |
| [commands contract](assets/references/commands-contract.md) | Ao usar new, check, feed ou qg. |
| [PRD](assets/templates/PRD.md) | Ao criar ou amadurecer PRD. |
| [status](assets/templates/status.md) | Como exemplo de cadastro manual. New emite status programaticamente. |
| [SPEC](assets/templates/SPEC.md) | Quando arquitetura precisa ficar explícita. |
| [plan](assets/templates/plan.json) | Quando a sequência requer tasks. |

## Uso da CLI

    python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo> --summary <resumo>
    python3 -I <plugin>/scripts/superflow.py --root <repo> check status
    python3 -I <plugin>/scripts/superflow.py --root <repo> check spec <spec>
    python3 -I <plugin>/scripts/superflow.py --root <repo> feed --output <feed.json>
    python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>

Python 3.9 ou superior é necessário. A interface, os efeitos e os exit codes
estão em assets/references/commands-contract.md.
Diagnósticos editoriais permanecem visíveis e não controlam CI ou ship do projeto.

## Materiais da spec

A spec reúne registros e materiais autocontidos da entrega. Código, testes,
configuração e outros artefatos permanentes recebem um local canônico no
projeto. Scripts temporários são removidos ao fechar ou promovidos com seus
consumidores. HTMLs e receipts históricos podem permanecer na spec.
Ferramentas de gestão de specs podem ler seus artefatos declarados.
A explicação completa vive no contrato de estado.
