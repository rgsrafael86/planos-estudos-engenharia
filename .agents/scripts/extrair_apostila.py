#!/usr/bin/env python3
"""Extrai o TEXTO REAL da apostila para o brief do agy.

Por que existe: a v1 do plano foi gerada a partir do RESUMO do Notebook (~2 linhas
por tópico). O agy não teve fonte suficiente e completou com conhecimento geral —
SPT, EDD, MTO/ATO/MTS e nivel-vs-chase nao existem em nenhuma das 254 paginas.
Aqui a fonte real entra no brief.

Uso: extrair_apostila.py <pdf> <pagina_inicial_impressa> <pagina_final_impressa> [saida.txt]
"""
import re
import sys

import pypdfium2 as pdfium


def main():
    pdf = sys.argv[1]
    ini, fim = int(sys.argv[2]), int(sys.argv[3])
    saida = sys.argv[4] if len(sys.argv) > 4 else "/opt/data/cache/scratch/apostila_trecho.txt"

    doc = pdfium.PdfDocument(pdf)
    paginas = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]

    # o numero IMPRESSO costuma estar deslocado do indice do PDF: localiza pelo rodape
    desloc = 0
    for i, p in enumerate(paginas[:12]):
        m = re.search(r"\n\s*(\d{1,3})\s*$", p.strip())
        if m and int(m.group(1)) <= 12:
            desloc = i + 1 - int(m.group(1))
            break

    a, b = max(0, ini - 1 + desloc), min(len(paginas), fim + desloc)
    trecho = "\n".join(paginas[a:b])
    trecho = re.sub(r"[ \t]+", " ", trecho)
    trecho = re.sub(r"\n{3,}", "\n\n", trecho)

    open(saida, "w", encoding="utf-8").write(trecho)
    print(f"pdf={len(paginas)} p | deslocamento detectado={desloc} | "
          f"indice PDF {a+1}..{b} = paginas impressas {ini}..{fim}")
    print(f"chars={len(trecho)} -> {saida}")
    print("--- primeiros 200 chars ---")
    print(trecho[:200])


if __name__ == "__main__":
    main()
