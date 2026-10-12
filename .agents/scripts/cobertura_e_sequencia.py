#!/usr/bin/env python3
"""C4 — Cobertura e sequência (derivada).  v2 — extrator corrigido.

A v1 casava UM formato só (`**Tópico N:**`) e por isso mentiu:
  - PCP:  achou 12 de 14 — a numeração REINICIA a cada unidade (4+4+6)
  - DH:   achou 18 por acidente (casou sub-itens); o formato real é `Tópico N.M`
  - ETN:  3, correto (usa o mesmo formato do PCP)

v2 casa os DOIS formatos reais e AUTO-VALIDA contra a contagem esperada.
Um extrator que não se testa é um extrator que mente — e um portão que só
diz "sim" não é portão, é enfeite.

Nada é escrito: é leitura pura do estado que já existe.
"""
import json
import re
import sys

AGENDA = sys.argv[1] if len(sys.argv) > 1 else \
    "/opt/data/cache/scratch/repos/planos-estudos-engenharia/agenda_semestre.json"
ANCORADO = "/opt/data/workspace/academico/av1-online-2026-10/conteudo-ancorado-notebook.json"

PROVA = {"Planejamento e Controle da Produção (PCP)": "2026-10-21",
         "Direitos Humanos, Cidadania e Inclusão": "2026-10-20",
         "Relações Étnico-Raciais e Diferentes Culturas": "2026-10-20"}

# Minutos alocados por disciplina (blocos na agenda, 11/10/2026)
# DH: 120 (qua 80 + dom 40) + 60 (qua) + 60 (sex) = 240  <- decisão do grill
BLOCOS = {"Planejamento e Controle da Produção (PCP)": 1000,
          "Direitos Humanos, Cidadania e Inclusão": 240,
          "Relações Étnico-Raciais e Diferentes Culturas": 60}

ESPERADO = {"Planejamento e Controle da Produção (PCP)": 14,
            "Direitos Humanos, Cidadania e Inclusão": 18,
            "Relações Étnico-Raciais e Diferentes Culturas": 3}


def extrair(ans):
    """Casa os DOIS formatos reais. Devolve (topicos, formato)."""
    fmt_a = re.findall(r"\*\*T[óo]pico\s*(\d+)\s*\(p\.\s*(\d+)\)\s*:?\*\*", ans)
    fmt_b = re.findall(r"\*\*T[óo]pico\s*(\d+\.\d+)\s*:?\*\*", ans)
    if fmt_b and len(fmt_b) > len(fmt_a):
        return [f"Tópico {n}" for n in fmt_b], "Tópico N.M (apostila por tema)"
    return [f"Tópico {n} (p. {p})" for n, p in fmt_a], "Tópico N (p. X) — reinicia por unidade"


def main():
    dados = json.load(open(ANCORADO, encoding="utf-8"))
    agenda = json.load(open(AGENDA, encoding="utf-8"))
    sessoes = agenda["sessions"]

    print("=" * 78)
    print("C4 v2 — COBERTURA E SEQUÊNCIA  (extrator corrigido, 11/10/2026)")
    print("=" * 78)

    falhas = []
    for disc, prova in PROVA.items():
        chave = next((k for k in dados if k.split(",")[0][:20] in disc or disc[:20] in k), None)
        ans = dados[chave]["answer"] if chave else ""
        tops, fmt = extrair(ans)
        minutos = BLOCOS.get(disc, 0)
        esp = ESPERADO.get(disc)

        cobertos = [s["current_content"] for s in sessoes
                    if s.get("discipline") == disc
                    and s.get("current_content") not in (None, "None")]

        print(f"\n### {disc}")
        print(f"    prova {prova} | formato: {fmt}")
        print(f"    tópicos: {len(tops)} (esperado {esp}) | minutos: {minutos}")
        if tops:
            r = minutos / len(tops)
            print(f"    ritmo: {r:.1f} min/tópico   {'OK' if r >= 10 else 'APERTADO'}")
        if len(tops) != esp:
            falhas.append(f"{disc}: {len(tops)} tópicos, esperado {esp}")
        print(f"    cobertos no repo: {len(cobertos)} -> "
              f"veredito FAIL-COBERTURA {len(cobertos)}/{len(tops)} (linha de base)")

    print("\n" + "=" * 78)
    print(f"AUTO-VALIDAÇÃO DO EXTRATOR: {'PASSOU' if not falhas else 'FALHOU'}")
    for f in falhas:
        print("   !", f)
    print("=" * 78)

    # auto-teste negativo: o portão PRECISA reprovar quando o texto quebra
    dh = next(v["answer"] for k, v in dados.items() if "Direitos" in k)
    quebrado = dh.replace("**Tópico 5.10", "**Topico 5.10")
    t_q, _ = extrair(quebrado)
    detectou = len(t_q) < 18
    print(f"AUTO-TESTE NEGATIVO (quebrei 'Tópico 5.10' de propósito): 18 -> {len(t_q)}"
          f"  {'OK — o portão detecta a perda' if detectou else 'FALHOU — passaria batido'}")
    return 0 if (not falhas and detectou) else 1


if __name__ == "__main__":
    sys.exit(main())
