#!/usr/bin/env python3
"""
rota — desenha o plano antes de rodar, e a run depois.

  python3 rota.py desenhar plano.json                  → ASCII do plano + veredito das leis
  python3 rota.py conferir  wf_<runId>.json [plano.json] → ASCII da run + comparação

Sai 1 quando reprova. O desenho não se escreve à mão: é preenchimento de modelo.
Bordas, colunas e alinhamento saem daqui, e as leis são verificadas no mesmo
passo — regra que vive só em prosa não segura nada.
"""
import json, sys, re

W, M, TETO = 96, 92, 15
PAPEIS      = {"reader", "writer", "fixer", "integrador"}
MODELOS     = {"sonnet", "opus"}
EFFORTS     = {"low", "medium", "high", "xhigh", "max"}
PADROES     = {"parallel", "pipeline", "serial"}
SIMB        = {"parallel": "‖", "pipeline": "→", "serial": "·"}
NADA        = {"—", "-", "", None}
MAX_ESCRITORES = 3          # lei L4: numa superfície coesa, no máximo 3 escrevem

def vazio(v): return (v.strip() if isinstance(v, str) else v) in NADA

def papel(a):
    """`papel` é o nome canônico; `agentType` é aceito porque foi assim que nasceu."""
    return a.get("papel") or a.get("agentType")

# ── moldura ────────────────────────────────────────────────────────────────
def dupla(pares):
    o = ["╔" + "═"*(W-2) + "╗"]
    for e, d in pares:
        o.append("║ " + (e + " "*max(1, M-len(e)-len(d)) + d if d else e.ljust(M)) + " ║")
    return o + ["╚" + "═"*(W-2) + "╝"]

def abre(titulo, direita):
    ini, fim = f"┌─ {titulo} ", f" {direita} ─┐"
    return ini + "─"*max(1, W - len(ini) - len(fim)) + fim

def fecha():     return "└" + "─"*(W-2) + "┘"
def linha(t=""): return "│ " + corta(t, M).ljust(M) + " │"
def corta(t, n): return t if len(t) <= n else t[:max(0, n-1)] + "…"

def quebra(rot, txt, larg):
    """Rótulo + texto quebrado na largura, sem estourar a moldura."""
    saida, prim, buf = [], True, ""
    for pal in str(txt).split():
        while len(pal) > larg:                       # palavra maior que a coluna
            saida.append((rot if prim else "", pal[:larg-1] + "-")); prim, pal = False, pal[larg-1:]
        if len(buf) + len(pal) + 1 > larg:
            saida.append((rot if prim else "", buf)); prim, buf = False, pal
        else:
            buf = f"{buf} {pal}".strip()
    if buf or not saida: saida.append((rot if prim else "", buf))
    return saida

COLS = [20, 12, 7, 7, 13, 28]          # agente · tipo · modelo · effort · schema · escreve
assert 5 + sum(COLS) <= M, 'colunas estouram a moldura'   # 5 = prefixo '   ├ '
def fila(marca, campos):
    return linha(f"   {marca} " + "".join(corta(str(c), l-1).ljust(l) for c, l in zip(campos, COLS)))
def cabcol(nomes):
    return linha("     " + "".join(n.ljust(l) for n, l in zip(nomes, COLS)))

def destino(a):
    """Coluna 'escreve': o artefato corrigido, e o julgamento versionado ao lado."""
    c, r = a.get("corrige", "—"), a.get("registra", "—")
    if vazio(c) and vazio(r): return "—"
    if vazio(r): return c
    if vazio(c): return r
    return f"{c} +{r}"

def nome_schema(s):
    if isinstance(s, dict): return s.get("nome", "?")
    return "—" if vazio(s) else str(s)

