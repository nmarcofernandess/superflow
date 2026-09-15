# Superflow

Superflow ajuda a registrar e conduzir trabalho de forma proporcional. A fonte
da promessa é o PRD; análise, arquitetura e plano entram somente quando a
situação precisa deles.

    pedido
      -> PRD
      -> analyst, build ou plan quando necessário
      -> execução, review e QA do projeto
      -> aceite e estado factual

O plugin não é um executor, board, campanha, sprint ou sistema paralelo de
provas. Ele usa fontes do repositório e suas ferramentas nativas.

## O que o plugin exporta

| Skill | Responsabilidade |
|---|---|
| superflow | Escolhe uma receita curta sem pré-carregar toda a biblioteca. |
| prd | Cria ou amadurece a promessa, escopo e aceite. |
| analyst | Faz recon, examina facetas relevantes e devolve o PRD corrigido. |
| build | Fecha arquitetura e reuso em SPEC quando há decisão técnica material. |
| plan | Cria plan.json quando sequência e dependências justificam. |
| review | Examina desenho ou diff com evidência e rechecagem. |
| status | Mantém o retrato completo, a orientação de continuidade e as relações entre specs. |

As cinco receitas são capture, feature, retomar, fechar e reconciliar. Execute
e QA permanecem etapas do fluxo, operadas pelas regras e ferramentas do projeto,
sem skills separadas.

## Estado e arquivos

Toda spec tem PRD e status; arquitetura e plano são condicionais e independentes.
O plano com task pendente é o cursor da execução; `Próximo trabalho` no status
orienta a continuidade. `relations` preserva vínculos sem decidir bloqueios.

Um pacote pode conter:

    specs/<id-ou-slug>/
      status.md
      PRD.md
      SPEC.md
      plan.json

Somente status.md e PRD.md surgem no comando new. Os demais são condicionais.
Os [contratos](plugins/superflow/assets/references/) de estado e comandos acompanham o pacote.

## Comandos

O runtime é Python 3.9 ou superior e usa modo isolado:

    python3 -I <plugin>/scripts/superflow.py --root <repo> new <slug> --title <titulo> --summary <resumo>
    python3 -I <plugin>/scripts/superflow.py --root <repo> check status
    python3 -I <plugin>/scripts/superflow.py --root <repo> check spec <spec>
    python3 -I <plugin>/scripts/superflow.py --root <repo> feed --output <feed.json>
    python3 -I <plugin>/scripts/superflow.py --root <repo> qg --output <qg.html>

New exige um resumo humano do tema e cria o cadastro inicial. Check é somente
leitura e relata conteúdo incompleto ou inválido como diagnóstico editorial;
feed e QG preservam esses diagnósticos na mesma fotografia. Eles nunca executam
proof, ship ou outro comando configurado pelo repositório.

O QG abre em **Em aberto**, com minispecs aninhadas sempre visíveis. O card
mostra o título e o resumo durável para escolher; o card inteiro abre o drawer com a narrativa completa do
`status.md`. Não há tarefas, arquivos, progresso ou graph no QG. A busca cobre
o conteúdo completo e abre a cadeia até a minispec. **Concluídas** é uma visão
separada. Uma spec concluída pode aparecer como contexto de filhos abertos.

## Instalação

O pacote publicado é uma release completa. Personalizações pertencem ao projeto
consumidor, fora do diretório instalado.

Instale uma release identificada por tag e confira a versão declarada nos
manifestos antes de usar:

    codex plugin marketplace add nmarcofernandess/superflow --ref v0.10.2
    codex plugin add superflow@superflow

Em Claude Code:

    claude plugin marketplace add nmarcofernandess/superflow@v0.10.2
    claude plugin install superflow@superflow

Para atualizar um marketplace já cadastrado, use `codex plugin marketplace upgrade superflow` seguido de `codex plugin add superflow@superflow`, ou `claude plugin marketplace update superflow` seguido de `claude plugin update superflow@superflow`. Se o marketplace estiver preso a uma tag antiga, altere a referência na configuração do host antes de atualizar.

Após atualizar, abra uma nova task para recarregar o inventário de skills.

## Materiais da spec

A spec reúne registros e materiais autocontidos da entrega. Código, testes,
configuração e outros artefatos permanentes recebem um local canônico no
projeto. Scripts temporários são removidos ao fechar ou promovidos com seus
consumidores. HTMLs e receipts históricos podem permanecer na spec.
Ferramentas de gestão de specs podem ler seus artefatos declarados.
A explicação completa vive no contrato de estado.

## Desenvolvimento

A fonte do plugin é plugins/superflow. A validação local existente confere o conjunto
exato de sete diretórios de skills, referências internas e conteúdo do pacote.
Leia o [README do plugin](plugins/superflow/README.md) para uso; leia
a [SPEC atual](SPEC-superflow-plugin.md) para as decisões técnicas.

### Incorporar a lista de specs

`qg --embed --output fragmento.html` gera um fragmento autocontido para inserir em outro HTML. Usa o mesmo renderer do standalone com CSS e IDs isolados por Shadow DOM. Regere e substitua o fragmento quando as fontes mudarem; a navegação do hospedeiro permanece independente. Detalhes em `plugins/superflow/assets/references/commands-contract.md`.
