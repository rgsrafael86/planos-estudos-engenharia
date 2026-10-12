#!/usr/bin/env python3
"""Livro-caixa de consumo do `agy` — o que dá para medir sem a TUI.

POR QUE EXISTE
  A cota restante do Antigravity NÃO é legível headless: o painel é o comando de barra
  `/usage` (alias `/quota`), que abre uma TUI e consulta o backend. Verificado em
  11/10/2026: não há subcomando (`agy usage` -> "unexpected argument"), não há arquivo de
  cota em `~/.gemini/antigravity-cli/`, e os logs só registram `doRefreshQuota: starting
  reload` — o valor não é persistido de forma legível.

  O que É legível: o envelope `--output-format json` de cada run traz
  `usage{input_tokens, output_tokens, thinking_tokens, cache_read_tokens, total_tokens}`.
  Somando os envelopes, sabe-se quanto a esteira QUEIMOU — que é o insumo para decidir
  onde usar o pool do Gemini e onde gastar o pool separado de Claude/GPT.

ESTRUTURA DA COTA (doc oficial, lida 11/10/2026)
  - AI Pro: cota alta, renovada a cada 5 h até o limite semanal.
  - DOIS medidores independentes no seletor de modelo: "Gemini models" e
    "Claude and GPT models" — reservas separadas na mesma assinatura.
  - Gemini é baseline de todos os planos; Claude/GPT são pool de terceiro, menor.

Uso:
  agy_usage_ledger.py registrar <envelope.json> <modelo> <tarefa>
  agy_usage_ledger.py varrer <dir>            # registra todo *.json de envelope ainda não lançado
  agy_usage_ledger.py relatorio
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path("/opt/data/workspace/academico/av1-online-2026-10/agy_usage_ledger.json")

# pool de cota por família — é o que a decisão de modelo precisa enxergar
POOL = {"gemini": "Gemini models", "claude": "Claude and GPT models",
        "gpt": "Claude and GPT models"}


def pool_de(modelo: str) -> str:
    m = (modelo or "").lower()
    for k, v in POOL.items():
        if k in m:
            return v
    return "desconhecido"


def carregar() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {"lancamentos": []}


def gravar(d: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    tmp = LEDGER.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(LEDGER)


def registrar(envelope: Path, modelo: str, tarefa: str) -> dict:
    d = json.loads(envelope.read_text(encoding="utf-8"))
    u = d.get("usage") or {}
    lan = {
        "quando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tarefa": tarefa,
        "modelo": modelo,
        "pool": pool_de(modelo),
        "status": d.get("status"),
        "duracao_s": round(d.get("duration_seconds") or 0, 1),
        "input": u.get("input_tokens", 0),
        "output": u.get("output_tokens", 0),
        "thinking": u.get("thinking_tokens", 0),
        "total": u.get("total_tokens", 0),
        "arquivo": envelope.name,
    }
    return lan


def relatorio() -> int:
    d = carregar()
    l = d["lancamentos"]
    if not l:
        print("ledger vazio")
        return 0
    print(f"{'tarefa':34} {'modelo':24} {'pool':22} {'total':>8} {'s':>6}")
    print("-" * 100)
    for x in l:
        print(f"  {x['tarefa'][:32]:34} {x['modelo'][:22]:24} {x['pool']:22} "
              f"{x['total']:>8} {x['duracao_s']:>6}")
    print("-" * 100)
    por_pool: dict = {}
    for x in l:
        p = por_pool.setdefault(x["pool"], {"runs": 0, "total": 0})
        p["runs"] += 1
        p["total"] += x["total"]
    for p, v in por_pool.items():
        print(f"  {p:24} {v['runs']:>3} runs  {v['total']:>9} tokens")
    print(f"\n  TOTAL: {len(l)} runs, {sum(x['total'] for x in l)} tokens")
    print("  (a cota RESTANTE não é legível aqui — só o painel /usage na TUI)")
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "relatorio"
    if cmd == "registrar":
        d = carregar()
        lan = registrar(Path(sys.argv[2]), sys.argv[3], sys.argv[4])
        d["lancamentos"] = [x for x in d["lancamentos"] if x["arquivo"] != lan["arquivo"]]
        d["lancamentos"].append(lan)
        gravar(d)
        print(json.dumps(lan, ensure_ascii=False))
        return 0
    if cmd == "varrer":
        dirp = Path(sys.argv[2])
        d = carregar()
        ja = {x["arquivo"] for x in d["lancamentos"]}
        novos = 0
        for f in sorted(dirp.glob("*.json")):
            try:
                j = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if "usage" not in j or f.name in ja:
                continue
            modelo = j.get("model") or j.get("model_name") or "desconhecido"
            d["lancamentos"].append(registrar(f, modelo, f.stem))
            novos += 1
        gravar(d)
        print(f"{novos} lancamentos novos (modelo ausente no envelope -> marque a mao)")
        return 0
    return relatorio()


if __name__ == "__main__":
    sys.exit(main())