# ── leis ───────────────────────────────────────────────────────────────────
def leis(plano):
    falhas, avisos = [], []
    for i, run in enumerate(plano.get("runs", [])):
        rn    = run.get("nome", f"RUN {i+1}")
        fases = run.get("fases", [])
        ags   = [a for f in fases for a in f.get("agentes", [])]
        mult  = run.get("multiplicador", 1)
        pior  = run.get("piorCaso", len(ags) * mult)

        if pior != len(ags) * mult:
            avisos.append(f"{rn}: piorCaso {pior} ≠ {len(ags)} agentes × {mult} rodadas")
        if pior > TETO and not run.get("justificativaTeto"):
            falhas.append(f"{rn}: pior caso {pior} acima de {TETO} sem 'justificativaTeto'. "
                          f"O número não é proibido — a frase que o explica é obrigatória (L1)")
        elif pior > TETO:
            avisos.append(f"{rn}: pior caso {pior} acima de {TETO} — justificado: "
                          f"{run['justificativaTeto']}")
        if mult > 1:
            for k in ("condicaoParada", "maxRounds", "memoria"):
                if not run.get(k): falhas.append(f"{rn}: loop sem '{k}' declarado (L2)")
        for k, rot in (("porque","POR QUÊ"), ("extrai","EXTRAI"), ("dod","DoD")):
            if not run.get(k): falhas.append(f"{rn}: falta {rot}")
        if not run.get("retorno"): falhas.append(f"{rn}: sem schema de return (L6)")
        ultimo = (i == len(plano["runs"]) - 1)
        if not ultimo and not run.get("ponte"):
            falhas.append(f"{rn}: sem ponte para o run seguinte (§4)")
        if run.get("ponte") and not run.get("suficiencia"):
            falhas.append(f"{rn}: ponte sem critério de suficiência — o run seguinte "
                          f"não fica determinável (§4)")

        tem_integrador_depois = [
            any(papel(a) == "integrador" for f2 in fases[j+1:] for a in f2.get("agentes", []))
            for j in range(len(fases))]

        for j, f in enumerate(fases):
            fn = f.get("nome", f"FASE {j+1}")
            if f.get("padrao") not in PADROES:
                falhas.append(f"{rn}/{fn}: padrão '{f.get('padrao')}' fora de {sorted(PADROES)}")
            membros = f.get("agentes", [])
            for a in membros:
                an = a.get("nome", "?")
                for k, universo in (("papel", PAPEIS), ("modelo", MODELOS), ("effort", EFFORTS)):
                    v = papel(a) if k == "papel" else a.get(k)
                    if not v:            falhas.append(f"{rn}/{an}: '{k}' não declarado")
                    elif v not in universo: falhas.append(f"{rn}/{an}: {k}='{v}' fora de {sorted(universo)}")
                # schema: nome sozinho não é contrato — precisa dos campos, ou de justificativa
                s = a.get("schema")
                if isinstance(s, dict):
                    if not s.get("nome") or not s.get("campos"):
                        falhas.append(f"{rn}/{an}: schema sem 'nome' ou sem 'campos'")
                elif vazio(s):
                    if not a.get("semSchemaPorque"):
                        falhas.append(f"{rn}/{an}: sem schema e sem 'semSchemaPorque' — quem "
                                      f"consome vai ler prosa (Free-Text Parsing)")
                else:
                    falhas.append(f"{rn}/{an}: schema é só o nome '{s}'; declare "
                                  f"{{'nome':…, 'campos':[…]}} com os campos escritos")
                # papéis: quem corrige precisa de destino; quem só lê não corrige
                tipo, corrige, registra = papel(a), a.get("corrige"), a.get("registra")
                if tipo == "fixer":
                    if a.get("somenteLeitura"):
                        if vazio(registra):
                            falhas.append(f"{rn}/{an}: fixer somente-leitura sem 'registra' — "
                                          f"o achado não sobrevive ao run (L7)")
                    elif vazio(corrige):
                        falhas.append(f"{rn}/{an}: fixer sem 'corrige' — revisor que só aponta "
                                      f"custa outra volta inteira (L3). Se a revisão é somente "
                                      f"leitura, declare 'somenteLeitura': true")
                    elif vazio(registra):
                        avisos.append(f"{rn}/{an}: fixer corrige mas não registra o julgamento "
                                      f"em arquivo versionado (L7)")
                if tipo == "reader" and not vazio(corrige):
                    falhas.append(f"{rn}/{an}: reader com 'corrige' — quem levanta não altera "
                                  f"o objeto investigado")

            # L4 — escritores por fase, contados por destino real
            escritores = [a for a in membros if not vazio(a.get("corrige"))]
            distintos  = {a.get("corrige") for a in escritores}
            if len(distintos) > MAX_ESCRITORES and not run.get("excecaoMecanica"):
                falhas.append(f"{rn}/{fn}: {len(distintos)} destinos escritos por agentes "
                              f"diferentes na mesma fase (máximo {MAX_ESCRITORES}). Quem escreve "
                              f"coisas que se referenciam tem que ser o mesmo agente (L4); se o "
                              f"trabalho é mecânico sobre padrão pronto, declare 'excecaoMecanica'")
            # dois no mesmo destino: ou isolam e integram, ou viram um
            por_destino = {}
            if f.get("padrao") != "serial":   # em serial não há colisão: um escreve depois do outro
                for a in escritores: por_destino.setdefault(a["corrige"], []).append(a)
            for dest, quem in por_destino.items():
                if len(quem) < 2: continue
                if not all(x.get("isolamento") for x in quem):
                    falhas.append(f"{rn}/{fn}: {len(quem)} agentes escrevem '{dest}' sem "
                                  f"isolamento (L4)")
                elif not tem_integrador_depois[j]:
                    falhas.append(f"{rn}/{fn}: {len(quem)} agentes escrevem '{dest}' em worktrees "
                                  f"isoladas e nenhuma fase posterior integra — worktree não "
                                  f"herda worktree, o trabalho de um deles se perde (L4/L6)")
    return falhas, avisos

