---
name: gerador-planos-antigravity
description: Usa agenda_semestre.json e os notebooks do NotebookLM para distribuir a ementa, gerar, testar e publicar planos interativos no GitHub Pages. Atualiza somente os campos acadêmicos e de publicação de cada sessão, preservando os dados originados no Google Agenda.
---

# Gerador de Planos no Antigravity

## Objetivo

Gerar planos de estudos confiáveis e progressivos usando:

1. `agenda_semestre.json` como calendário acadêmico oficial;
2. NotebookLM como fonte oficial da ementa, materiais e continuidade;
3. template HTML oficial como motor visual;
4. navegador integrado para testes;
5. GitHub Pages como canal de publicação.

## Arquivos oficiais

- Agenda: `agenda_semestre.json`
- Template: `Template plano de estudos blindado completo.html`
- Registro opcional de publicação: `planos_publicados.json`
- Repositório recomendado: `planos-estudos-engenharia`

## Princípio de propriedade dos dados

O Antigravity trabalha no mesmo `agenda_semestre.json`, mas não é proprietário dos campos importados do Google Agenda.

### Campos somente leitura, mantidos pelo Gemini Spark

- `session_id`
- `calendar_event_id`
- `recurring_event_id`
- `original_start`
- `date`
- `day_of_week`
- `discipline`
- `discipline_slug`
- `start`
- `end`
- `available_minutes`
- `session_type`
- `location`
- `original_description`
- `academic_cycle`

O Antigravity nunca deve apagar, renomear ou alterar esses campos.

### Campos que o Antigravity pode atualizar

- `plan_status`
- `plan_url`
- `plan_generated_at`
- `plan_validation`
- `content_status`
- `notebook_name`
- `notebook_id`
- `sources_used`
- `previous_content`
- `current_content`
- `next_content`
- `learning_objective`
- `modules_count`
- `questions_count`
- `videos_count`
- `published_commit`
- `validation_report`
- `error`

O Antigravity deve fazer merge por `session_id`, preservando todos os campos desconhecidos.

## Uso do NotebookLM

Para cada disciplina:

1. localize o notebook correto;
2. use somente as fontes do notebook;
3. leia a ementa e o histórico disponível;
4. conte as sessões futuras daquela disciplina no semestre;
5. identifique avaliações N1, N2 e exame final;
6. distribua a ementa entre as sessões disponíveis;
7. reserve sessões próximas das avaliações para revisão e simulado;
8. evite repetição sem finalidade pedagógica;
9. selecione conteúdo compatível com a duração da sessão.

Se o notebook não for encontrado ou não possuir fontes suficientes, marque:

```text
plan_status: FAILED
content_status: BLOCKED
error: descrição objetiva
```

Não use conhecimento geral como substituto.

## Planejamento da ementa

Antes de gerar o primeiro plano de uma disciplina, produza um mapa interno com:

- unidades e tópicos da ementa;
- pré-requisitos;
- sessões disponíveis antes da N1;
- sessões entre N1 e N2;
- sessões após N2;
- revisões e simulados;
- conteúdo previsto por sessão.

O mapa deve ser recalculado quando:

- a Agenda mudar;
- uma sessão for cancelada;
- uma avaliação mudar de data;
- Rafael marcar conteúdo como concluído ou pendente;
- fontes relevantes forem adicionadas ao notebook.

## Seleção de sessões

Processe somente sessões com:

```text
plan_status: PENDING
```

ou sessões explicitamente marcadas para regeneração:

```text
plan_status: FAILED
```

Não gere plano para avaliações, encerramentos ou sessões `SKIPPED`, salvo instrução explícita.

Não altere automaticamente para `COMPLETED`. Esse status depende de confirmação de Rafael.

## Geração do conteúdo

Para cada sessão elegível:

1. use data, horário e duração do `agenda_semestre.json`;
2. consulte a continuidade no NotebookLM;
3. defina objetivo, módulos, fontes, vídeos (OBRIGATÓRIO: encontre e inclua pelo menos 1 vídeo relevante e verificado do YouTube sobre o tema, mesmo que o NotebookLM não forneça links. Busque ativamente para enriquecer a aula) e questões (OBRIGATÓRIO: gere exatamente 6 questões de múltipla escolha);
4. ajuste o volume ao tempo disponível;
5. use `R.G.` como estudante;
6. não exponha URLs privadas do NotebookLM ou Google Drive;
7. não inclua conteúdo demonstrativo.

## Compatibilidade e normalização

Aceite dados acadêmicos com campos equivalentes:

- `prompt`, `enunciado` ou `pergunta`;
- `options`, `alternatives` ou `alternativas`;
- `start` e `end`, ou `time` no formato `HH:MM-HH:MM`;
- duração numérica ou textual;
- ausência de `videos`, convertendo para `[]`.

Normalize sem alterar o significado acadêmico.

## Template

Use o template oficial e preserve o motor.

Substitua somente o conteúdo JSON do elemento:

```html
<script id="studyPlanData" type="application/json">
```

entre:

```text
STUDY_PLAN_START
STUDY_PLAN_END
```

Não altere HTML estrutural, CSS, JavaScript, KaTeX, progresso, resultado, reinício, impressão ou tema, exceto em uma tarefa explícita de manutenção do template.

## Validação dos dados

Bloqueie a geração quando houver:

- JSON inválido;
- conteúdo demonstrativo;
- menos de um módulo;
- menos de seis questões (Obrigatório possuir exatamente 6 questões);
- questão sem quatro alternativas;
- `answer` fora de 0 a 3;
- IDs duplicados;
- cronograma fora da sessão;
- módulos sem tópicos;
- questão sem explicação;
- ausência de vídeos (é obrigatório ter pelo menos 1 vídeo sobre os temas da aula);
- URL de vídeo insegura;
- conteúdo incompatível com a disciplina.

## Testes no navegador

Antes de publicar, teste:

1. carregamento da página;
2. título e disciplina;
3. módulos e fontes;
4. quantidade de questões;
5. quatro alternativas por questão;
6. clique em uma alternativa;
7. feedback;
8. progresso;
9. resultado final;
10. reinício;
11. responsividade básica;
12. ausência de conteúdo duplicado ou demonstrativo.

Não publique se qualquer teste falhar.

## Testes Prévios (Pré-commit)

Antes de realizar o `git push` para publicar o plano, você **DEVE OBRIGATORIAMENTE** executar o script de validação para garantir a integridade dos dados JSON do plano:
```bash
python .agents/scripts/validate_plan.py <caminho_do_index.html_gerado>
```
Se o script retornar `[FALHA NA VALIDACAO]`, você não tem permissão para prosseguir. Corrija o plano até o script retornar `[SUCESSO]`.

## Publicação no GitHub Pages

Publique cada plano em:

```text
planos/[discipline_slug]/[date]/index.html
```

URL esperada:

```text
https://rgsrafael86.github.io/planos-estudos-engenharia/planos/[discipline_slug]/[date]/
```

Após o deploy, abra e teste a URL pública. Teste local não equivale a validação pública.

## Atualização de agenda_semestre.json

### Ao iniciar

```text
plan_status: GENERATING
content_status: IN_PROGRESS
error: ""
```

### Após publicar, antes de validar a URL pública

```text
plan_status: PUBLISHED
content_status: READY
```

### Após validar a URL pública

```text
plan_status: VALIDATED
content_status: READY
plan_url: URL pública
plan_generated_at: timestamp ISO
plan_validation: APPROVED
```

Preencha também:

- `notebook_name`
- `notebook_id`, quando disponível;
- `sources_used`
- `previous_content`
- `current_content`
- `next_content`
- `learning_objective`
- `modules_count`
- `questions_count`
- `videos_count`
- `published_commit`
- `validation_report`

### Em falha

```text
plan_status: FAILED
plan_validation: REPROVED
plan_url: ""
error: descrição objetiva
```

Nunca deixe `VALIDATED` quando a URL pública não tiver sido testada.

## Concorrência e gravação segura

Antes de salvar `agenda_semestre.json`:

1. releia a versão mais recente do arquivo;
2. encontre a sessão por `session_id`;
3. preserve os campos do Google Agenda;
4. aplique somente os campos permitidos;
5. escreva em arquivo temporário;
6. valide o JSON;
7. substitua o arquivo principal de forma atômica;
8. confirme que nenhuma sessão foi perdida.

Se o arquivo tiver sido alterado durante o processamento, refaça o merge. Não sobrescreva cegamente.

## Resultado

Ao concluir, informe somente:

```text
Sessão processada:
Disciplina:
NotebookLM consultado:
Fontes utilizadas:
Conteúdo atual:
Próximo conteúdo:
HTML gerado:
URL pública:
Testes:
Status gravado na agenda:
Erro:
```

## Troubleshooting
Caso a autenticacao do NotebookLM expire (Auth tokens were reloaded from disk but are no longer valid), o usuario deve executar o comando de login no terminal:
`C:\Users\rgsra\AppData\Local\Python\pythoncore-3.14-64\Scripts\nlm.exe login`
