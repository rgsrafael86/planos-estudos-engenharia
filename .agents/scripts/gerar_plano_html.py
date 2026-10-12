#!/usr/bin/env python3
"""Injeta o JSON do plano no template blindado e grava o index.html.

O template é um RENDERIZADOR: o motor (HTML/CSS/JS) é protegido e só o JSON
entre STUDY_PLAN_START / STUDY_PLAN_END muda. Portanto este passo é
DETERMINÍSTICO — não é trabalho de LLM. Por isso o `agy` produz o JSON
(conteúdo) e este script faz o merge (estrutura).

Segurança: o JSON vai dentro de <script>. A sequência `</` é escapada para
`<\\/` para que nenhum conteúdo feche a tag antes da hora.

Uso:
  python3 gerar_plano_html.py <plano.json> <saida/index.html> [template]
"""
import json
import re
import sys
from pathlib import Path

TEMPLATE_PADRAO = ("/opt/data/cache/scratch/repos/planos-estudos-engenharia/"
                   "templates/template_blindado.html")
BLOCO = re.compile(
    r'(<script id="studyPlanData" type="application/json">)(.*?)(</script>)',
    re.DOTALL)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    plano_path, saida = Path(sys.argv[1]), Path(sys.argv[2])
    template_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(TEMPLATE_PADRAO)

    plano = json.loads(plano_path.read_text(encoding="utf-8"))
    html = template_path.read_text(encoding="utf-8")

    corpo = json.dumps(plano, ensure_ascii=False, indent=2)
    corpo_seguro = corpo.replace("</", "<\\/")   # não deixa o JSON fechar o <script>

    novo, n = BLOCO.subn(lambda m: m.group(1) + "\n" + corpo_seguro + "\n" + m.group(3), html)
    if n != 1:
        print(f"[ERRO] esperava 1 bloco studyPlanData, achei {n}")
        return 1
    if "STUDY_PLAN_START" not in novo or "STUDY_PLAN_END" not in novo:
        print("[ERRO] marcadores STUDY_PLAN_* desapareceram")
        return 1

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(novo, encoding="utf-8")
    print(json.dumps({
        "status": "gravado",
        "saida": str(saida),
        "bytes": len(novo),
        "json_bytes": len(corpo),
        "motor_preservado": len(html) - len(BLOCO.search(html).group(2)),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
