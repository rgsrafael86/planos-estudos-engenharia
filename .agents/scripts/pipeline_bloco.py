#!/usr/bin/env python3
"""Esteira de um bloco: fonte -> brief -> agy -> auditoria -> merge -> portoes -> publica -> agenda.

POR QUE EXISTE
  Oito blocos a processar. Repetir à mão oito vezes é onde o erro entra (foi assim que a
  v1 saiu desancorada e o plano de 12/10 saiu sem 'topics'). Aqui o passo de JULGAMENTO
  continua sendo o brief; o resto é mecânico e roda igual toda vez.

OS TRES PORTOES, e cada um pega o que o outro nao ve:
  1. verdade   -> verificar_ancoragem.py  (a citacao existe na fonte?)
  2. forma     -> validate_plan.py        (6 questoes, 4 alternativas, cronograma cabe)
  3. navegador -> roda pelo chamador       (a pagina REALMENTE INICIA)

Uso: pipeline_bloco.py <data ISO> [--dry-run] [--sem-publicar]
"""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date as _date

REPO = "/opt/data/cache/scratch/repos/planos-estudos-engenharia"
SCRATCH = "/opt/data/cache/scratch"
ALOC = "/opt/data/workspace/academico/av1-online-2026-10/alocacao-topicos-blocos.json"
PY_PDF = "/opt/data/.local/venvs/pdf/bin/python"
AGY = "/opt/data/.local/bin/agy"
MODELO = "gemini-3.1-pro-high"

# slug do repo por disciplina (o mesmo do agenda_semestre.json)
SLUG = {"PCP": "planejamento-e-controle-da-produc-a-o-pcp",
        "Direitos Humanos": "direitos-humanos-cidadania-inclusao",
        "Relações Étnico-Raciais": "relacoes-etnico-raciais-e-diferentes-culturas"}
DISC_NOME = {"PCP": "Planejamento e Controle da Produção (PCP)",
             "Direitos Humanos": "Direitos Humanos, Cidadania e Inclusão",
             "Relações Étnico-Raciais": "Relações Étnico-Raciais e Diferentes Culturas"}
PDF = {"PCP": f"{SCRATCH}/apostilas/pcp.pdf",
       "Direitos Humanos": f"{SCRATCH}/apostilas/dh.pdf",
       "Relações Étnico-Raciais": f"{SCRATCH}/apostilas/etn.pdf"}