# ── desenho do plano ───────────────────────────────────────────────────────
def desenhar(plano):
    falhas, avisos = leis(plano)
    runs  = plano.get("runs", [])
    total = sum(r.get("piorCaso", sum(len(f.get("agentes", [])) for f in r.get("fases", []))
                                   * r.get("multiplicador", 1)) for r in runs)
    o = dupla([(f"PLANO · {plano.get('nome','?')}", "REPROVA" if falhas else "para aprovação"),
               (f"intenção   {plano.get('intencao','—')}", ""),
               (f"forma      {len(runs)} run(s) · máximo {total} agentes · teto {TETO} por run", "")])
    if len(runs) > 1:
        P = len("RUN 1") + len(" ──■──► ")
        o += ["", "   " + " ──■──► ".join(f"RUN {i+1}" for i in range(len(runs)))
              + "     ■ = ponte: o Marco lê,",
              "   " + "".join(r.get("verbo","·").ljust(P) for r in runs).rstrip()
              .ljust(len(runs)*P) + "  ajusta e libera", ""]
    for i, r in enumerate(runs):
        pior = r.get("piorCaso", sum(len(f.get("agentes", [])) for f in r.get("fases", []))
                                  * r.get("multiplicador", 1))
        if i: o += [""]
        o += dupla([(f"RUN {i+1} · {r.get('nome','?')}", f"máximo {pior} agentes")])[:-1]
        o += ["║ " + " "*M + " ║"]
        for k, rot in (("porque","POR QUÊ"), ("extrai","EXTRAI"), ("dod","DoD")):
            for ro, tx in quebra(rot, r.get(k, "—"), M - 11):
                o.append("║ " + f"{ro:<11}{tx}".ljust(M) + " ║")
        o += ["╚" + "═"*(W-2) + "╝"]
        for f in r.get("fases", []):
            p, membros = f.get("padrao", "serial"), f.get("agentes", [])
            nota = f"{SIMB.get(p,'?')} {p.upper()}"
            if p == "parallel": nota += f" · espera {len(membros)}"
            if r.get("multiplicador", 1) > 1: nota += f" · × {r['multiplicador']}"
            o += [abre(f"FASE · {f.get('nome','?')}", nota),
                  cabcol(["agente","papel","modelo","effort","schema","escreve"]), linha()]
            for j, a in enumerate(membros):
                o += [fila("└" if j == len(membros)-1 else "├",
                           [a.get("nome","?"), papel(a) or "?", a.get("modelo","?"),
                            a.get("effort","?"), nome_schema(a.get("schema")), destino(a)])]
            o += [linha(), fecha()]
        rot = "PONTE" if r.get("ponte") else "FIM"
        o += ["", f"■ {rot:<9} return {r.get('retorno','—')}"]
        for k in ("ponte", "suficiencia"):
            if r.get(k):
                pre = "" if k == "ponte" else "suficiência: "
                for _, tx in quebra("", pre + r[k], W - 12): o += [" "*12 + tx]
    if falhas or avisos:
        o += ["", "─"*W] + [f"  ✗ {x}" for x in falhas] + [f"  ⚠ {x}" for x in avisos]
    return "\n".join(o), falhas

# ── desenho da run ─────────────────────────────────────────────────────────
def h(n):   return "n/v" if n is None else (f"{n/1e6:.1f}M" if n >= 1e6 else (f"{n//1000}k" if n >= 1000 else str(n)))
def dur(ms):
    if ms is None: return "n/v"
    s = ms // 1000
    return f"{s//3600}h{(s%3600)//60:02d}m" if s >= 3600 else (f"{s//60}m{s%60:02d}s" if s >= 60 else f"{s}s")

