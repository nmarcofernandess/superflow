# Verificação do pacote de proposta — 23/09/2026

## Base e alcance

Superflow main@b99f78eee3251e3ac2ed4feffe04632a17ad0eb1. A entrega acrescenta apenas specs/, documentos e um protótipo público com dados fictícios. Não muda plugins/, CLI, manifests, versão, release ou projetos consumidores.

## Executado no exemplo

Playwright Python com Chromium, contexto offline e HTML carregado por set_content. Larguras 390, 768 e 1440 px. Não é ensaio do CLI ou do componente oficial.

- Nove cartões; inicialmente nenhuma seleção. Em desktop/tablet, dez arestas totais; selecionar writer deixa quatro; desselecionar recupera dez.
- Segundo clique, Mostrar tudo, Escape e clique na área vazia desfazem foco.
- Editor mostra referência visual-system fora do recorte, sem criar décimo cartão. Guide continua isolado e consultável.
- Sete precedências produzem cinco etapas: identity/clock; writer; editor/views; proof; release. Audit/guide ficam sem precedência declarada.
- Fonte writer ausente permanece como cartão de diagnóstico; a sequência não aparece. Ciclo release->writer também impede a sequência, sem apagar o mapa.
- Navegação por teclado, três abas sem overflow horizontal, zero pageerror e zero request de rede em cada largura.
- Texto com fechamento de script/tag e handler malicioso não executa nem cria img; labels permanecem texto.
- JSON incorporado no HTML equivale ao fixture example.json. Capturas desktop, sequência e mobile inspecionadas.

Esses resultados verificam a demonstração. Não certificam parser genérico, refresh, HTTP/CORS, múltiplos QGs ou integração do plugin; esses aceites pertencem a P01–P06.

## Verificação documental

Status contém somente os campos canônicos. plan.json tem seis tasks pending com dependências locais acíclicas. Links relativos do pacote conferidos. Os destinos futuros de código estão rotulados como propostos. Não há dados privados, tokens, bibliotecas remotas ou paths locais de usuário no asset.

## Não executado

Não foi executado npm test do Superflow, não houve instalação de dependências, implementação de --scope, mudança de feed.v4, publicação de release ou integração do runtime. A próxima entrega funcional é uma PR separada, sem merge automático.

## Verificação do ajuste de foco — 26/09/2026

Base: `a9c94cd9d338eb1fb6efcdfba9f8fa844e8a9b32`. Alteração restrita ao protótipo e à documentação desta demonstração. A integração do QG e as seis tasks do plano continuam pendentes.

- RED observado no HTML anterior: cartão secundário tinha `opacity=0.5`; a superfície inteira não bloqueava a passagem do traço. O teste recusou esse estado antes da alteração.
- GREEN em Chromium headless via Playwright, contexto offline com `set_content`, em 1440, 768 e 390 px. Zero `pageerror` e zero request HTTP(S) em cada largura.
- Desktop/tablet: dez relações no conjunto, quatro no foco de writer. No foco, endpoints geométricos ficam sob o centro dos cartões e não há marker-end; SVG tem z-index inferior e `pointer-events:none`. Hit-test numa parte do traço dentro do cartão resolve para o cartão, não para o SVG. Os cartões, incluindo `.dim`, têm opacidade 1.
- Segundo clique, Mostrar tudo, Escape e área vazia restauram as dez relações e as oito setas de direção do conjunto.
- Preservadas as cinco etapas calculadas, frentes isoladas, referência fora do recorte, diagnóstico de fonte ausente/ciclo, navegação por teclado e três abas sem overflow horizontal.
- Capturas antes/depois do foco em 1440 px e resultado em 768/390 px inspecionados. JavaScript extraído passou em `node --check`; fixture JSON incorporado permaneceu idêntico.

O ensaio é da demonstração, não do plugin instalado. Nenhum `npm test`, CLI, release, migration ou dado do consumidor foi executado/alterado nesta revisão. A entrega entra em PR, sem merge automático.


## Implementação integrada — 26/09/2026

Os relatos anteriores são históricos. Na candidata 0.13.0, npm test executou a validação completa: contratos Python, distribuição, browser, portabilidade e os novos testes de scope. Resultado: validate-all: passed.

test_scope.py cobre parser, projeção, ciclos, fontes ausentes, refresh seletivo, preservação de arquivo em falha e proteção das fontes. test_scope_browser.cjs cobre arquivo offline real, foco, drawer, sequência, troca de scope com mesmo feed, dados hostis inertes, ausência de fonte e larguras 390/768/1440. O asset editorial teve cópia e navegação verificadas.

Validação local não prova instalação nem publicação; essas etapas são verificadas no fechamento da release. O protótipo não é utilizado como substituto dos testes do runtime.
