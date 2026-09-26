# Mapa por escopo e orquestração

## Duas identidades, uma casa

A spec tem promessa, estado `pending | done`, narrativa e plano quando necessário.
Um encaminhamento tem destinatário, próxima ação e situação de envio/revisão.
Concluir uma preparação não conclui a spec. A skill `orquestrar` cuida desse
segundo objeto, consulta as fontes e oferece prompts. Não é scheduler e não
acrescenta status de execução à spec.

O QG apresenta specs a partir do feed oficial. A mesa de encaminhamentos pode
reunir links de vários projetos, sem fingir um feed agregado ou duplicar tasks.
O painel existente deve ser preservado; o asset é só ponto de partida para uma
mesa nova. Conteúdo atualizado por outro owner não é substituído por um exemplo.

## Mapa opt-in

    python3 -I <plugin>/scripts/superflow.py --root <projeto> qg --scope .superflow/scopes/entrega.json --output mapa.html

O mapa usa o renderer e o drawer do QG. Sem `--scope`, a lista permanece igual.
Um escopo é relativo à raiz do projeto, sem symlinks ou `..`. Só ele é lido;
nenhum scan de scopes ou planos. `--embed` e `--online` continuam disponíveis.
`--scope` não combina com `--refresh`; o refresh relê o `scope-path` guardado em
cada componente selecionado. `ids` e composição não podem coexistir.

```json
{
  "schema_version": "superflow.scope.v1",
  "id": "entrega",
  "title": "Uma entrega",
  "goal": "Conectar duas contribuições",
  "groups": [{"id": "core", "title": "Core"}],
  "members": [
    {"spec_id": "writer", "group": "core", "focus": "Confirmação da gravação"},
    {"spec_id": "editor", "group": "core", "focus": "Sessão que consome a confirmação"}
  ],
  "edges": [{"from": "writer", "to": "editor", "kind": "after", "reason": "A integração consome o contrato de confirmação."}]
}
```

`schema_version`, `id`, `title`, `goal` e `members` são obrigatórios. `groups` e
`edges` são opcionais. IDs são opacos. Campos desconhecidos, duplicatas e tipos
errados são recusados. Membros aceitam `spec_id`, `group` e `focus`; não armazenam
estado. O cartão informa o estado da spec inteira, mesmo quando focus descreve
uma contribuição parcial.

Arestas: `after` ordena contribuições; `context` relaciona; `evidence` aponta
uma evidência. Só `after` participa da sequência. Relações dos status entram como
contexto, com motivos e origem preservados. Uma relação externa é indicada no
detalhe sem ampliar o recorte. Grupo visual não significa fase de execução.
Mesma etapa não garante recurso, independência de arquivos ou autorização.

Fonte ausente/ambígua mantém o membro visível. Se participa de uma precedência,
a sequência fica indisponível. Ciclo contextual é válido; ciclo de precedência
impede apresentar uma ordem parcial como se fosse completa. Conjunto e foco têm
lista textual equivalente; Escape, segundo clique ou Mostrar tudo restauram o mapa.

## Publicação e atualização

O HTML incorpora snapshot e composição como JSON inerte. O navegador não busca
arquivos locais de scope. A chave de render inclui feed e composição; polling
HTTP continua opcional e preserva a última fotografia válida em falhas de rede.

Refresh prepara todas as saídas selecionadas antes de escrever, relê somente seus
scopes e protege essas fontes contra sobrescrita/mudança durante publicação.
Arquivo de escopo inválido é erro operacional; faltas de cadastro e ciclos são
diagnósticos visíveis. Atomicidade é por arquivo; não existe transação de lote.
Não há edição visual, persistência browser, agendamento ou concessão de aceite.

## Mesa existente e multiprojeto

O mapa v1 contém specs de um projeto. A mesa humana pode incorporar vários QGs,
cada qual com feed/escopo explícitos, e seus encaminhamentos com links canônicos.
Não há ordenação automática entre repositórios. Não criar specs artificiais para
registrar um envio, nem forçar migração de um painel manual já funcional.
