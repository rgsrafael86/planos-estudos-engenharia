#!/usr/bin/env python3
"""Verifica se os termos das questoes do plano estao na APOSTILA (fonte real)
ou se o agy completou com conhecimento geral.

Compara tres colunas: apostila (254 p.) x brief dado ao agy x o plano gerado.
"""
import re
import sys

import pypdfium2 as pdfium

PDF = "/opt/data/cache/scratch/apostilas/pcp.pdf"
BRIEF = "/opt/data/cache/scratch/brief_pcp_20261012.txt"

TERMOS = ["spt", "shortest processing", "menor tempo de processamento", "edd",
          "earliest due", "sequenciamento", "make to order", "mto",
          "assemble to order", "make to stock", "nivel constante", "nível constante",
          "chase", "perseguicao", "perseguição", "lead time", "tempo de atravessamento",
          "wip", "estoque em processo", "gargalo", "schroeder",
          "ponto de desacoplamento", "carregamento finito", "carregamento infinito",
          "planejamento agregado", "objetivos de desempenho", "flexibilidade"]

doc = pdfium.PdfDocument(PDF)
paginas = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]
full = "\n".join(paginas)
low = full.lower()
brief = open(BRIEF, encoding="utf-8").read().lower()

print(f"apostila: {len(doc)} paginas, {len(full)} chars")
print(f"\n{'termo':32} {'apostila':>9} {'brief':>6}  leitura")
for t in TERMOS:
    na, nb = low.count(t), brief.count(t)
    if na and not nb:
        leitura = "<<< ESTA NA APOSTILA, FALTOU NO BRIEF"
    elif not na and not nb:
        leitura = ">>> NAO ESTA NA APOSTILA — conhecimento geral"
    elif na and nb:
        leitura = "ok (ancorado)"
    else:
        leitura = "no brief mas nao na apostila?"
    print(f"  {t:32} {na:>9} {nb:>6}  {leitura}")

# onde aparece SPT na apostila (se aparecer)
for t in ("spt", "sequenciamento", "planejamento agregado"):
    idx = [i + 1 for i, p in enumerate(paginas) if t in p.lower()]
    print(f"\n'{t}' aparece nas paginas: {idx[:14]}{' ...' if len(idx) > 14 else ''}")
