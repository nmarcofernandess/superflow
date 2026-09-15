# SPEC: plugin Superflow enxuto

## Intenção

Superflow mantém um fluxo proporcional e uma fonte factual de trabalho. PRD descreve a promessa; status.md reúne cadastro, resumo durável e retrato; SPEC registra decisões técnicas materiais; plan.json registra uma sequência quando necessário. SPEC e plano são independentes e condicionais.

## Superfícies públicas

Sete skills: `superflow`, `prd`, `analyst`, `build`, `plan`, `review`, `status`.
Cinco receitas: `capture`, `feature`, `retomar`, `fechar`, `reconciliar`.
Duas referências: `state-contract` e `commands-contract`.
Quatro templates: PRD, status, SPEC e plano.

Execute e QA são ações nas receitas e usam as ferramentas do projeto. Rota é um plugin separado.

## Estado e relações

Status.md exige frontmatter com `id`, `title`, `summary` e `status`; este aceita `pending | done`. `relations` é opcional, com objetos `id` e `reason`. Destinos existem, são distintos da própria spec e não duplicados. Ciclos são válidos: as relações preservam memória e não controlam execução.

O corpo Markdown é o retrato completo. `Próximo trabalho` orienta continuidade e condições relevantes. O resumo explica o tema durável para quem não lembra da spec, preferencialmente em uma ou duas frases. Cadastro com resumo permite apresentação mesmo sem corpo.

Hierarquia de mãe e minispecs deriva do path; minispec aberta não reabre a mãe. O QG oferece Em aberto, Concluídas, busca, famílias, relações e narrativa integral no drawer. Uma mãe concluída aparece como contexto dos filhos abertos. Relações inversas são derivadas, e seus destinos podem ser abertos fora da visão atual.

Plan.json contém tasks com exatamente `id`, `task`, `status`, `depends_on` e `acceptance`. Dependências de tasks são locais e acíclicas. Um plano com task `pending` está ativo e é o único cursor de tasks. Um plano totalmente concluído permanece registro encerrado. O status muda quando muda direção, autorização, espera relevante, relação, divisão de escopo ou handoff, sem duplicar cada conclusão de task.

## Runtime

Python 3.9 ou superior, em modo isolado, expõe `new`, `check status`, `check spec`, `feed` e `qg`, com raiz explícita. New exige resumo humano e cria somente PRD e status, preservando proteção contra IDs e destinos já ocupados. Check spec relata diagnósticos nos dois obrigatórios e em SPEC/plano quando presentes, sem inferir prontidão ou controlar CI/ship. Os status da coleção permitem conferir os destinos das relações.

Feed e QG leem exclusivamente status.md. O snapshot `superflow.feed.v4` contém resumo e relações. O parser YAML é seguro, e PyYAML acompanha o pacote. A gravação de feed/QG é atômica; a serialização do conteúdo preserva a fronteira entre dados e código do HTML.

## Autoria e verificação

Analyst e Build investigam realidade, facetas relevantes e reuso. Review confronta contratos e resultado com verificação proporcional ao risco. Fechar respeita aceites, provas e autorização do projeto.

A fronteira do pacote é explicada em `state-contract.md`: materiais da spec são autocontidos; infraestrutura permanente recebe localização canônica no projeto. Ferramentas de gestão de specs podem ler seus artefatos declarados. Tasks com scripts temporários declaram condição de remoção ou promoção nos campos existentes; o fechamento confere seu destino.

## Distribuição

Os manifests Codex e Claude descobrem as skills do pacote. As releases são pacotes completos e versionados; customizações do consumidor ficam fora do diretório instalado. A validação local existente confere conteúdo, referências e comportamento. O canal Node opcional distribui runtime, assets, vendor e licenças; a CLI continua Python.
