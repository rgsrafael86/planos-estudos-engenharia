#!/usr/bin/env python3
"""Aceite do PORTAL: abre a página publicada no Chromium (CDP), deixa o JS rodar e conta
o que aparece na TELA. O dashboard monta os cards no cliente a partir do
agenda_semestre.json — checar só o HTML estático não prova nada.

Uso: conferir_portal.py <url_do_portal> [quantos_planos_esperados]
"""
import json
import sys
import time
import urllib.request

CDP = "http://127.0.0.1:9222"

JS = """(() => {
  const links = [...document.querySelectorAll('a[href*="/planos/"]')].map(a => a.getAttribute('href'));
  const uniq = [...new Set(links)];
  const t = document.body.innerText || "";
  return JSON.stringify({
    titulo: (document.title || "").slice(0, 80),
    cards: uniq.length,
    links: uniq.slice(0, 30),
    chars: t.length,
    vazio: t.trim().length < 50,
    erro: /erro|failed|uncaught/i.test(t) ? t.slice(0, 120) : null
  });
})()"""


def nova_aba(url):
    req = urllib.request.Request(f"{CDP}/json/new?{url}", method="PUT")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["id"]


def avaliar(tid, expr, espera=4.0):
    import websocket
    ws = websocket.create_connection(f"ws://127.0.0.1:9222/devtools/page/{tid}",
                                     timeout=60, suppress_origin=True)
    try:
        ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        ws.recv()
        time.sleep(espera)                      # deixa o fetch + render do dashboard rodar
        ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate",
                            "params": {"expression": expr, "returnByValue": True}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 2:
                return msg["result"]["result"].get("value")
    finally:
        ws.close()


def main():
    url = sys.argv[1]
    esperado = int(sys.argv[2]) if len(sys.argv) > 2 else None
    tid = nova_aba(url)
    try:
        raw = avaliar(tid, JS)
        if raw is None:
            print("VEREDITO: REPROVADO — a página não devolveu nada ao JS")
            return 1
        d = json.loads(raw)
        print(f"  titulo ....... {d['titulo']}")
        print(f"  cards/links .. {d['cards']} link(s) de plano renderizado(s)")
        print(f"  texto visivel  {d['chars']} chars | vazio: {d['vazio']}")
        if d["erro"]:
            print(f"  possivel erro: {d['erro']}")
        for l in d["links"][:8]:
            print(f"     {l}")
        if esperado is not None and d["cards"] < esperado:
            print(f"VEREDITO: REPROVADO — esperava >= {esperado} planos no dashboard, renderizou {d['cards']}")
            return 1
        print("VEREDITO: PASSOU — o dashboard carrega e renderiza os planos")
        return 0
    finally:
        try:
            urllib.request.urlopen(f"{CDP}/json/close/{tid}", timeout=10).read()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
