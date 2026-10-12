# TEMPLATE DO BRIEF — geração de plano de estudos

Copie este arquivo, preencha os `<<<>>>` e passe ao `agy`. **Não improvise a estrutura**: as quatro seções
existem porque cada uma já evitou um erro concreto (registrado no fim).

```
COMECE O BRIEF COM ESTA LINHA, SEMPRE:

NÃO use ferramentas (não rode comandos, não leia nem escreva arquivos). Todo o material está neste brief.
Responda DIRETAMENTE com o JSON.
```

## 1. TAREFA

Gere as questões de um plano de estudos de <<<DISCIPLINA>>> (AV<<<N>>> em <<<DATA_DA_PROVA>>>) para a UNIASSELVI.

## 2. ANCORAGEM ESTRITA — a regra que mais importa

O texto da fonte está no FINAL, entre `<<<FONTE>>>` e `<<<FIM>>>`.

**Toda questão deve ser respondível usando APENAS esse texto.** É PROIBIDO usar conhecimento geral que não
esteja no texto. Se a fonte não cobre um assunto, **não pergunte sobre ele**. Se precisar de um conceito que
o texto não traz, escolha outro ponto do texto — não invente.

## 3. CONTEÚDO DO PLANO

<<<LISTA DE MÓDULOS: para cada um, unidade/tópico + páginas + temas, extraídos do sumário da fonte>>>

## 4. SCHEMA EXATO DA RAIZ

Cole aqui o JSON da raiz (todas as chaves menos `modules` e `questions`), obtido do plano anterior ou do
template. Acrescente a instrução: *(acrescente "modules" com os módulos acima e "questions" com as 6 questões)*.

Campos que o portão exige não-vazios: `id`, `title`, `discipline`, `studyDate`, `objective`.
`student` deve ser exatamente `"R.G."` — nunca o nome completo.

### 4-bis. SCHEMA DOS MÓDULOS — cole LITERALMENTE, não descreva

**Este bloco existe porque um modelo renomeou as chaves e o plano não abriu no navegador.** Ele escreveu
`contents` no lugar de `topics`, e `unit`/`topic`/`pages` soltos no lugar de `source`. O conteúdo estava
certo; a chave, errada — e o motor do template rejeitou com *"Módulo m1 sem tópicos"*.

```json
"modules": [
  {
    "id": "m1",
    "title": "string",
    "duration": "55 min",
    "topics": ["string", "string"],
    "source": {"origin":"string","document":"string","location":"string","pages":"3–22","searchHint":"string","url":""},
    "videos": [{"title":"string","url":"https://www.youtube.com/results?search_query=..."}]
  }
]
```

**`topics` é LISTA e o nome é `topics`.** Não use `contents`, `topic`, `conteudos` nem `tópicos`.
Não invente chaves fora desta lista — o motor valida contra ela e **bloqueia a página inteira**.

## 5. AS QUESTÕES — exatamente 6

```json
{"id":"qN","prompt":"...","options":["...","...","...","..."],"answer":0,"explanation":"..."}
```

- `answer` é o **índice** (0 a 3) da alternativa correta.
- **`explanation` deve CITAR o trecho e a página da fonte que sustenta a resposta** — ex.: *"Conforme a p. 14, ..."*.
  Sem citação, a questão é considerada **não ancorada** e o passo de auditoria reprova.
- **Distribua as respostas entre A, B, C e D.** (Um modelo entregou A:3 B:2 C:1 D:0 — a alternativa D nunca
  era a correta, e isso é um vício detectável.)
- Nível de AV: aplicação e compreensão, não decoreba. Distratores plausíveis, errados por motivo identificável.

## 6. VÍDEOS — não deixe o modelo escolher links fixos

Cada módulo leva **pelo menos 1 vídeo**, com **URL de busca dinâmica** do YouTube (nunca link/ID fixo):

```
https://www.youtube.com/results?search_query=termo+especifico+do+modulo
```

A busca deve ser específica e alinhada ao tema do módulo. **Verifique depois**: a URL precisa devolver
resultados (`videoRenderer` na resposta) e os títulos precisam ser do tema.

## 7. SAÍDA

Apenas o JSON da raiz, começando com `{` e terminando com `}`. Sem cercas de código, sem comentário,
sem texto antes ou depois.

---

## COMO MONTAR A FONTE (seção final do brief)

```bash
# 1. extraia o TEXTO REAL das páginas — nunca use o resumo do NotebookLM
python3 .agents/scripts/extrair_apostila.py <pdf> <pagina_ini> <pagina_fim> fonte.txt

# 2. embuta o conteúdo de fonte.txt entre <<<FONTE>>> e <<<FIM>>>
```

## POR QUE CADA SEÇÃO EXISTE — os erros que ela evita

| seção | erro que já aconteceu |
|---|---|
| linha inicial proibindo ferramenta | sem ela o modelo tentou rodar comando, sofreu soft-deny e devolveu `SUCCESS` com **resposta vazia** — 30 k tokens perdidos |
| ancoragem estrita + fonte embutida | a v1 usou o **resumo** do NotebookLM (2 linhas/tópico); o executor completou com conhecimento geral e escreveu sobre SPT/EDD, MTO/ATO/MTS e nível-vs-perseguição — **nenhum desses termos existe nas 254 páginas da apostila** |
| citação de página obrigatória | sem ela não há como provar ancoragem; o `gemini-3.8-flash-high` entregou 6 questões corretas e **zero citações** — inauditável |
| distribuir as respostas | um plano saiu com A:3 B:2 C:1 **D:0** |
| `student` = `R.G.` | um plano saiu com o nome completo e reprovou no portão |

## MODELO

```
agy -p "$(cat brief.txt)" --model gemini-3.1-pro-high --output-format json
```

Default `gemini-3.1-pro-high` (pool que dificilmente esgota, cita página 6/6, ~32 k tokens, ~23 s).
Fallback `claude-sonnet-5-5-high`. Opus só quando a citação literal for crítica.
**`gemini-3.8-flash-high` nunca para conteúdo auditável.**
