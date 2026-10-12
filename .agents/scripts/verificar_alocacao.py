#!/usr/bin/env python3
"""Verifica a alocação tópico->bloco nas DUAS direções.

RESPONDE AO RECEIO: "a divisão de conteúdo não está bem feita e no fim muito
conteúdo ficou de fora".

Ele confere três coisas, e a terceira é a que pega o aperto no fim:
  1. COBERTURA  — canônico − alocado = vazio? (nenhum tópico deixado de fora)
  2. INVENÇÃO   — alocado − canônico = vazio? (nenhum tópico que não existe na fonte)
  3. RITMO      — min/tópico por bloco. Cobertura 100% com 10 min/tópico na véspera
                  é cobertura no papel e aperto na prática.

Uso: verificar_alocacao.py [alocacao.json] [conteudo-ancorado.json]
"""
import json
import re
import sys
import unicodedata

ALOC = sys.argv[1] if len(sys.argv) > 1 else \
    "/opt/data/workspace/academico/av1-online-2026-10/alocacao-topicos-blocos.json"
ANCORADO = sys.argv[2] if len(sys.argv) > 2 else \
    "/opt/data/workspace/academico/av1-online-2026-10/conteudo-ancorado-notebook.json"

CHAVE = {"PCP": "PCP",
         "Direitos Humanos": "Direitos",
         "Relações Étnico-Raciais": "Relações"}


def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).lower().strip()


def canonico(disciplina: str, dados: dict) -> list:
    """Extrai a lista canônica do conteúdo ancorado, com a UNIDADE na chave.

    A chave inclui a unidade porque a numeração de tópicos REINICIA a cada unidade:
    em PCP há três 'Tópico 1' (U1, U2, U3). Comparar só pelo número faz o verificador
    acusar tudo como duplicado — erro cometido na v1 deste script.
    """
    chave = next((k for k in dados if CHAVE[disciplina] in k), None)
    ans = dados[chave]["answer"] if chave else ""

    # DH usa `Tópico N.M` (sem unidade) — chave direta
    fmt_b = re.findall(r"\*\*T[óo]pico\s*(\d+\.\d+)\s*:?\*\*", ans)
    fmt_a = re.findall(r"\*\*T[óo]pico\s*(\d+)\s*\(p\.\s*(\d+)\)\s*:?\*\*", ans)
    if fmt_b and len(fmt_b) > len(fmt_a):
        return [f"T{n}" for n in fmt_b]

    # PCP/ETN: percorre o texto marcando a unidade corrente a cada cabeçalho
    itens, unidade = [], 0
    for m in re.finditer(r"UNIDADE\s*(\d)|\*\*T[óo]pico\s*(\d+)\s*\(p\.\s*(\d+)\)", ans, re.I):
        if m.group(1):
            unidade = int(m.group(1))
        else:
            itens.append((unidade, int(m.group(2)), m.group(3)))
    if not itens:  # fonte sem marcador de unidade (ETN): unidade única
        itens = [(1, int(n), p) for n, p in fmt_a]
    return [f"U{u}-T{n}" for u, n, _ in itens]


def chave_topico(disciplina: str, t: dict) -> str:
    """Converte o id da alocação para a MESMA forma canônica."""
    tid = t["id"]
    if disciplina == "Direitos Humanos":
        return f"T{tid[1:]}"
    m = re.match(r"(?:U(\d)-)?T?(\d+)$", tid.replace("ETN-", ""))
    if disciplina == "Relações Étnico-Raciais":
        return f"U1-T{tid.split('-')[-1][1:]}"
    if m:
        return f"U{m.group(1)}-T{m.group(2)}"
    return tid


def main() -> int:
    aloc = json.load(open(ALOC, encoding="utf-8"))
    dados = json.load(open(ANCORADO, encoding="utf-8"))
    problemas = []

    for disc, cfg in aloc["disciplinas"].items():
        can = canonico(disc, dados)
        n_can = len(can)
        alocados, ritmos = [], []
        for b in cfg["blocos"]:
            tops = b.get("topicos", [])
            if not tops:
                continue
            for t in tops:
                alocados.append(chave_topico(disc, t))
            ritmos.append((b["data"], b["min"], len(tops), b["min"] / len(tops)))

        print(f"\n### {disc}  (canônico: {n_can} tópicos, prova {cfg['prova']})")

        faltando = [c for c in can if c not in alocados]
        sobrando = [a for a in alocados if a not in can]
        dup = [a for a in set(alocados) if alocados.count(a) > 1]

        print(f"    alocados: {len(alocados)}  |  canônicos: {n_can}")
        if faltando:
            problemas.append(f"{disc}: {len(faltando)} tópico(s) FORA da alocação: {faltando}")
            print(f"    !! FICARAM DE FORA ({len(faltando)}): {faltando}")
        else:
            print("    cobertura: OK — nenhum canônico ficou de fora")
        if sobrando:
            problemas.append(f"{disc}: {len(sobrando)} alocado(s) que não existem na fonte: {sobrando}")
            print(f"    !! INVENTADOS: {sobrando}")
        if dup:
            problemas.append(f"{disc}: tópico alocado mais de uma vez: {dup}")
            print(f"    !! DUPLICADOS: {dup}")

        print(f"    ritmo por bloco:")
        for data, mins, n, r in ritmos:
            alerta = "  <<< APERTADO" if r < 15 else ""
            print(f"      {data}  {mins:>4} min / {n} tópicos = {r:5.1f} min/tópico{alerta}")

    print("\n" + "=" * 74)
    if problemas:
        print(f"VEREDITO: REPROVADO — {len(problemas)} problema(s)")
        for p in problemas:
            print("   -", p)
    else:
        print("VEREDITO: PASSOU — cobertura completa, sem invenção, sem duplicata")
        print("         (confira o RITMO acima: cobertura no papel com min/tópico baixo é aperto)")
    print("=" * 74)
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