def levas(ags):
    out = []
    for a in sorted(ags, key=lambda x: x.get("startedAt") or 0):
        ini = a.get("startedAt") or 0; fim = ini + (a.get("durationMs") or 0)
        if out and ini <= out[-1]["fim"]:
            out[-1]["ags"].append(a); out[-1]["fim"] = max(out[-1]["fim"], fim)
        else: out.append({"ags": [a], "ini": ini, "fim": fim})
    return out

def conferir(d, plano=None):
    wp    = d.get("workflowProgress", [])
    ags   = [x for x in wp if x.get("type") == "workflow_agent"]
    fases = [x for x in wp if x.get("type") == "workflow_phase"]
    m     = re.search(r"AGENTES:\s*(\d+)", d.get("script", "") or "")
    decl  = int(m.group(1)) if m else None
    real  = d.get("agentCount", len(ags))
    desvio = False
    if   decl is None: vd = "AGENTES não declarado no script"; desvio = True
    elif real <= decl: vd = f"máximo {decl} · realizado {real}  ✓ dentro"
    else:              vd = f"máximo {decl} · realizado {real}  ✗ {real-decl} a mais"; desvio = True

    o = dupla([(f"RUN · {d.get('workflowName','?')}", d.get("status","?")),
               (f"{real} chamadas agent()", vd),
               (f"{h(d.get('totalTokens'))} tokens · {d.get('totalToolCalls','n/v')} ferramentas",
                dur(d.get("durationMs")))])
    for f in fases:
        meus = [a for a in ags if a.get("phaseIndex") == f.get("index")]
        tk   = sum(a.get("tokens") or 0 for a in meus)
        span = (max((a.get("startedAt") or 0)+(a.get("durationMs") or 0) for a in meus)
                - min(a.get("startedAt") or 0 for a in meus)) if meus else 0
        o += ["", abre(f"FASE {f.get('index')} · {f.get('title','?')}",
                       f"{len(meus)} ag · {h(tk)} tok · {dur(span)}"),
              cabcol(["agente","estado","modelo","tokens","tempo","ferramentas"]), linha()]
        for g in levas(meus):
            n = len(g["ags"])
            o += [linha(f"  {'‖' if n>1 else '·'}  " + (f"BARREIRA · espera {n}" if n > 1 else "SERIAL"))]
            # Um agente, uma linha. Nunca resumir: agente escondido não é contado.
            for k, a in enumerate(g["ags"]):
                o += [fila("└" if k == n-1 else "├",
                           [a.get("label","?"), a.get("state","n/v"),
                            (a.get("model") or "n/v").replace("claude-","").replace("-5",""),
                            h(a.get("tokens")), dur(a.get("durationMs")),
                            a.get("toolCalls", "n/v")])]
            o += [linha()]
        o += [fecha()]

    modelos = {a.get("model") for a in ags}
    if d.get("defaultModel") and len(modelos) > 1:
        o += ["", f"  defaultModel do JSON é {d['defaultModel']}, mas rodaram "
              f"{sorted(str(x) for x in modelos)}.",
              "  defaultModel não prova o modelo de nenhuma chamada — confira agente a agente."]
    if plano:
        previstos = {a.get("nome") for r in plano.get("runs", [])
                     for f in r.get("fases", []) for a in f.get("agentes", [])}
        rotulos   = {re.split(r"[:·]", a.get("label",""))[0] for a in ags}
        fora = sorted(x for x in rotulos if x and not any(x in p or p in x for p in previstos))
        o += ["", "  Identidade das chamadas contra o plano:"]
        o += [f"    rótulos sem correspondência no plano: {', '.join(fora)}"] if fora else \
             ["    todos os rótulos correspondem a agentes do plano"]
        if fora: desvio = True
    else:
        o += ["", "  Plano não fornecido: a identidade das chamadas fica NÃO VERIFICADA.",
              "  Passe o plano.json como segundo argumento para comparar."]
    o += ["", "  Este JSON cobre esta run. Ele não prova que o chat deixou de usar Agent",
          "  tool por fora dela — confira a sessão ou declare o limite."]
    return "\n".join(o), desvio

if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    modo, alvo = sys.argv[1], sys.argv[2]
    if modo == "desenhar":
        txt, falhas = desenhar(json.load(open(alvo))); print(txt); sys.exit(1 if falhas else 0)
    if modo == "conferir":
        pl = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
        txt, desvio = conferir(json.load(open(alvo)), pl); print(txt); sys.exit(1 if desvio else 0)
    print(__doc__); sys.exit(2)
