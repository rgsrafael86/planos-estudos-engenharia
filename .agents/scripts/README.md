# Esteira de planos de estudo — como um plano nasce

Documento de operação. Escrito em 11/10/2026, depois de a v1 do plano de PCP ir ao ar **desancorada**
e só ser pega porque o Rafael perguntou *"você verificou?"*.

## O fluxo (7 passos, 1 run de LLM)

```
1. FONTE     .agents/scripts/extrair_apostila.py   -> texto real do PDF (NÃO o resumo do Notebook)
2. BRIEF     (montado à mão)                        -> fonte + schema + regras do portão + proibição de ferramenta
3. GERAÇÃO   agy -p "$(cat brief)" --model gemini-3.1-pro-high --output-format json
4. AUDITORIA .agents/scripts/verificar_ancoragem.py -> cada citação literal conferida contra o PDF
5. MERGE     .agents/scripts/gerar_plano_html.py    -> injeta o JSON no template (determinístico)
6. PORTÃO    .agents/scripts/validate_plan.py       -> tem de devolver [SUCESSO]
7. PUBLICA   git push + update_index.py + URL no evento da agenda
```

**Só o passo 3 é LLM.** Os outros seis são scripts — por isso o custo por bloco é ~32 k tokens e ~23 s.

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
