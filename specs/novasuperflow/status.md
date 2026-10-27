---
id: novasuperflow
title: Superflow como central de comando agnóstica
summary: Investiga a fronteira entre organização de entregas e execução, compara opções de QG compartilhado e apresenta decisões em um HTML didático.
status: pending
---

## Intenção
Análise para decisão de Marco. Distinguir correção rápida da hipótese maior de QG agnóstico.

## Estado real
Análise documental e HTML preparados em 27/10/2026. Anexo integral lido da Library (52 linhas, 6.568 bytes). Hipóteses H1–H5 avaliadas, arquiteturas comparadas e migração proposta, sem decisão de produto presumida. A validação estática e o ensaio isolado do resolvedor passaram. A inspeção visual local está bloqueada pela política do navegador para file://.

## Rastro
- Repositório: `nmarcofernandess/superflow`, checkout original `/Users/marcoantonio/superflow`.
- Base `main` / `origin/main`: `78b62b64e05a9b3b975e0bb5f91d9af78e7b8438`, confirmada por `ls-remote` em 27/10/2026.
- Branch: `novasuperflow`; não existia localmente nem no remoto.
- Worktree: `/Users/marcoantonio/Documents/Codex/2026-10-27/task-2/novasuperflow`.
- Devkit observado inicialmente em `40221ec2de18f26acde23f5ff7334a162da9ea66`.
- Dietflow-app observado inicialmente em `2e21aaea4ddc327ad73bb9ced21f87c320759483`.
- Anexo: Library `libfile_9f5e428417d48191af0f913f63c55db7`, `Texto colado(9).md`, file `file_0000000021c081f7ad3ba95e4756c288`.

## Próximo trabalho
Marco revisa as recomendações e o HTML. A inspeção visual manual foi solicitada. Para fechar a lacuna de fontes, receber o ledger original da sessão 132/02 e acesso autorizado ao código da v2 do Agora. Não começar implementação por consequência desta análise.

## Documentos
- [HTML didático](ANALISE.html): duas trilhas, mapas, roadmap real, hipóteses, arquitetura, migração e decisões.
- [Análise completa](ANALYST.md): evidência, inferência, propostas e limites.
- [Fontes e hashes](SOURCES.json).
- [Ensaio do resolvedor](EXPERIMENTOS.json).
- [Verificação](VERIFICACAO.md) e [resultado estático](STATIC-CHECK.json).

## Limites
Somente documentação de análise. Board Agora somente leitura; parent atualiza cards. Nenhuma implementação, push, PR ou merge. Worktrees alheias preservadas. A Library recusou a materialização do arquivo-fonte v2 do Agora por não verificar propriedade (404), sem contorno. Ledger ativo não recuperado. O navegador negou a abertura file:// e proibiu workaround; não foram tentados servidor HTTP nem outra superfície de browser. Renderização, navegação e legibilidade visual não foram verificadas.
