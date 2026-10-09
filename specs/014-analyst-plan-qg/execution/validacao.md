# Superflow 0.14.0 — validação da candidata

Validação local realizada em 08/10/2026 na lane exclusiva `superflow-014-validation`, a partir de `b0177d0ae9134c4918653f1649a0e5ee38ca19b4`, com base `main@ea3f8b91be9791a12ba09f17f95c88f1b7c3ccc4`.

## Resultado observado

- Node v24.20.0, Python 3.9.6 e Chromium provisionado pelo Playwright 1.63.0 do projeto.
- `npm ci`: exit 0, duas dependências instaladas, nenhuma vulnerabilidade reportada.
- Primeira execução de `npm test`: parou em comparações de paths dos testes novos. No macOS, o runtime normaliza `/var` para `/private/var`; três expectativas foram corrigidas com `Path.resolve()`, preservando as recusas de symlinks e escapes.
- `python3 -I plugins/superflow/scripts/test_work.py` após a correção: exit 0, 27 testes.
- `npm test` após a correção: exit 0; estrutura válida; 76 testes Python (17 model, 27 work, 15 commands, 9 qg, 8 scope); distribuição válida; quatro ensaios Chromium aprovados; `validate-all: passed`.
- Distribuição: empacotamento e instalação em consumidor temporário, metadados 0.14.0, versão do CLI e uso isolado do runtime. Não alterou instalações reais.
- Chromium: QG padrão, detalhe com cinco abas, ordenação 1/9/2, HTML inerte, larguras 390/768/1440, scopes, arquivo portátil, HTTP/CORS, polling, preservação da última fotografia válida e falhas de host.
- Acrescentado teste específico de refresh do detalhe: feed novo preserva drawer aberto e aba Trabalho; conclusão da task 9 muda a próxima unidade para task 2. `node plugins/superflow/scripts/test_qg_detail.cjs`: exit 0 após essa edição. Os demais testes não foram repetidos porque a edição posterior foi restrita a esse teste e documentação.
- Helper Superpowers 6.4.2 `task-brief`: tasks 1 e 2 do PLAN real extraídas com sucesso; fixture com ordem 1/9/2 extraída e lida pelo parser. Ledger de fixture identificou próxima task 9. Arquivos temporários removidos.
- Self-review do delta: parser/identidade, recusas de paths/symlinks, seleção explícita entre formatos, fontes opt-in, fingerprint, retenção documental, apresentação inerte, refresh e distribuição. Nenhum defeito de runtime identificado nessa revisão.

## Limites e integração

A revisão foi inline; não houve dispatch de subagents, execução SDD ou ledger nativo desta implementação. Foi removida do status a referência a `execution/progress.md`, que não existia. Os testes de ledger usam fixtures e não comprovam execução de agentes. Não houve aceite visual humano nem checks remotos automáticos.

Marco autorizou em 08/10/2026 validar, atualizar a PR #23 e integrar em main se ainda aberta. A candidata está validada para essa integração. Tag, release pública e instalação de consumidores são operações separadas e não foram executadas por esta validação. Este relato é evidência local do Superflow, não recibo de CI clínico.
