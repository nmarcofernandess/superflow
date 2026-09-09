#!/usr/bin/env python3
"""Behavioral tests for the Superflow `rota` contract (R1-R8).

A multi-agent plan that lives only in prose gets approved on vibes: the operator
sees a shape, not a count, and the bill arrives later. `rota` makes the plan a
file, draws it from that file, and checks the laws in the same pass. These tests
prove the validator has teeth — every mutant below is a plan that must be
refused, and every green case is a legitimate plan that must not be.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROTA = SCRIPT_DIR / "superflow_rota.py"
PLUGIN_ROOT = SCRIPT_DIR.parent
TEMPLATE = PLUGIN_ROOT / "assets" / "templates" / "plano.json"
FIXTURE = PLUGIN_ROOT / "assets" / "fixtures" / "rota" / "plano-valido.json"

AGENTE = {
    "nome": "a1", "papel": "reader", "modelo": "sonnet", "effort": "low",
    "schema": {"nome": "S", "campos": ["a", "b"]}, "corrige": "—", "registra": "—",
}
BASE = {
    "nome": "teste", "intencao": "provar as leis",
    "runs": [{
        "nome": "R1", "verbo": "fazer", "porque": "p", "extrai": "e", "dod": "d",
        "retorno": "{ x }",
        "fases": [{"nome": "F", "padrao": "serial", "agentes": [dict(AGENTE)]}],
    }],
}

falhas: list[str] = []


def desenhar(plano: dict) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(plano, fh, ensure_ascii=False)
        alvo = fh.name
    return subprocess.run([sys.executable, str(ROTA), "desenhar", alvo],
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def caso(lei: str, nome: str, esperado: str, muta=None) -> None:
    plano = copy.deepcopy(BASE)
    if muta:
        muta(plano)
    obtido = "ok" if desenhar(plano).returncode == 0 else "reprova"
    marca = "PASS" if obtido == esperado else "FAIL"
    if marca == "FAIL":
        falhas.append(f"{lei} {nome}: obteve {obtido}, esperava {esperado}")
    print(f"{marca} {lei} {nome}")


def agentes(plano: dict, *novos, padrao: str | None = None) -> None:
    fase = plano["runs"][0]["fases"][0]
    fase["agentes"] = list(novos)
    if padrao:
        fase["padrao"] = padrao


def main() -> int:
    # R1 — o pior caso é contado antes, e o número acima de 15 pede uma frase
    caso("R1a", "plano mínimo válido", "ok")
    caso("R1b", "16 agentes sem justificativa", "reprova",
         lambda p: agentes(p, *[dict(AGENTE, nome=f"a{i}") for i in range(16)]))
    caso("R1c", "16 agentes com justificativa escrita", "ok",
         lambda p: (p["runs"][0].update(justificativaTeto="censo mecânico em 16 pastas já nomeadas"),
                    agentes(p, *[dict(AGENTE, nome=f"a{i}") for i in range(16)]),
                    p["runs"][0].update(excecaoMecanica="mesma leitura em 16 alvos sem referência cruzada")))
    caso("R1d", "3 agentes x 6 rodadas = 18 sem justificativa", "reprova",
         lambda p: (p["runs"][0].update(multiplicador=6, condicaoParada="c", maxRounds=6, memoria="m"),
                    agentes(p, *[dict(AGENTE, nome=f"a{i}") for i in range(3)])))

    # R2 — loop declara parada, teto e memória do que já foi refutado
    caso("R2a", "loop sem condicaoParada", "reprova",
         lambda p: p["runs"][0].update(multiplicador=3, maxRounds=3, memoria="m"))
    caso("R2b", "loop sem maxRounds", "reprova",
         lambda p: p["runs"][0].update(multiplicador=3, condicaoParada="c", memoria="m"))
    caso("R2c", "loop sem memória do refutado", "reprova",
         lambda p: p["runs"][0].update(multiplicador=3, condicaoParada="c", maxRounds=3))
    caso("R2d", "loop completo", "ok",
         lambda p: p["runs"][0].update(multiplicador=3, condicaoParada="c", maxRounds=3, memoria="m"))

    # R3 — quem revisa corrige, onde a escrita está autorizada
    caso("R3a", "fixer sem corrige", "reprova",
         lambda p: agentes(p, dict(AGENTE, papel="fixer", corrige="—", registra="qa-v1.md")))
    caso("R3b", "fixer somente-leitura sem registra", "reprova",
         lambda p: agentes(p, dict(AGENTE, papel="fixer", somenteLeitura=True, corrige="—", registra="—")))
    caso("R3c", "fixer somente-leitura que registra", "ok",
         lambda p: agentes(p, dict(AGENTE, papel="fixer", somenteLeitura=True, corrige="—", registra="qa-v1.md")))
    caso("R3d", "fixer que corrige e registra", "ok",
         lambda p: agentes(p, dict(AGENTE, papel="fixer", corrige="x.ts", registra="qa-v1.md")))
    caso("R3e", "reader que corrige o objeto investigado", "reprova",
         lambda p: agentes(p, dict(AGENTE, corrige="x.ts")))
    caso("R3f", "corrige com espaços conta como vazio", "reprova",
         lambda p: agentes(p, dict(AGENTE, papel="fixer", corrige=" — ", registra="qa.md")))

    # R4 — um agente escreve tudo que se conecta
    caso("R4a", "4 destinos distintos sem exceção", "reprova",
         lambda p: agentes(p, *[dict(AGENTE, nome=f"w{i}", papel="writer", corrige=f"f{i}.ts")
                                for i in range(4)], padrao="parallel"))
    caso("R4b", "4 destinos distintos com excecaoMecanica", "ok",
         lambda p: (p["runs"][0].update(excecaoMecanica="mesma correção em 4 arquivos prontos"),
                    agentes(p, *[dict(AGENTE, nome=f"w{i}", papel="writer", corrige=f"f{i}.ts")
                                 for i in range(4)], padrao="parallel")))
    caso("R4c", "3 destinos distintos, no limite", "ok",
         lambda p: agentes(p, *[dict(AGENTE, nome=f"w{i}", papel="writer", corrige=f"f{i}.ts")
                                for i in range(3)], padrao="parallel"))
    caso("R4d", "2 no mesmo destino, em paralelo", "reprova",
         lambda p: agentes(p, *[dict(AGENTE, nome=f"w{i}", papel="writer", corrige="mesmo.ts")
                                for i in range(2)], padrao="parallel"))
    caso("R4e", "2 no mesmo destino, em serial", "ok",
         lambda p: agentes(p, *[dict(AGENTE, nome=f"w{i}", papel="writer", corrige="mesmo.ts")
                                for i in range(2)], padrao="serial"))
    caso("R4f", "2 isolados sem integrador depois", "reprova",
         lambda p: agentes(p, *[dict(AGENTE, nome=f"w{i}", papel="writer", corrige="mesmo.ts",
                                     isolamento="worktree") for i in range(2)], padrao="parallel"))
    caso("R4g", "2 isolados com integrador depois", "ok",
         lambda p: (agentes(p, *[dict(AGENTE, nome=f"w{i}", papel="writer", corrige="mesmo.ts",
                                      isolamento="worktree") for i in range(2)], padrao="parallel"),
                    p["runs"][0]["fases"].append(
                        {"nome": "I", "padrao": "serial",
                         "agentes": [dict(AGENTE, nome="int", papel="integrador", corrige="R.md")]})))
    caso("R4h", "agentes read-only não contam como escrita", "ok",
         lambda p: agentes(p, *[dict(AGENTE, nome=f"r{i}") for i in range(5)], padrao="parallel"))

    # R5 — contrato de saída: schema com campos, ou o motivo de não ter
    caso("R5a", "schema só com o nome", "reprova",
         lambda p: agentes(p, dict(AGENTE, schema="SAIDA")))
    caso("R5b", "schema objeto sem campos", "reprova",
         lambda p: agentes(p, dict(AGENTE, schema={"nome": "SAIDA"})))
    caso("R5c", "sem schema e sem justificativa", "reprova",
         lambda p: agentes(p, dict(AGENTE, schema="—")))
    caso("R5d", "sem schema com semSchemaPorque", "ok",
         lambda p: agentes(p, dict(AGENTE, schema="—",
                                   semSchemaPorque="o produto é o arquivo no disco")))

    # R6 — todo run diz por que existe, o que extrai e quando terminou
    for campo, rotulo in (("porque", "POR QUÊ"), ("extrai", "EXTRAI"), ("dod", "DoD"),
                          ("retorno", "return")):
        caso("R6", f"run sem {rotulo}", "reprova",
             lambda p, c=campo: p["runs"][0].update({c: ""}))

    # R7 — a ponte carrega o critério que torna o run seguinte desenhável
    def dois_runs(p, **extra):
        segundo = copy.deepcopy(p["runs"][0])
        segundo["nome"] = "R2"
        p["runs"][0].update(extra)
        p["runs"].append(segundo)

    caso("R7a", "primeiro de dois runs sem ponte", "reprova", dois_runs)
    caso("R7b", "ponte sem critério de suficiência", "reprova",
         lambda p: dois_runs(p, ponte="o operador decide"))
    caso("R7c", "ponte com suficiência", "ok",
         lambda p: dois_runs(p, ponte="o operador decide", suficiencia="lista fechada"))

    # R8 — vocabulário fechado e bordas que não podem estourar
    caso("R8a", "modelo não declarado", "reprova",
         lambda p: agentes(p, dict(AGENTE, modelo="")))
    caso("R8b", "effort não declarado", "reprova",
         lambda p: agentes(p, {k: v for k, v in AGENTE.items() if k != "effort"}))
    caso("R8c", "effort 'max' é válido", "ok",
         lambda p: agentes(p, dict(AGENTE, effort="max")))
    caso("R8d", "papel fora do vocabulário", "reprova",
         lambda p: agentes(p, dict(AGENTE, papel="juiz")))
    caso("R8e", "padrão fora do vocabulário", "reprova",
         lambda p: p["runs"][0]["fases"][0].update(padrao="fanout"))
    caso("R8f", "agente sem nome reprova em vez de estourar", "reprova",
         lambda p: agentes(p, {k: v for k, v in dict(AGENTE, modelo="haiku").items() if k != "nome"}))
    caso("R8g", "agentType ainda é aceito como sinônimo de papel", "ok",
         lambda p: agentes(p, {("agentType" if k == "papel" else k): v for k, v in AGENTE.items()}))

    # O exemplo que a skill manda copiar tem de passar, desenhar dentro da moldura,
    # e não pode esconder agente nenhum atrás de um resumo.
    for alvo, rotulo in ((TEMPLATE, "assets/templates/plano.json"),
                         (FIXTURE, "assets/fixtures/rota/plano-valido.json")):
        r = subprocess.run([sys.executable, str(ROTA), "desenhar", str(alvo)],
                           text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ok = r.returncode == 0
        print(f"{'PASS' if ok else 'FAIL'} R9a {rotulo} desenha sem reprovar")
        if not ok:
            falhas.append(f"R9a {rotulo}: {r.stdout[-300:]}")
            continue
        molde = [l for l in r.stdout.splitlines() if l and l[0] in "║│╔╚┌└"]
        fora = [l for l in molde if len(l) != 96]
        print(f"{'PASS' if not fora else 'FAIL'} R9b {rotulo} moldura de 96 colunas")
        if fora:
            falhas.append(f"R9b {rotulo}: {len(fora)} linha(s) fora da moldura")
        resumido = "mais" in r.stdout and "iguais" in r.stdout
        print(f"{'PASS' if not resumido else 'FAIL'} R9c {rotulo} nenhum agente resumido")
        if resumido:
            falhas.append(f"R9c {rotulo}: desenho esconde agente")

    # R11 — `conferir` é veredito, não relatório. O plano aprovado é a autoridade;
    # o `// AGENTES:` do script é declaração de quem escreveu o script, e o script
    # é justamente o que pode ter mudado. Cada caso abaixo foi um falso aceite real.
    def agente_run(nome, modelo="sonnet", fase=1, i=0):
        return {"type": "workflow_agent", "index": i + 1, "label": nome, "phaseIndex": fase,
                "model": f"claude-{modelo}-5", "state": "done", "startedAt": i * 20,
                "durationMs": 10, "tokens": 100, "toolCalls": 1}

    PLANO_AB = {
        "nome": "Reconhecer", "intencao": "Ler A e B",
        "runs": [{
            "nome": "Reconhecimento", "verbo": "reconhecer", "porque": "dimensionar",
            "extrai": "dois inventários", "dod": "inventário de A e B",
            "retorno": "{ inventarios[] }",
            "fases": [{"nome": "Ler", "padrao": "parallel", "agentes": [
                dict(AGENTE, nome=n, registra=f"{n.replace(':', '-')}.md")
                for n in ("ler:A", "ler:B")]}],
        }],
    }

    def conferir(run: dict, plano: dict | None) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as tmp:
            rj = Path(tmp) / "wf.json"
            rj.write_text(json.dumps(run, ensure_ascii=False))
            args = [sys.executable, str(ROTA), "conferir", str(rj)]
            if plano is not None:
                pj = Path(tmp) / "plano.json"
                pj.write_text(json.dumps(plano, ensure_ascii=False))
                args.append(str(pj))
            return subprocess.run(args, text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)

    def run_base(**over) -> dict:
        r = {"runId": "wf_t", "workflowName": "Reconhecimento", "status": "completed",
             "agentCount": 2, "script": "// AGENTES: 2\n", "totalTokens": 200,
             "totalToolCalls": 2, "durationMs": 20, "defaultModel": "sonnet",
             "workflowProgress": [{"type": "workflow_phase", "index": 1, "title": "Ler"},
                                  agente_run("ler:A", i=0), agente_run("ler:B", i=1)]}
        r.update(over)
        return r

    def caso_conf(lei, nome, esperado, run, plano=PLANO_AB, precisa=None):
        r = conferir(run, plano)
        obtido = "ok" if r.returncode == 0 else "desvio"
        bem = obtido == esperado and (precisa is None or precisa in r.stdout)
        print(f"{'PASS' if bem else 'FAIL'} {lei} {nome}")
        if not bem:
            falhas.append(f"{lei} {nome}: obteve {obtido}, esperava {esperado}"
                          + (f" (faltou {precisa!r})" if precisa and precisa not in r.stdout else ""))

    caso_conf("R11a", "run fiel ao plano", "ok", run_base())
    caso_conf("R11b", "modelo trocado por opus", "desvio",
              run_base(workflowProgress=[{"type": "workflow_phase", "index": 1, "title": "Ler"},
                                         agente_run("ler:A", "opus", i=0),
                                         agente_run("ler:B", "opus", i=1)]),
              precisa="o plano aprovou sonnet")
    caso_conf("R11c", "alvo trocado por um não aprovado", "desvio",
              run_base(workflowProgress=[{"type": "workflow_phase", "index": 1, "title": "Ler"},
                                         agente_run("ler:ALVO-NAO-APROVADO", i=0),
                                         agente_run("ler:B", i=1)]),
              precisa="não corresponde a agente nenhum do plano")
    caso_conf("R11d", "agente previsto omitido, sem parada antecipada", "desvio",
              run_base(agentCount=1,
                       workflowProgress=[{"type": "workflow_phase", "index": 1, "title": "Ler"},
                                         agente_run("ler:A", i=0)]),
              precisa="não aparece na run")
    plano_para = copy.deepcopy(PLANO_AB)
    plano_para["runs"][0].update(multiplicador=2, condicaoParada="quando A bastar",
                                 maxRounds=2, memoria="alvos já lidos", piorCaso=4)
    # o cabeçalho carrega o PIOR caso (4), e a run parou em 1 porque a condição bateu
    caso_conf("R11e", "agente omitido COM parada antecipada declarada", "ok",
              run_base(agentCount=1, script="// AGENTES: 4\n",
                       workflowProgress=[{"type": "workflow_phase", "index": 1, "title": "Ler"},
                                         agente_run("ler:A", i=0)]),
              plano=plano_para)
    caso_conf("R11f", "script declara mais agentes que o plano", "desvio",
              run_base(agentCount=3, script="// AGENTES: 3\n",
                       workflowProgress=[{"type": "workflow_phase", "index": 1, "title": "Ler"},
                                         agente_run("ler:A", i=0), agente_run("ler:B", i=1),
                                         agente_run("ler:C", i=2)]),
              precisa="o plano aprovado soma 2")
    caso_conf("R11g", "fase trocada", "desvio",
              run_base(workflowProgress=[{"type": "workflow_phase", "index": 1, "title": "Outra"},
                                         agente_run("ler:A", i=0), agente_run("ler:B", i=1)]),
              precisa="o plano o pôs em")
    caso_conf("R11h", "modelo ausente no registro fica não verificado", "desvio",
              run_base(workflowProgress=[{"type": "workflow_phase", "index": 1, "title": "Ler"},
                                         {**agente_run("ler:A", i=0), "model": None},
                                         agente_run("ler:B", i=1)]),
              precisa="NÃO VERIFICADO")
    caso_conf("R11i", "sem plano, nada é verificado", "desvio", run_base(), plano=None,
              precisa="NÃO VERIFICADO")

    # R12 — o desenho da run não pode afirmar barreira a partir do relógio
    r = conferir(run_base(), PLANO_AB)
    sem_barreira = "BARREIRA" not in r.stdout
    print(f"{'PASS' if sem_barreira else 'FAIL'} R12a desenho não afirma barreira por horário")
    if not sem_barreira:
        falhas.append("R12a: o desenho chamou de barreira o que só é simultaneidade observada")
    encostado = run_base(workflowProgress=[
        {"type": "workflow_phase", "index": 1, "title": "Ler"},
        {**agente_run("ler:A", i=0), "startedAt": 0, "durationMs": 10},
        {**agente_run("ler:B", i=1), "startedAt": 10, "durationMs": 10}])
    saida = conferir(encostado, PLANO_AB).stdout
    seq = saida.count("SERIAL") == 2
    print(f"{'PASS' if seq else 'FAIL'} R12b terminar quando o outro começa é sequência")
    if not seq:
        falhas.append("R12b: janelas que só se encostam foram agrupadas como simultâneas")

    if falhas:
        print()
        for f in falhas:
            print(f"  FALHOU: {f}")
        return 1
    print("OK: superflow rota contract tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
