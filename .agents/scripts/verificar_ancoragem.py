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


def carregar_fonte(caminho: Path, ini: int | None, fim: int | None) -> tuple[str, int]:
    if caminho.suffix.lower() == ".pdf":
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(caminho))
        n = len(doc)
        a = (ini - 1) if ini else 0
        b = fim if fim else n
        return "\n".join(doc[i].get_textpage().get_text_range() for i in range(a, min(b, n))), n
    return caminho.read_text(encoding="utf-8"), 0


def normalizar(s: str) -> str:
    """Tira acento, caixa, e — crítico — cabeçalho/rodapé de página.

    ORDEM IMPORTA: o cabeçalho da apostila vem QUEBRADO EM DUAS LINHAS na extração
    ('UNIDADE 1 | OS FUNDAMENTOS DO PLANEJAMENTO DA PRODUÇÃO\\n8\\n'), então o regex
    não o pega antes de colapsar o espaço. Colapsar primeiro, limpar depois — se limpar
    antes, a citação verdadeira é acusada de falsa.
    """
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s)                     # colapsa ANTES (junta o cabeçalho)
    s = re.sub(r"unidade\s*\d+\s*\|.{0,90}?\d{1,3}", " ", s, flags=re.I)
    s = re.sub(r"tema\s*\d+\s*\|.{0,90}?\d{1,3}", " ", s, flags=re.I)
    s = re.sub(r"\s+", " ", s)                     # colapsa DEPOIS (a remoção deixa espaço triplo)
    return s.lower().strip()


def auditar(plano: dict, fonte_norm: str, rotulo: str) -> list[str]:
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
        citacoes = [c for c in re.findall(r"['\u2018\u2019]([^'\u2018\u2019]{18,200})['\u2018\u2019]", exp)
                    if len(c.split()) >= MIN_PALAVRAS_CITACAO]
        conf = sum(1 for c in citacoes if normalizar(c) in fonte_norm)

        if not paginas:
            erros.append(f"{qid}: SEM citação de página")
        for c in citacoes:
            if normalizar(c) not in fonte_norm:
                # quanto do trecho existe? distingue paráfrase de invenção
                pal = c.split()
                maior = 0
                for n in range(len(pal), 3, -1):
                    if any(normalizar(" ".join(pal[i:i + n])) in fonte_norm
                           for i in range(len(pal) - n + 1)):
                        maior = n
                        break
                if maior:
                    erros.append(f"{qid}: citação REFORMULADA ({maior}/{len(pal)} palavras reais) — "
                                 f"\"{c[:70]}\"")
                else:
                    erros.append(f"{qid}: citação NÃO ENCONTRADA na fonte — \"{c[:70]}\"")

        marca = "OK " if paginas and conf == len(citacoes) else "!! "
        print(f"  {marca}{qid}: páginas {paginas or 'NENHUMA'} | "
              f"citações literais {conf}/{len(citacoes)}")
    return erros


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    plano = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    ini = int(sys.argv[3]) if len(sys.argv) > 3 else None
    fim = int(sys.argv[4]) if len(sys.argv) > 4 else None
    texto, npag = carregar_fonte(Path(sys.argv[2]), ini, fim)
    fn = normalizar(texto)

    print("=" * 78)
    print(f"AUDITORIA DE ANCORAGEM — fonte: {Path(sys.argv[2]).name}"
          f"{f' (páginas {ini}–{fim})' if ini else ''}")
    print(f"fonte: {npag or 'n/a'} páginas, {len(texto)} chars, {len(fn)} normalizados")
    print("=" * 78)

    erros = auditar(plano, fn, "QUESTÕES")

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
