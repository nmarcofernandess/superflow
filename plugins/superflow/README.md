# Superflow plugin

Este pacote oferece uma fonte pequena de trabalho vivo: PRD para promessa,
status.md para cadastro factual e plan.json quando a sequência precisa ser
controlada. O projeto continua dono de suas ferramentas, testes, CI, ship e
evidências.

## Fluxo

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
- status registra fase, andamento, espera, evidência e relações sem inferir
  sucesso.

## Receitas

| Receita | Use quando | Saída |
|---|---|---|
| [capture](assets/playbooks/capture.md) | uma ideia ou pedido ainda está em gathering | pacote local e próxima preparação explícita |
| [feature](assets/playbooks/feature.md) | há entrega autorizada | entrega verificada ou bloqueio real |
| [retomar](assets/playbooks/retomar.md) | é preciso continuar trabalho existente | próxima ação baseada em fontes atuais |
| [fechar](assets/playbooks/fechar.md) | a entrega pede aceite | done com prova, ou reabertura honesta |
| [reconciliar](assets/playbooks/reconciliar.md) | cadastro e realidade divergem | fonte e projeção coerentes |

Este README é o índice único das receitas; não há README paralelo na pasta de
playbooks.

## Referências e templates

| Recurso | Consulta |
|---|---|
| [state contract](assets/references/state-contract.md) | Ao editar status.md, relações, tasks ou evidência. |
| [commands contract](assets/references/commands-contract.md) | Ao usar new, check, feed ou qg. |
| [quality contract](assets/references/quality-contract.md) | Ao planejar, revisar, testar ou fechar comportamento. |
| [PRD](assets/templates/PRD.md) | Ao criar ou amadurecer PRD. |
| [status](assets/templates/status.md) | Como exemplo de cadastro manual. New emite status programaticamente. |
| [analysis](assets/templates/analysis.md) | Quando a investigação precisa persistir. |
| [SPEC](assets/templates/SPEC.md) | Quando arquitetura precisa ficar explícita. |
| [plan](assets/templates/plan.json) | Quando a sequência requer tasks. |

## Uso da CLI

    python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo>
    python3 -I <plugin>/scripts/superflow.py --root <repo> check
    python3 -I <plugin>/scripts/superflow.py --root <repo> feed --output <feed.json>
    python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>

Python 3.9 ou superior é necessário. A interface, os efeitos e os exit codes
estão em assets/references/commands-contract.md.

## Migração

Documentos anteriores sem status.md entram como diagnóstico
UNREGISTERED_DOCUMENTS; eles não viram tickets automaticamente. O censo de
migração do consumidor decide o destino de cada item. Status.md inválido é
erro; evidência local ausente também é erro. Referências HTTPS são preservadas,
mas o check estrutural não consulta a rede.

Status.json, HANDBOOK, logs de implementação/revisão, WARLOG, board, sprint e
campanha pertencem ao contrato aposentado. Não os crie em novos pacotes.
