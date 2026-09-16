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

    codex plugin marketplace add nmarcofernandess/superflow --ref v0.12.2
    codex plugin add superflow@superflow

Em Claude Code:

    claude plugin marketplace add nmarcofernandess/superflow@v0.12.2
    claude plugin install superflow@superflow

No Cursor, o marketplace do repositório já declara o plugin. Importe o GitHub e instale `superflow`:

    agent plugin marketplace add https://github.com/nmarcofernandess/superflow --git-ref v0.12.2

Depois, no Agent, abra `/plugin`, escolha Superflow no Marketplace e instale no escopo user. Para teste local, copie o pacote para o diretório que o Cursor lê sem marketplace:

    cp -R plugins/superflow ~/.cursor/plugins/local/superflow

Para atualizar um marketplace já cadastrado, use `codex plugin marketplace upgrade superflow` seguido de `codex plugin add superflow@superflow`, ou `claude plugin marketplace update superflow` seguido de `claude plugin update superflow@superflow`, ou `agent plugin marketplace update` e reinstale Superflow em `/plugin`. Se o marketplace estiver preso a uma tag antiga, altere a referência na configuração do host antes de atualizar.

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

## Incorporar a lista de specs

O QG gerado é autocontido: runtime e snapshot incorporados. Abre por duplo clique sem servidor. `qg --online <URL-do-feed> --output painel.html` acrescenta uma fonte HTTP opcional; começa na fotografia incorporada e conserva a última leitura válida se a rede falhar.

`qg --embed --output fragmento.html` produz o componente para qualquer ponto de outro HTML. O host declara `src` opcional, `ids` opcional e `refresh-seconds` opcional. IDs ausentes deixam de aparecer; Shadow DOM isola CSS e IDs. Atualizações preservam busca e drawer, e não recriam o DOM quando `snapshot_id` não muda.

`feed` publica `.superflow/feed.json` e `.superflow/qg.js`. A URL HTTP é escolhida e mapeada pelo host do consumidor; `/superflow/feed.json` é um exemplo, não um caminho obrigatório. Atualizar esse feed permite que os leitores HTTP acompanhem a nova fotografia. A leitura pelo navegador não regrava o HTML e não cria cache persistente.

`qg --refresh painel-a.html painel-b.html` publica o mesmo snapshot nos componentes indicados, preservando o restante dos hosts e seus filtros. Sem caminhos, lê a lista opcional `qg_outputs` da configuração. Em hosts de vários projetos, `--source <URL>` seleciona os componentes pela fonte declarada. Não há descoberta automática de destinos.

**Este painel funciona sem servidor com o retrato incorporado. Para acompanhar atualizações publicadas, configure uma URL HTTP do feed. Para atualizar a fotografia portátil, execute o comando de atualização.**

O contrato de comandos explica HTTP/CORS, publicação e limites. Arquivo local buscando feed HTTP depende de CORS; F5 de uma página servida por HTTP depende de o host continuar disponível.

### Verificação do componente

A suíte Python roda com `bash scripts/validate-all.sh`. Com Playwright disponível no ambiente (ou via `NODE_PATH`), execute `node plugins/superflow/scripts/test_qg_browser.cjs` e `node plugins/superflow/scripts/test_qg_portable.cjs`. O segundo cobre arquivo local real, HTTP com e sem CORS, queda do host, polling e preservação do último retrato válido. `SUPERFLOW_CHROME=1` usa a instalação local do Google Chrome; por padrão usa Chromium. Os ensaios são temporários e não instalam dependências nos consumidores.
