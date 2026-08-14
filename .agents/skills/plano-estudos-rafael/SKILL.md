---
name: plano-estudos-rafael
description: Gera, valida, salva e registra planos diários interativos de Engenharia de Produção de Rafael. Use quando a solicitação envolver aula, pré-aula, revisão, simulado, cronograma acadêmico, NotebookLM, vídeo didático, template HTML blindado, publicação pelo Web App ou registro do plano no documento entre agentes. Não use para triagem de e-mails, finanças, programação de projetos ou organização geral sem entrega de plano acadêmico.
---

# Plano de Estudos de Rafael

## Objetivo
Produzir um plano acadêmico diário baseado na agenda real e nas fontes do NotebookLM, usando o template oficial blindado. O agente gera somente o JSON autorizado, nunca reescreve o motor HTML.

## Contexto essencial
- Idioma: português brasileiro.
- Fuso: America/Sao_Paulo.
- Curso: Engenharia de Produção, 6º semestre, UNIASSELVI.
- Aulas presenciais habituais: segunda Automação Industrial; quinta Planejamento Estratégico; sexta Manutenção Industrial.
- Disciplinas online: PCP e transversais.
- Expediente CLT habitual: segunda a sexta, 05:00–14:40.
- Estudante exibido no plano compartilhável: `R.G.`.

## Recursos oficiais
- Template local: `templates/template_blindado.html`, ou versão oficial mais recente identificada como `RAFAEL-STUDY-ENGINE`.
- Motor esperado: `RAFAEL-STUDY-ENGINE v3.0.0`.
- URL-base do Web App:
  `https://script.google.com/macros/s/AKfycbw9h4zoSrCRUYA0XpZt1uoBZePNPeSz5I1-RPqpR2HmrDt0Xbz9Tbo-gDTJ1ie2q4qt/exec`
- Documento Comunicação entre Agentes:
  ID `1yRCWcQxPpMV7zYsqu4gJgiJ8JydD3Ks_2z0AXndrBlE`.

## Fluxo obrigatório
1. Consultar o Google Agenda para as próximas 24 horas.
2. Identificar aula, pré-aula, revisão, trabalho ou prova.
3. Calcular a janela real, preservando transição entre compromissos.
4. Consultar o NotebookLM da disciplina.
5. Selecionar conteúdo compatível com o tempo.
6. Pesquisar vídeos apenas quando agregarem valor.
7. Copiar o template oficial e substituir somente o JSON dentro de `studyPlanData`, entre `STUDY_PLAN_START` e `STUDY_PLAN_END`.
8. Validar JSON, cronograma, módulos, vídeos, questões e motor.
9. Salvar como HTML puro no Drive.
10. Abrir pelo Web App, efetuar teste funcional e registrar no documento entre agentes.

## Regra crítica do template
Edite somente:

```html
<!-- STUDY_PLAN_START -->
<script id="studyPlanData" type="application/json">
{ ... JSON válido ... }
</script>
<!-- STUDY_PLAN_END -->
```

Nunca altere HTML estrutural, CSS, JavaScript, KaTeX, IDs, progresso, resultado, reinício, impressão, tema, validação ou versão do motor.

## Agenda e cronograma
- Use `HH:MM` em 24 horas.
- Não invente horários.
- `availableMinutes` é inteiro.
- Itens devem estar ordenados, sem sobreposição e dentro da janela.
- A duração dos vídeos precisa aparecer no cronograma.
- Quantidade de conteúdo deve caber no tempo real.

## Fontes
Cada módulo precisa de `source` com:
- `origin`
- `document`
- `location`
- `pages`
- `searchHint`
- `url`

Não invente páginas, capítulos, autores ou links. Deixe vazio o que não estiver confirmado. Metadados internos não devem aparecer na notificação ao usuário.

## Vídeos
- Até 1 vídeo por módulo e no máximo 3 por sessão.
- `videos` deve ser sempre uma lista; use `[]` se não houver vídeo adequado.
- Confirmar título, canal, duração, URL, trecho e relevância.
- O vídeo precisa caber na agenda.
- `verificationStatus` deve ficar vazio quando aprovado e conter texto apenas para pendência real.

## Questões
- Até 30 min: 4 a 6.
- 31 a 60 min: 6 a 8.
- 61 a 90 min: 8 a 12.
- Acima de 90 min: 10 a 15.
- Cada questão deve ter ID único, enunciado, quatro alternativas, índice `answer` entre 0 e 3 e explicação.
- Somente uma alternativa correta.
- Não escrever letras nas alternativas.
- Combinar recordação, compreensão, aplicação e análise.
- Exibir percentual final de acertos.

## Fórmulas
- Use Unicode para fórmulas simples quando suficiente.
- Use LaTeX entre `$...$` ou `$$...$$` para fórmulas complexas.
- No JSON, duplique barras invertidas, por exemplo: `$MTTR = \\frac{T}{N}$`.
- Não altere a configuração do KaTeX.

## Gravação no Drive
- Caminho: `Estudos - Engenharia de Produção/[Disciplina]/Planos Diários/`.
- Nome: `AAAA-MM-DD_Disciplina_Assunto.html`.
- MIME: `text/html`.
- UTF-8 e início `<!DOCTYPE html>`.
- Nunca converter para Google Docs, DOCX, XML ou PDF.
- Não usar DocsApp para o plano.
- URL final: `URL_BASE?id=ID_DO_ARQUIVO`.

## Validação obrigatória
Só publicar após confirmar:
- JSON válido;
- motor e versão preservados;
- IDs únicos;
- cronograma válido;
- no mínimo 1 módulo e 4 questões;
- quatro alternativas por questão;
- links de vídeo HTTPS;
- renderização sem duplicidade;
- uma resposta gera feedback e aumenta o progresso;
- todas as respostas liberam o resultado;
- reinício retorna a zero;
- URL do Web App abre.

Se qualquer teste falhar, registrar falha e não publicar como plano pronto.

## Registro no documento entre agentes
Inserir no topo de `MENSAGENS`, sem editar entradas anteriores:

```text
[GEMINI SPARK] | DD/MM/AAAA HH:MM | Status | Plano diário criado
ID: SPARK-[DISCIPLINA]-AAAAMMDD-001
Disciplina: ...
Status: Plano criado e validado
Arquivo: ...
URL: ...
Template: RAFAEL-STUDY-ENGINE v3.0.0
Módulos: N
Questões: N
Vídeos: N
Validação: aprovada
Autorização necessária: Não
```

## Notificação limpa
```text
♻️ PLANO DE ESTUDOS
📘 Disciplina: <disciplina>
📅 Data: <DD/MM/AAAA (dia da semana)>
⏰ Horário: <HH:MM–HH:MM>
🎯 Tópicos: <tópicos>
📺 Vídeos: <N> vídeos
❓ Questões: <N> questões
🔗 Link: <somente URL do Web App>
```

Não mostrar link direto do Drive, MIME, ID técnico, teste 200 OK ou notas internas.
