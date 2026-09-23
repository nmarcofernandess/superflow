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
