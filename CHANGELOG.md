# Changelog

## 0.12.3

- Include Chromium integration tests in local release validation, with repository-owned Playwright development setup.

## 0.12.2

- Clarify default local output paths and consumer-defined public feed URLs, with consistent feed/runtime examples.

## 0.12.1

- Report missing HTML publication destinations without blocking existing outputs or changing configuration.
- Report updated and missing destination counts, including when only feed/runtime were published.

## 0.12.0

- Portable snapshots and runtime in every generated QG, with optional HTTP refresh.
- Retain the latest valid view on network failure and preserve search/drawer state during updates.
- Optional refresh intervals and project-configured HTML publication destinations.

## 0.11.0

- Shared QG component with an HTTP feed and per-host ID selection.
- Feed publishes data and runtime; offline exports reuse the same component.
- Refresh multiple HTML components while preserving host content and scopes.

## 0.10.3

- Discover the same seven skills in Cursor through `.cursor-plugin` marketplace and plugin manifests.

## 0.10.2

- Report spec and status diagnostics as advisory output while preserving operational failure signaling.
- Allow independent spec creation with ID and destination collision protection.

## 0.10.1

- QG embutível com `qg --embed`: mesmo layout e dados do standalone, isolados por Shadow DOM, preservando a navegação do HTML hospedeiro.

## 0.10.0

- Require a human summary in status and new; project specs through feed v4.
- Preserve neutral relations with inverse navigation; keep task dependencies local to plans.
- Validate optional SPEC and plan independently with check spec.
- Show expanded minispec families, status dots and full narratives in the QG.
- Align skills and playbooks around conditional artifacts and canonical product ownership.
- Remove the personal installer and retired historical artifacts.

Breaking: existing status files need summary; replace spec dependencies with semantic relations and move active conditions into the narrative. The CLI no longer accepts check ready, proof_cmd or ship_cmd.

## 0.9.3 — 2026-09-14

- Impede o shell e as abas do QG de ampliarem a página em viewports estreitos.

## 0.9.2 — 2026-09-14

- Mantém as minispecs visíveis no acordeão quando a busca encontra a spec principal.

## 0.9.1 — 2026-09-14

- Corrige o upgrade de instalações antigas removendo os dois templates abolidos
  `analysis.md` e `technical_blueprint.md` antes de validar o staging.

## 0.9.0 — 2026-09-13

### Breaking changes

- Reduz o plugin a sete skills, cinco receitas, três contratos e quatro templates.
- Substitui o formato e os comandos anteriores por `new`, `check status`, `check ready`, `feed` e `qg`.
- Remove o runtime de campanha, WARLOG, roteamento por orçamento, plano executável e logs obrigatórios.
- Reduz `status.md` a estado binário e narrativa completa; o QG lê somente esse arquivo.
- Mostra specs e minispecs em famílias expansíveis e abre a narrativa em drawer.

### Distribution

- Adiciona `@superflow/runtime` privado para consumidores Node instalarem o runtime Python por Git pinado.
- O pacote não executa scripts de instalação e não migra repositórios consumidores automaticamente.
- Python 3.9 ou superior continua pré-requisito explícito para o runtime.

## Histórico

As versões até `0.8.0` permanecem disponíveis para consumidores que ainda usam o contrato anterior. Elas não descrevem a superfície do Superflow 0.9.0.
