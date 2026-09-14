---
name: superflow
description: Roteia trabalho por uma spec mínima, escolhendo capacidades e playbooks conforme os contratos existentes, sem máquina persistida de fases.
---

# Superflow

Use para registrar, preparar, retomar, reconciliar ou fechar uma entrega.

## Leitura inicial

1. Localize a spec e leia `status.md` primeiro.
2. Escolha a intenção: capturar, preparar/executar, retomar, reconciliar ou fechar.
3. Abra somente os contratos necessários à ação escolhida.

## Regras

- Ideia nova: `PRD.md` e `status.md`.
- Antes da primeira implementação aceita: `SPEC.md` e `plan.json` também existem e passam em `superflow check ready <spec>`.
- Estado global e estado de task usam apenas `pending | done`.
- Analyst, Build, Plan, Execute, Review e QA são capacidades ou ações; nunca grave uma fase.
- Atualize PRD quando mudar produto; SPEC quando mudar arquitetura; plano quando mudar execução; status quando mudar o retrato ou houver handoff relevante.
- O projeto consumidor continua dono de teste, prova, CI e ship.

## Playbooks

Leia somente a receita escolhida em `../../assets/playbooks/`: `capture`, `feature`, `retomar`, `fechar` ou `reconciliar`.

Os comandos `new`, `feed`, `qg` e `check` são determinísticos e não autorizam ações externas.
