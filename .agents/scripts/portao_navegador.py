#!/usr/bin/env python3
"""PORTAO 3 — a pagina INICIA no navegador de verdade?

POR QUE EXISTE
  O Rafael abriu o plano de 12/10 e nao havia conteudo: o executor tinha usado
  `contents`/`topic`/`pages` em vez de `topics`/`source`, e o motor do template BLOQUEIA a
  pagina inteira quando falta `topics`. O portao de forma (validate_plan.py) APROVOU, porque
  ele valida o JSON e nao executa o JavaScript. "Vc me entregou material sem abrir o link e
  validar tudo." Este portao e o que fecha esse buraco: ele abre a URL publica, deixa o JS
  rodar e confere o que aparece na TELA.

  Nao substitui o portao 1 (verdade) nem o 2 (forma): cada um pega o que os outros nao veem.
  Um plano pode passar no 2 e reprovar aqui — foi exatamente o caso do plano de 12/10.

Uso: portao_navegador.py <url1> [url2 ...]
     portao_navegador.py --reprovar-sem-js <url>   (teste negativo)
"""
import json
import sys
import time
import urllib.request

CDP = "http://127.0.0.1:9222"

JS = """(() => {
  const t = document.body.innerText || "";
  return JSON.stringify({
    titulo: (document.title || "").slice(0, 70),
    modulos: document.querySelectorAll('.module').length,
    questoes: document.querySelectorAll('.question').length,
    alternativas: document.querySelectorAll('.option').length,
    vazio: document.getElementById('app') ? (document.getElementById('app').innerHTML.length < 50) : null,
    chars: t.length,
    alarme: /sem t[óo]picos|não foi poss[íi]vel|Erro ao renderizar|undefined/i.test(t),
    inicio: t.replace(/\\s+/g, " ").slice(0, 150)
  });
})()"""


def nova_aba(url: str) -> str:
    req = urllib.request.Request(f"{CDP}/json/new?{url}", method="PUT")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["id"]


def fechar_aba(tid: str):
    try:
        urllib.request.urlopen(f"{CDP}/json/close/{tid}", timeout=10).read()
    except Exception:
        pass


def avaliar(tid: str, expressao: str, espera: float = 0.0):
    import websocket
    ws = websocket.create_connection(
        f"ws://127.0.0.1:9222/devtools/page/{tid}", timeout=40,
        suppress_origin=True)
    try:
        ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        ws.recv()
        if espera:
            time.sleep(espera)
        ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate",
                            "params": {"expression": expressao, "returnByValue": True}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 2:
                return msg["result"]["result"].get("value")
    finally:
        ws.close()


def main() -> int:
    urls = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not urls:
        print(__doc__)
        return 2
    falhas = 0
    for url in urls:
        tid = nova_aba(url)
        time.sleep(6)                      # deixa o Pages/CDN servir e o JS rodar
        bruto = avaliar(tid, JS)
        fechar_aba(tid)
        print(f"\n### {url}")
        if not bruto:
            print("   [FALHA] nao consegui ler a pagina")
            falhas += 1
            continue
        d = json.loads(bruto)
        print(f"   titulo ....... {d['titulo']}")
        print(f"   modulos ...... {d['modulos']}")
        print(f"   questoes ..... {d['questoes']}")
        print(f"   alternativas . {d['alternativas']}")
        print(f"   texto visivel: {d['chars']} chars")
        problemas = []
        if d["modulos"] == 0 or d["questoes"] == 0 or d["alternativas"] == 0:
            problemas.append("a pagina NAO RENDERIZOU conteudo (modulos/questoes/alternativas zerados)")
        if d["chars"] < 2000:
            problemas.append(f"texto visivel muito curto ({d['chars']} chars)")
        if d["alarme"]:
            problemas.append("a pagina exibe mensagem de erro")
        if problemas:
            falhas += 1
            for p in problemas:
                print(f"   !! {p}")
        else:
            print(f"   inicio ....... {d['inicio'][:100]}")
            print("   PORTAO 3: PASSOU — a pagina inicia e renderiza")
    print("\n" + "=" * 74)
    print(f"VEREDITO: {'REPROVADO' if falhas else 'PASSOU'} — {falhas} de {len(urls)} reprovada(s)")
    print("=" * 74)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
