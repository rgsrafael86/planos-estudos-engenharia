# Esteira de planos de estudo — como um plano nasce

Documento de operação. Escrito em 11/10/2026, depois de a v1 do plano de PCP ir ao ar **desancorada**
e só ser pega porque o Rafael perguntou *"você verificou?"*.

## O fluxo (1 run de LLM por bloco)

**A esteira inteira é um comando:** `python3 /opt/data/scripts/pipeline_bloco.py <AAAA-MM-DD> [disciplina]`
(disciplina é necessária em 16/10, que tem **dois** blocos: ETN e DH).

```
1. FONTE     extrair_apostila.py <pdf> <ini> <fim>      -> com marcador [[p. N]] por página
2. BRIEF     montar_brief() do pipeline                 -> texto real da fonte + schema literal
3. GERAÇÃO   agy -p "$(cat brief)" --model gemini-3.1-pro-high --output-format json
4. MERGE     gerar_plano_html.py <plano.json> <index.html>
5. PORTÃO 1  verificar_ancoragem.py <plano.json> <pdf> <ini> <fim>   (exit 0 = passou)
6. PORTÃO 2  validate_plan.py <index.html>                           (exige [SUCESSO])
7. PUBLICA   git push
8. PORTÃO 3  portao_navegador.py <url pública>                       (exit 0 = passou)
9. AGENDA    URL do plano + do vídeo no evento da sessão
```

**Só o passo 3 é LLM.** Todo o resto é script ou verificação — ~45 k tokens e ~2 min por bloco.

### São TRÊS portões, e cada um pega o que o outro não vê

| # | portão | o que confere | o que ele NÃO vê |
|---|---|---|---|
| 1 | ancoragem | a citação existe **na página citada**? | estrutura do JSON |
| 2 | forma | 6 questões, 4 alternativas, cronograma cabe | **`topics` dos módulos**, e se a página inicia |
| 3 | navegador | **a página realmente abre e renderiza** | se o conteúdo é verdadeiro |

**Os três saem com código de saída — use o código, não a mensagem.**

**O portão 3 é o único que valida o que o Rafael vê.** Em 11/10 o plano passou nos portões 1 e 2 e
**quebrou no navegador**: o `agy` nomeou as chaves dos módulos como `contents`/`topic`/`pages` em vez de
`topics` + `source`. O `validate_plan.py` **não checa `topics`** (a palavra não existe no script), e a
auditoria de ancoragem é cega para estrutura. **O motor do template rejeitou a página inteira.**

```bash
python3 .agents/scripts/portao_navegador.py <url1> [url2 ...]
# usa o Chrome headless já de pé em 127.0.0.1:9222 (CDP); exige o venv gn (websocket-client)
/opt/data/.local/venvs/gn/bin/python .agents/scripts/portao_navegador.py <url>
```

Ele conta `.module` / `.question` / `.option` no DOM **renderizado**, exige texto visível acima de 2 000 chars
e procura mensagem de erro. **Conte com o cache do Pages:** ele serve a versão antiga por ~45–75 s depois do
push — repita até a versão nova aparecer.

## O que os portões aprenderam em 12/10/2026 (cinco defeitos no verificador)

O portão de ancoragem dava **PASSOU** sem ter examinado **nada**. Cinco causas, todas no verificador — o plano
estava certo:

1. **Cegueira a aspas duplas.** O regex procurava `'...'`; o modelo escreve `"..."`. Zero citações reconhecidas
   → `conf == len(citacoes)` vira `0 == 0` → **PASSOU vazio**. Agora exige ≥1 citação por questão.
2. **Citação conferida contra a fonte INTEIRA.** Uma frase da p. 53 sustentava questão que dizia "p. 41".
   Agora confere contra a **união das páginas citadas**.
3. **Página impressa ≠ índice do PDF.** Em PCP o índice 53 é a **página impressa 41**. Resolver página a página
   deixa buracos (página que abre com figura não casa o padrão). O deslocamento é do **documento**: cada
   cabeçalho legível vota `(indice - numero)` e vence a maioria.
4. **Brief exigia página e entregava texto corrido.** O modelo **chutava** o número (em DH errou por +1 nas seis).
   O extrator agora emite `[[p. N]]` antes de cada página.
5. **Não-caracteres da extração.** `indi\uFFFEvíduo`: o modelo cita "indivíduo" e a comparação falha. O
   normalizador remove `Cc/Cf/Co/Cn` dos dois lados.

**Extrator e verificador têm de usar a MESMA regra de numeração** — se divergirem, o portão reprova exatamente
o que o brief mandou citar. E o teste é sempre nos dois sentidos: caso ruim tem de reprovar, caso bom tem de passar.


## Modelo (medido, não suposto)

| modelo | pool | cita página | citações literais | tokens | tempo |
|---|---|---|---|---|---|
| `claude-opus-5-5-high` | Claude/GPT (menor) | 6/6 | 14/14 | 59.147 | 118 s |
| `claude-sonnet-5-5-high` | Claude/GPT (menor) | 6/6 | 7/10 | 55.052 | 60 s |
| **`gemini-3.1-pro-high`** | **Gemini (renova 5 h)** | **6/6** | **4/4** | **32.251** | **23 s** |
| `gemini-3.8-flash-high` | Gemini (renova 5 h) | 0/6 | não citou | 54.103 | 179 s |

**Default: `gemini-3.1-pro-high`.** Pool que dificilmente esgota, cita página, metade dos tokens do Claude.
Fallback: `claude-sonnet-5-5-high`. Opus só quando a citação literal for crítica.
**`gemini-3.8-flash-high` nunca para conteúdo auditável** — não citou página em nenhuma questão.

## As três regras que já falharam

1. **O brief leva o TEXTO da fonte, não o resumo dela.** A v1 usou o resumo do NotebookLM (2 linhas por tópico);
   o executor completou com conhecimento geral e escreveu sobre SPT/EDD, MTO/ATO/MTS e nível-vs-perseguição —
   **nenhum desses termos existe nas 254 páginas da apostila**.
2. **Brief headless proíbe ferramenta.** Sem *"NÃO use ferramentas; responda DIRETAMENTE"*, o modelo tenta rodar
   comando, sofre soft-deny e devolve `status: SUCCESS` com resposta vazia — ~30 k tokens perdidos.
3. **Ao conferir citação, remova cabeçalho de página do texto-fonte.** A apostila tem cabeçalho correndo no meio
   da frase; sem limpar, o conferidor acusa citação verdadeira como falsa.

## O portão valida FORMA, não VERDADE

`validate_plan.py` confere: ≥1 módulo, **exatamente 6** questões, **exatamente 4** alternativas, `answer` 0–3,
sem ID duplicado, cronograma sem sobreposição e dentro de `availableMinutes`, ≥1 vídeo com URL `https://`.

Ele **não** confere se a questão está certa, nem se o conteúdo é da apostila. Um plano com 6 questões
formosíssimas e erradas passa. **A verificação semântica é o passo 4, e é separada de propósito.**

## Consumo

`python3 .agents/scripts/agy_usage_ledger.py relatorio` — soma os envelopes do `agy`.
A cota RESTANTE não é legível headless (`/usage` é comando de barra da TUI); o que se mede é o que já queimou.
