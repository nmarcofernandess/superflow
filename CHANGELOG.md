# Changelog

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
