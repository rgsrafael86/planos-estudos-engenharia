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


_RE_CABECALHO = re.compile(r"(T[ÓO]PICO|UNIDADE|TEMA)[^\n]*\n\s*(\d{1,3})\s*\n", re.I)


def deslocamento(paginas: list[str]) -> int:
    """Deslocamento entre índice do PDF e número IMPRESSO, decidido pela MAIORIA.

    O deslocamento é propriedade do DOCUMENTO, não de cada página. Resolvê-lo página a
    página deixa buracos: em PCP a página índice 75 abre com figura, o cabeçalho não casa
    o padrão, ela vira chave 75 — e o material a numera 63. Citação correta, chave errada.
    Aqui cada cabeçalho que casa VOTA (indice - numero) e vence o mais votado; o resultado
    vale para todas as páginas, inclusive as que não têm cabeçalho legível.
    """
    from collections import Counter
    votos = Counter()
    for i, p in enumerate(paginas):
        m = _RE_CABECALHO.match(p.strip())
        if m:
            votos[(i + 1) - int(m.group(2))] += 1
    return votos.most_common(1)[0][0] if votos else 0


def main():
    pdf = sys.argv[1]
    ini, fim = int(sys.argv[2]), int(sys.argv[3])
    saida = sys.argv[4] if len(sys.argv) > 4 else "/opt/data/cache/scratch/apostila_trecho.txt"

    doc = pdfium.PdfDocument(pdf)
    paginas = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]

    # deslocamento único para o documento, decidido pela maioria dos cabeçalhos legíveis
    desloc = deslocamento(paginas)

    def impressa(i: int) -> int:
        return (i + 1) - desloc

    idxs = [i for i in range(len(paginas)) if ini <= impressa(i) <= fim] or \
           list(range(max(0, ini - 1), min(len(paginas), fim)))
    a, b = idxs[0], idxs[-1] + 1

    # --- BURACO FECHADO (12/10/2026): o trecho era entregue como TEXTO CORRIDO, sem
    # marcador de página — e o brief exige que cada questão cite a página. O modelo não
    # tinha como saber o número e CHUTAVA. Agora cada página leva o número IMPRESSO.
    partes = []
    for i in range(a, b):
        corpo = re.sub(r"[ \t]+", " ", paginas[i]).strip()
        partes.append(f"[[p. {impressa(i)}]]\n{corpo}")
    trecho = "\n".join(partes)
    trecho = re.sub(r"\n{3,}", "\n\n", trecho)

    open(saida, "w", encoding="utf-8").write(trecho)
    print(f"pdf={len(paginas)} p | deslocamento={desloc} | indice PDF {a+1}..{b} | "
          f"paginas impressas {impressa(a)}..{impressa(b-1)}")
    print(f"chars={len(trecho)} -> {saida}")


if __name__ == "__main__":
    main()
