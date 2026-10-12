# Esteira de planos de estudo — como um plano nasce

Documento de operação. Escrito em 11/10/2026, depois de a v1 do plano de PCP ir ao ar **desancorada**
e só ser pega porque o Rafael perguntou *"você verificou?"*.

## O fluxo (7 passos, 1 run de LLM)

```
1. FONTE     .agents/scripts/extrair_apostila.py <pdf> <ini> <fim> fonte.txt
2. BRIEF     .agents/templates/brief_plano.md   -> copie, preencha os <<<>>> e embuta a fonte
3. GERAÇÃO   agy -p "$(cat brief)" --model gemini-3.1-pro-high --output-format json
4. AUDITORIA .agents/scripts/verificar_ancoragem.py <plano.json> <pdf> <ini> <fim>   (exit 0 = passou)
5. MERGE     .agents/scripts/gerar_plano_html.py <plano.json> <saida/index.html>
6. PORTÃO    .agents/scripts/validate_plan.py <saida/index.html>                      (exige [SUCESSO])
7. NAVEGADOR abrir a página e conferir que ela INICIA  <-- o portão que faltava
8. PUBLICA   git push + update_index.py + URL no evento da agenda
```

**Só o passo 3 é LLM.** Os outros sete são scripts ou verificação — por isso o custo por bloco é ~32 k tokens e ~23 s.

### São TRÊS portões, e cada um pega o que o outro não vê

| # | portão | o que confere | o que ele NÃO vê |
|---|---|---|---|
| 4 | ancoragem | a citação existe na fonte? | estrutura do JSON |
| 6 | forma | 6 questões, 4 alternativas, cronograma cabe | **`topics` dos módulos**, e se a página inicia |
| 7 | navegador | **a página realmente abre** (roda o validador do próprio template) | se o conteúdo é verdadeiro |

**O passo 7 é o único que valida o que o Rafael vê.** Em 11/10 o plano passou nos passos 4 e 6 e
**quebrou no navegador**: o `agy` nomeou as chaves dos módulos como `contents`/`topic`/`pages` em vez de
`topics` + `source`. O `validate_plan.py` **não checa `topics`** (a palavra não existe no script), e a
auditoria de ancoragem é cega para estrutura. **O motor do template rejeitou a página inteira.**

**Como rodar o passo 7:** abrir a página (`file://` antes de publicar, a URL pública depois), esperar o JS
rodar e conferir que `fatalError` está oculto, `appMain` visível e os módulos renderizados.
**Publique e teste a URL pública — e conte com o cache:** nas primeiras tentativas o Pages ainda serve a
versão antiga (levou ~45 s e 3 tentativas em 11/10). Use `?cb=<timestamp>` e repita até a versão nova aparecer.


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
