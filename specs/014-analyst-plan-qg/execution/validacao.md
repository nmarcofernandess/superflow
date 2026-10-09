# Superflow 0.14.0 · validação e limites da candidata

**Estado:** PR Draft #23; base main@ea3f8b91be9791a12ba09f17f95c88f1b7c3ccc4.
**Entrega:** implementação e documentação na branch, sem merge, tag, release ou atualização de consumidores.

## Verificações efetivamente observadas nesta sessão

- Verificação GitHub: PR #23 existe, é Draft, destino main, e HEAD publicado inclui os arquivos de runtime, testes, skills, templates, docs e metadados 0.14.0.
- Validação sintática pelo mecanismo JavaScript V8: qg-detail.js, scope-view.js, runtime combinado qg-component.js + renderer de qg.html, e test_qg_detail.cjs foram compilados com sucesso como JavaScript, sem executar o DOM nem o navegador.
- Inspeção do empacotamento: package.json declara 0.14.0 e contém qg-detail.js, superflow_work.py, ANALYST.md e execution-contract.md; manifestos e marketplaces receberam a versão candidata.
- Inspeção do contrato estrutural: validate_superflow.py enumera a nova referência, template e arquivos runtime; validate-all.sh inclui os testes novos e o browser de detalhe.
- Inspeção da PR: nenhum merge/tag foi efetuado; os commits foram publicados apenas na branch de revisão.

Essas verificações **não** são equivalentes a testes Python, npm test, pacote npm instalado ou exercício no Chromium. Não alegar PASS desses cenários.

## Verificações ainda obrigatórias antes de tirar a PR de Draft

1. Em checkout descartável e limpo da branch, executar `npm ci`, `npm run test:setup` quando o Chromium não estiver provisionado e `npm test`. Registrar comandos, exit codes, versões de runtime e contagens efetivas.
2. Conferir em ambiente isolado a execução de `python3 -I plugins/superflow/scripts/superflow.py --root <fixture> check spec <spec>`, `feed` e `qg`, incluindo ausência de plano/ledger, dois planos com escolha explícita, retrofit 1→9→2 e symlink indevido.
3. Inspecionar no Chromium o QG status-only, o detalhe opt-in nas cinco abas, documento HTML inerte, mapa --scope, refresh/preservação de drawer e variações de 390/768/1440 px. O test_qg_detail.cjs foi adicionado, mas ainda não foi executado nesta branch.
4. Demonstrar o helper nativo `task-brief` sobre PLAN.md real e a identidade do ledger (fixture não prova dispatch de subagent). Se não houver subagents, classificar o método como inline, não SDD.
5. Realizar review final focado no parser nativo, retenção antes do cleanup, isolamento/publicação de fontes e contrato de distribuição. Corrigir achados causais, reexecutar o menor teste pertinente, depois a validação de release.
6. Conferir versão 0.14.0 em package/lock, três manifestos, marketplaces, CLI e pacote instalado, sem publicar release ou mudar instalações de consumidor.

## Aprovação e fronteiras

A versão 0.14.0 está **preparada para revisão técnica, ainda não aprovada para release**. O status global desta spec continua pending enquanto as verificações acima não produzirem evidência observável.

Nenhum `.superpowers/sdd` foi produzido nesta execução via conector GitHub. Não inventar ledger de execução nativo nem marcar tasks como completas sem as verificações contratadas. A ausência de `execution/progress.md` deve aparecer como falta de evidência, e não como execução concluída.

É proibido apresentar este documento como recibo de CI. A validação da candidata pertence ao repositório Superflow, não ao CI clínico do projeto consumidor.
