#!/usr/bin/env python3
"""Auditoria de ancoragem — confere cada citação do plano contra a fonte real.

O QUE ESTE SCRIPT RESPONDE
  "As questões do plano estão ancoradas na fonte, ou o modelo completou com conhecimento geral?"
  Ele NÃO confere forma (isso é o validate_plan.py) — ele confere VERDADE.

POR QUE EXISTE
  A v1 do plano de PCP foi publicada com questões sobre SPT/EDD, MTO/ATO/MTS e nível-vs-perseguição.
  Nenhum desses termos existe nas 254 páginas da apostila: o executor completou com conhecimento geral
  porque o brief levou o RESUMO da fonte, não o texto. O portão estrutural aprovou — forma correta,
  conteúdo desancorado. Este script é o que pega isso.

Uso:
  verificar_ancoragem.py <plano.json> <fonte.pdf|fonte.txt> [pagina_ini] [pagina_fim]

Saída: por questão, se cita página e se cada citação literal existe na fonte. Exit 0 = passou.

ARMADILHA CONHECIDA (por isso o normalizador é agressivo)
  A apostila tem CABEÇALHO DE PÁGINA correndo no meio da frase na extração do PDF:
  "...a interrupção do seu processo produtivo UNIDADE 1 | OS FUNDAMENTOS DO PLANEJAMENTO DA PRODUÇÃO 8
   é complexa e, normalmente, onerosa."
  Sem remover cabeçalho/rodapé, o conferidor acusa citação VERDADEIRA como falsa — e falso positivo de
  verificador queima a confiança na verificação inteira.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

MIN_PALAVRAS_CITACAO = 6   # abaixo disso é comentário entre aspas, não citação

# --- BURACO FECHADO (12/10/2026): o regex só reconhecia ASPAS SIMPLES.
# O modelo escreve as citações com aspas DUPLAS ("..."), então o portão lia 0 citações
# e, com `conf == len(citacoes)` = 0 == 0, dava PASSOU sem examinar nada. Ele era cego
# à própria coisa que existe para auditar. Aceita agora as quatro formas: ' " ‘ ’ “ ”.
_P = "'\u2018\u2019\"\u201c\u201d"
RE_CITACAO = re.compile(f"[{_P}]([^{_P}]{{18,400}})[{_P}]")


_RE_CABECALHO = re.compile(r"(T[ÓO]PICO|UNIDADE|TEMA)[^\n]*\n\s*(\d{1,3})\s*\n", re.I)


def deslocamento(paginas: list[str]) -> int:
    """Deslocamento índice-do-PDF -> número IMPRESSO, decidido pela MAIORIA — MESMA regra
    do extrair_apostila.py. Se as duas divergirem, o portão reprova o que o brief mandou citar.

    Propriedade do DOCUMENTO, não de cada página: resolver por página deixa buracos (uma
    página que abre com figura vira chave = índice) e o portão acusa citação correta como
    ausente. Cada cabeçalho legível vota (indice - numero); vence o mais votado.
    """
    from collections import Counter
    votos = Counter()
    for i, p in enumerate(paginas):
        m = _RE_CABECALHO.match(p.strip())
        if m:
            votos[(i + 1) - int(m.group(2))] += 1
    return votos.most_common(1)[0][0] if votos else 0


def carregar_fonte(caminho: Path, ini: int | None, fim: int | None) -> tuple[str, int, dict[int, str]]:
    """Devolve (texto, n_paginas, {pagina: texto_normalizado}).

    O mapa é indexado pela página IMPRESSA — a que o brief manda citar e a que o aluno vê.
    Em PCP o índice 53 do PDF é a página impressa 41; sem o deslocamento o portão compara
    contra a página errada e reprova citação literal correta.
    """
    if caminho.suffix.lower() == ".pdf":
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(caminho))
        n = len(doc)
        brutas = [doc[i].get_textpage().get_text_range() for i in range(n)]
        desloc = deslocamento(brutas)
        sel = []
        mapa: dict[int, str] = {}
        for i in range(n):
            num = (i + 1) - desloc
            if ini and num < ini:
                continue
            if fim and num > fim:
                continue
            sel.append(i)
            if num not in mapa:
                mapa[num] = normalizar(brutas[i])
        texto = "\n".join(brutas[i] for i in sel)
        return texto, n, mapa
    texto = caminho.read_text(encoding="utf-8")
    return texto, 0, {}   # txt não tem fronteira de página — só a checagem global


def normalizar(s: str) -> str:
    """Tira acento, caixa, e — crítico — cabeçalho/rodapé de página.

    ORDEM IMPORTA: o cabeçalho da apostila vem QUEBRADO EM DUAS LINHAS na extração
    ('UNIDADE 1 | OS FUNDAMENTOS DO PLANEJAMENTO DA PRODUÇÃO\\n8\\n'), então o regex
    não o pega antes de colapsar o espaço. Colapsar primeiro, limpar depois — se limpar
    antes, a citação verdadeira é acusada de falsa.
    """
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    # --- BURACO FECHADO (12/10/2026): a extração do PDF deixa NÃO-CARACTERES no meio de
    # palavra — 'indi\uFFFEvíduo'. O modelo cita 'indivíduo', a comparação falha e o portão
    # reprova citação literal. Remove controles/formatação, preservando espaço e quebra.
    s = "".join(c for c in s
                if c in " \n\t" or unicodedata.category(c) not in ("Cc", "Cf", "Co", "Cn"))
    s = re.sub(r"\s+", " ", s)                     # colapsa ANTES (junta o cabeçalho)
    s = re.sub(r"unidade\s*\d+\s*\|.{0,90}?\d{1,3}", " ", s, flags=re.I)
    s = re.sub(r"tema\s*\d+\s*\|.{0,90}?\d{1,3}", " ", s, flags=re.I)
    # --- BURACO FECHADO (12/10/2026): o PDF quebra palavra no fim da linha e o extrator
    # preserva o hífen ('conheci-\nmento'). O modelo, ao citar, escreve a palavra inteira
    # ('conhecimento') — e o portão acusava "citação NÃO ENCONTRADA" num trecho literal.
    # Como os DOIS lados passam por aqui, remover 'hífen + espaço' dos dois os iguala.
    s = re.sub(r"-\s+", "", s)
    s = re.sub(r"\s+", " ", s)                     # colapsa DEPOIS (a remoção deixa espaço triplo)
    return s.lower().strip()


def auditar(plano: dict, fonte_norm: str, paginas_norm: dict[int, str], rotulo: str) -> list[str]:
    erros: list[str] = []

    # --- schema dos módulos: o motor do template BLOQUEIA a página inteira se faltar 'topics'.
    # Custo de descobrir isso só no navegador: o Rafael abriu e viu "Módulo m1 sem tópicos".
    for m in plano.get("modules", []):
        mid = m.get("id", "?")
        if not isinstance(m.get("topics"), list) or not m.get("topics"):
            achou = [k for k in m if k in ("contents", "conteudos", "topic", "topicos", "tópicos")]
            dica = f" — achou {achou!r} no lugar" if achou else ""
            erros.append(f"{mid}: 'topics' ausente ou não é lista{dica} (o template BLOQUEIA a página)")
        if not m.get("videos"):
            erros.append(f"{mid}: sem vídeos")

    questoes = plano.get("questions", [])
    print(f"\n### {rotulo} — {len(questoes)} questões")
    for q in questoes:
        qid = q.get("id", "?")
        exp = q.get("explanation", "") or ""
        paginas = sorted(set(re.findall(r"p\.\s*(\d+(?:\s*[–-]\s*\d+)?)", exp)))
        citacoes = [c for c in RE_CITACAO.findall(exp)
                    if len(c.split()) >= MIN_PALAVRAS_CITACAO]

        # --- BURACO FECHADO (12/10/2026): sem aspas, `conf == len(citacoes)` era 0 == 0
        # e a questão passava sem NADA ser verificado. Passar por vacuidade é pior que
        # reprovar: dá confiança falsa. Agora exige-se ao menos uma citação literal.
        if not citacoes:
            erros.append(f"{qid}: SEM citação literal entre aspas — nada a verificar (passe vazio)")
            print(f"  !! {qid}: páginas {paginas or 'NENHUMA'} | SEM citação literal")
            continue

        # --- BURACO FECHADO (12/10/2026): a citação era conferida contra a fonte INTEIRA.
        # Uma frase da p. 40 sustentava uma questão que dizia "p. 41". Agora confere-se
        # contra a união das páginas CITADAS.
        alvo = fonte_norm
        rotulo_pag = "fonte inteira"
        if paginas_norm and paginas:
            idx = set()
            for p in paginas:
                m = re.match(r"(\d+)\s*[–-]\s*(\d+)", p)
                if m:
                    idx.update(range(int(m.group(1)), int(m.group(2)) + 1))
                else:
                    idx.add(int(p))
            textos = [paginas_norm[i] for i in sorted(idx) if i in paginas_norm]
            if textos:
                alvo = " ".join(textos)
                rotulo_pag = f"páginas citadas {paginas}"

        conf = sum(1 for c in citacoes if normalizar(c) in alvo)
        for c in citacoes:
            if normalizar(c) not in alvo:
                # quanto do trecho existe? distingue paráfrase de invenção
                pal = c.split()
                maior = 0
                for n in range(len(pal), 3, -1):
                    if any(normalizar(" ".join(pal[i:i + n])) in alvo
                           for i in range(len(pal) - n + 1)):
                        maior = n
                        break
                if maior:
                    erros.append(f"{qid}: citação REFORMULADA ({maior}/{len(pal)} palavras reais) — "
                                 f"\"{c[:70]}\"")
                elif normalizar(c) in fonte_norm:
                    erros.append(f"{qid}: citação existe na fonte mas NÃO nas {rotulo_pag} — "
                                 f"\"{c[:70]}\"")
                else:
                    erros.append(f"{qid}: citação NÃO ENCONTRADA na fonte — \"{c[:70]}\"")

        marca = "OK " if conf == len(citacoes) else "!! "
        print(f"  {marca}{qid}: páginas {paginas or 'NENHUMA'} | "
              f"citações literais {conf}/{len(citacoes)} (checadas em {rotulo_pag})")
    return erros


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    plano = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    ini = int(sys.argv[3]) if len(sys.argv) > 3 else None
    fim = int(sys.argv[4]) if len(sys.argv) > 4 else None
    texto, npag, paginas_norm = carregar_fonte(Path(sys.argv[2]), ini, fim)
    fn = normalizar(texto)

    print("=" * 78)
    print(f"AUDITORIA DE ANCORAGEM — fonte: {Path(sys.argv[2]).name}"
          f"{f' (páginas {ini}–{fim})' if ini else ''}")
    print(f"fonte: {npag or 'n/a'} páginas, {len(texto)} chars, {len(fn)} normalizados")
    print("=" * 78)

    erros = auditar(plano, fn, paginas_norm, "QUESTÕES")

    # termos fora da fonte: procura vocabulário de gestão que não esteja na fonte
    suspeitos = ["spt", "shortest processing", "edd", "earliest due", "lpt",
                 "make to order", "assemble to order", "make to stock", "chase demand",
                 "nivel constante", "perseguicao"]
    corpo = normalizar(json.dumps(plano, ensure_ascii=False))
    fora = [t for t in suspeitos if t in corpo and t not in fn]
    if fora:
        erros.append("termos fora da fonte: " + ", ".join(fora))

    print("\n" + "=" * 78)
    if erros:
        print(f"VEREDITO: REPROVADO — {len(erros)} problema(s)")
        for e in erros:
            print(f"   - {e}")
    else:
        print("VEREDITO: PASSOU — toda questão cita página e toda citação existe na fonte")
    print("=" * 78)
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
