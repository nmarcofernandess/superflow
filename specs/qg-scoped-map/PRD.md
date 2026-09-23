# QG por escopo: ver o conjunto sem construir outro gestor

**Estado:** proposta, não feature instalada. **Base examinada:** main@b99f78eee3251e3ac2ed4feffe04632a17ad0eb1 (0.12.3).

## Propósito

Uma entrega pode depender de várias specs e ainda assim ter um propósito simples. O operador precisa reconhecer esse propósito, os donos das contribuições, o que vem antes e quais frentes não possuem precedência declarada entre si. Concluir uma contribuição não pode apagar o restante da promessa.

A origem visual é um painel de acompanhamento aprovado pelo operador: fundo claro, cabeçalho verde, frentes em colunas, conexões tipadas e detalhe lateral. Este pacote preserva essa linguagem, mas usa somente exemplos fictícios. Nenhum handbook, link privado, segredo ou dado de paciente acompanha o asset público.

## Histórias e aceite

- **R01 — conjunto e foco:** abrir com todas as linhas; selecionar uma frente destaca sua vizinhança; clicar nela novamente, usar Mostrar tudo, Escape ou área vazia volta ao conjunto. Teclado e celular possuem alternativa textual completa.
- **R02 — composição opcional:** um recorte seleciona IDs e pode explicar a contribuição de cada spec. Nenhum campo novo em status.md e nenhum status/percentual paralelo no sprint.
- **R03 — semântica:** uma relação duradoura contextual não implica ordem. Aresta de evidência também não bloqueia sozinha. Só uma precedência editorial explícita participa da sequência.
- **R04 — sequência legível:** grupos topológicos das precedências mostram etapas candidatas. Na mesma etapa não há precedência declarada entre as frentes; isso não garante recursos, arquivos distintos, autorização ou prontidão.
- **R05 — ausência honesta:** distinguir frente isolada válida, relação fora do recorte e fonte ausente/ambígua. Nada desaparece silenciosamente do sprint por perder seu cadastro. Ciclo de precedência impede sugerir uma ordem válida; ciclo contextual não é erro.
- **R06 — atualização e portabilidade:** preservar a lista padrão, fotografia offline, fonte HTTP opcional, Shadow DOM e refresh oficial. Estado novo vem do feed; composição nova vem do arquivo do escopo, não de inferência sobre prosa.
- **R07 — adoção proporcional:** sem arquivo de escopo, o QG permanece como está. Não desenhar o grafo de todo o repositório por padrão. Sem novo serviço, servidor, persistência browser ou dependência de layout.

## O que mora onde

| Fonte | Autoridade |
|---|---|
| status.md | ID, título, resumo, estado factual, narrativa e relações duradouras. |
| plan.json da spec | Tasks, dependências locais e cursor de execução. Não é copiado nem lido para calcular este mapa v1. |
| .superflow/scopes/<slug>.json | Membros exatos do recorte, propósito, agrupamento visual e precedências editoriais explicadas. |
| HTML/feed | Projeções regeneráveis. Nunca gravam conclusão ou autorização. |

Uma spec pode integrar dois sprints diferentes sem ser alterada. A contribuição parcial é descrita por focus no membro; o estado exibido continua explicitamente sendo o da spec inteira. Um requisito realmente executável permanece no plano/contrato do owner; não nasce de uma seta.

## Alternativas consideradas

1. **Adicionar sprint/order/lanes ao status.md:** rejeitada. Contamina a spec com uma perspectiva temporária e cria colisão quando participa de mais de uma entrega.
2. **Derivar ordem de relations:** rejeitada. O contrato permite ciclos e declara que relations não decide bloqueios.
3. **Scope editorial separado + feed factual:** recomendada. Pouca autoria manual, estado automático e nenhuma segunda fonte de execução.

## Recorte v1

Um projeto por escopo; IDs já cadastrados; grupos opcionais; três tipos de aresta; conjunto/foco; sequência; diagnósticos; consumo da narrativa canônica. Não há editor drag-and-drop, scheduler, estimativas, recursos, status de tasks, cross-repo, votação, IA inferindo dependências ou atualização automática da prosa.

## Por que uma spec, não um patch direto no runtime

README.md e SPEC-superflow-plugin.md hoje excluem graph/sprint do QG e limitam sua leitura aos status. Acrescentar um arquivo de composição altera uma fronteira pública de leitura e refresh. Este pacote fecha o desenho antes de mudar essa fronteira; a implementação futura deve alterar o contrato explicitamente e entrar por PR sem merge automático.

O [protótipo](assets/mapa-sprint.html) é a referência de UX; a [SPEC](SPEC.md) é a referência semântica; [IMPLEMENTATION.md](IMPLEMENTATION.md) destila paths, interfaces e provas. As tasks futuras permanecem pending.