def sh(cmd, env=None, timeout=900):
    r = subprocess.run(cmd, capture_output=True, text=True,
                       env=env or os.environ, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def bloco_de(data_iso, disc_filtro=None):
    """Chave = data + disciplina. 16/10 tem DOIS blocos (ETN e DH) — buscar só
    pela data pegaria o errado."""
    aloc = json.load(open(ALOC, encoding="utf-8"))
    for disc, cfg in aloc["disciplinas"].items():
        if disc_filtro and disc != disc_filtro:
            continue
        for b in cfg["blocos"]:
            if b["data"] == data_iso:
                return disc, cfg, b
    return None, None, None


def extrair_fonte(disc, bloco):
    """Texto real das páginas do bloco. DH usa o PDF inteiro: as páginas citadas
    pelo Notebook (102-116, 195-211) não existem num PDF de 46 páginas — são da
    edição completa, então o excerto É a fonte."""
    tops = bloco.get("topicos", [])
    if disc == "Direitos Humanos" or not tops:
        ini, fim = 1, 999
    else:
        pags = [int(t["pag"]) for t in tops if t.get("pag")]
        ini, fim = (min(pags), max(pags) + 11) if pags else (1, 999)
    out = f"{SCRATCH}/fonte_{disc.replace(' ', '_')}_{bloco['data']}.txt"
    rc, msg = sh([PY_PDF, "/opt/data/scripts/extrair_apostila.py",
                  PDF[disc], str(ini), str(fim), out])
    if rc != 0 or not os.path.exists(out):
        return None, f"falha ao extrair: {msg[:200]}"
    return out, None


def montar_brief(disc, cfg, bloco, fonte_path):
    """O brief é o passo de JULGAMENTO. Ele carrega o TEXTO da fonte, o schema dos
    módulos COLADO literalmente e as regras que já falharam uma vez."""
    fonte = open(fonte_path, encoding="utf-8").read()
    tops = bloco.get("topicos", [])
    lista = "\n".join(f"  - {t['id']}: {t['titulo']}" + (f" (p. {t['pag']})" if t.get("pag") else "")
                      for t in tops) or "  (bloco de revisão — sintetize o que já foi estudado)"
    prova = cfg["prova"]
    d = _date.fromisoformat(bloco["data"])

    return f"""NÃO use ferramentas (não rode comandos, não leia nem escreva arquivos). Todo o material está neste brief. Responda DIRETAMENTE com o JSON.

## TAREFA
Gere o conteúdo de um plano de estudos de {DISC_NOME[disc]} (prova em {prova}) para a UNIASSELVI.

## ANCORAGEM ESTRITA
O texto da apostila está no FINAL, entre <<<APOSTILA>>> e <<<FIM>>>.
TODA questão deve ser respondível usando APENAS esse texto. É PROIBIDO usar conhecimento geral
que não esteja no texto. Se o texto não cobre um assunto, não pergunte sobre ele.

## MÓDULOS DESTE BLOCO — um módulo por tópico abaixo
{lista}

## SCHEMA EXATO DA RAIZ
{{
  "id": "plano-{d.isoformat()}",
  "title": "Plano de Estudos: {DISC_NOME[disc]} — <tema do bloco>",
  "subtitle": "Preparação para a AV1",
  "institution": "UNIASSELVI",
  "course": "Engenharia de Produção",
  "discipline": "{DISC_NOME[disc]}",
  "disciplineCode": "",
  "professor": "",
  "student": "R.G.",
  "classGroup": "",
  "author": "Hermes Jidoka",
  "estimatedTime": "{bloco['min']} min",
  "level": "Graduação",
  "targetDate": "{prova[8:10]}/{prova[5:7]}/{prova[0:4]}",
  "studyDate": "{d.strftime('%d/%m/%Y')}",
  "scheduledStart": "{bloco.get('inicio', '16:00')}",
  "scheduledEnd": "{bloco.get('fim', '18:30')}",
  "availableMinutes": {bloco['min']},
  "scheduleSource": "Google Agenda",
  "contentSource": "Apostila via Gemini Notebook",
  "objective": "<uma frase: o que o aluno deve saber ao fim deste bloco>",
  "schedule": [
    {{"start":"HH:MM","end":"HH:MM","duration":"N min","activity":"string"}}
  ],
  "modules": [
    {{
      "id": "m1",
      "title": "string",
      "duration": "N min",
      "topics": ["string", "string"],
      "source": {{"origin":"Apostila","document":"{cfg['apostila']}","location":"string","pages":"string","searchHint":"string","url":""}},
      "videos": [{{"title":"string","url":"https://www.youtube.com/results?search_query=..."}}]
    }}
  ],
  "questions": [
    {{"id":"q1","prompt":"string","options":["a","b","c","d"],"answer":0,"explanation":"string"}}
  ]
}}

## REGRAS OBRIGATÓRIAS — o template BLOQUEIA a página inteira se violar
1. `id`, `title`, `discipline`, `studyDate`, `objective` não podem ser vazios.
2. `modules`: um por tópico listado acima. Cada um com `id`, `title`, `topics` (**LISTA, e o nome é
   exatamente `topics`** — não use `contents`, `conteudo`, `topic` nem `tópicos`), `duration`, `source`, `videos`.
3. `questions`: EXATAMENTE 6. Cada uma com `id`, `prompt`, EXATAMENTE 4 `options`, `answer` inteiro 0–3,
   `explanation` não vazia citando a página da apostila (ex.: "Conforme a p. 14, ...").
   **A `explanation` deve conter uma TRANSCRIÇÃO LITERAL entre aspas, copiada caractere a caractere do
   texto da apostila.** Não parafraseie, não corrija a gramática, não encurte com reticências no meio,
   não troque palavras por sinônimos. O trecho entre aspas tem de existir no texto, idêntico.
   Se não houver frase literal que sustente a resposta, escolha outro trecho do texto para a questão —
   jamais invente ou reescreva a citação. Citação reformulada reprova o plano no portão de verdade.
4. NENHUM `id` duplicado entre módulos e questões.
5. `schedule`: itens com `start` e `end` em HH:MM, **sem sobreposição**, soma ≤ {bloco['min']} minutos.
6. Cada módulo com pelo menos 1 vídeo, `url` de BUSCA DINÂMICA do YouTube
   (`https://www.youtube.com/results?search_query=...`), específica para o tema.
7. `student` exatamente "R.G.".
8. Não exponha URL privada. Não inclua conteúdo demonstrativo.
9. Distribua as respostas corretas entre A, B, C e D.
10. As questões são de AV1: aplicação e compreensão, não decoreba.

## SAÍDA
Apenas o JSON, começando com {{ e terminando com }}. Sem cercas de código, sem comentário.

<<<APOSTILA>>>
{fonte}
<<<FIM>>>
"""


def gerar(brief_path, out_path):
    env = dict(os.environ, HOME="/opt/data/home", AGY_CLI_DISABLE_AUTO_UPDATE="true")
    rc, msg = sh([AGY, "-p", open(brief_path, encoding="utf-8").read(),
                  "--model", MODELO, "--output-format", "json"], env=env, timeout=1800)
    if rc != 0:
        return None, f"agy rc={rc}: {msg[-300:]}"
    # o envelope é UMA linha JSON; stderr pode vir concatenado — isola a última linha válida
    env_json = None
    for linha in reversed(msg.strip().splitlines()):
        try:
            env_json = json.loads(linha)
            break
        except Exception:
            continue
    if env_json is None:
        return None, f"envelope ilegivel: {msg[-300:]}"
    resp = env_json.get("response", "")
    if not resp.strip():
        return None, f"resposta vazia (status={env_json.get('status')}, denied={env_json.get('denied_actions')})"
    open(out_path, "w", encoding="utf-8").write(resp)
    return env_json, None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    data_iso = sys.argv[1]
    disc_arg = next((a for a in sys.argv[2:] if not a.startswith("--")), None)
    dry = "--dry-run" in sys.argv
    disc, cfg, bloco = bloco_de(data_iso, disc_arg)
    if not bloco:
        print(f"[ERRO] {data_iso} não está na alocação")
        return 1
    print(f"### {data_iso} — {disc} — {bloco['min']} min — {len(bloco.get('topicos', []))} tópicos")

    fonte, err = extrair_fonte(disc, bloco)
    if err:
        print(f"    [FALHA] {err}")
        return 1
    print(f"    1. fonte: {fonte} ({os.path.getsize(fonte)} bytes)")

    brief = f"{SCRATCH}/brief_{disc.replace(' ', '_')}_{data_iso}.txt"
    open(brief, "w", encoding="utf-8").write(montar_brief(disc, cfg, bloco, fonte))
    print(f"    2. brief: {brief} ({os.path.getsize(brief)} bytes)")
    if dry:
        return 0

    saida = f"{SCRATCH}/plano_{disc.replace(' ', '_')}_{data_iso}.json"
    env_json, err = gerar(brief, saida)
    if err:
        print(f"    [FALHA] {err}")
        return 1
    u = env_json.get("usage", {})
    print(f"    3. agy: {MODELO} | total {u.get('total_tokens')} tokens | "
          f"{env_json.get('duration_seconds', 0):.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
