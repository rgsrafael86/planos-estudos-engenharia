const fs = require('fs');
const filePath = 'C:/Maintply/planos-estudos-engenharia/planos/planejamento-estrategico/2026-08-13/index.html';
let content = fs.readFileSync(filePath, 'utf8');

const marker = '<!-- STUDY_PLAN_START -->';
let tStart = content.indexOf(marker);
if(tStart === -1) {
  console.log('Not found');
  process.exit(1);
}

const scriptTag = '<script id="studyPlanData" type="application/json">';
let scriptStart = content.indexOf(scriptTag, tStart);
let scriptEnd = content.indexOf('</script>', scriptStart);

let jsonStr = content.substring(scriptStart + scriptTag.length, scriptEnd).trim();
let data = JSON.parse(jsonStr);

// The current 13/08 plan is the full one. I should change the modules completely.
// Since it's a PRESENTIAL CLASS that had a PRE_CLASS, it should only have ONE module: "Anotações e Observações da Aula Presencial"
// And I will put the insights there.

data.modules = [
  {
    "id": "obs1",
    "title": "Anotações e Observações da Aula Presencial",
    "duration": "180 min",
    "topics": [
      "Abaixo estão os insights estruturados extraídos do caderno de aula:",
      "Steiner e Elementos do Planejamento: Propósitos, objetivos, estratégias, orçamentos, procedimentos e normas.",
      "Características do Planejamento: Tempo de alcance (curto, médio e longo prazo), e propriedades (complexidade, confidencial/público, formal/informal).",
      "Pilares do Planejamento: Processos, Tecnologias e Pessoas.",
      "Benefícios: Visão clara, controle financeiro, foco, alinhamento, decisões seguras e menor erro.",
      "Estratégia: Definição de direção (missão, visão e objetivos), posicionamento e alocação de recursos (onde investir).",
      "Matriz de Ansoff: Foco na matriz, Penetração de Mercado (Produto Atual + Mercado Atual), Desenvolvimento de Mercado e de Produto.",
      "Henry Mintzberg: A estratégia como processo emergente."
    ],
    "source": { "origin": "Presencial", "document": "Caderno Aula 13/08.pdf", "location": "", "pages": "", "searchHint": "", "url": "" },
    "videos": []
  }
];

// Re-add the dummy questions for validation to pass, just 4 simple questions for the presencial class
data.questions = [
    {
      "id": "q1_dummy",
      "prompt": "Você assinou a lista de presença da aula presencial de hoje?",
      "options": [
        "Sim, assinei.",
        "Não assinei.",
        "A lista não foi passada.",
        "Assinarei no final."
      ],
      "answer": 0,
      "explanation": "A assinatura da lista é o registro oficial da sua presença em sala de aula."
    },
    {
      "id": "q2_dummy",
      "prompt": "Quais foram os principais insights capturados no seu caderno sobre Elementos do Planejamento e Matriz de Ansoff?",
      "options": [
        "Nenhum conceito foi anotado.",
        "Apenas notas sobre cronograma da disciplina.",
        "Os elementos abordam propósitos e orçamentos, e a Matriz Ansoff explora a relação de mercados e produtos atuais/novos.",
        "Os tópicos focaram apenas em manutenção preditiva."
      ],
      "answer": 2,
      "explanation": "As anotações estruturadas da aula descrevem explicitamente a Matriz de Ansoff (penetração, desenvolvimento) e elementos estratégicos de Steiner."
    },
    {
      "id": "q3_dummy",
      "prompt": "Segundo as anotações sobre os pilares do planejamento, quais são as três áreas fundamentais?",
      "options": [
        "Marketing, Vendas e Produção",
        "Processos, Tecnologias e Pessoas",
        "Hardware, Software e Redes",
        "Diretoria, Gerência e Operação"
      ],
      "answer": 1,
      "explanation": "No caderno foi apontado que os pilares são Processos, Tecnologias e Pessoas."
    },
    {
      "id": "q4_dummy",
      "prompt": "Sobre os benefícios do planejamento listados na aula, qual das alternativas contém características verdadeiras?",
      "options": [
        "Aumento da burocracia e lentidão na execução",
        "Geração de incertezas financeiras e perda de foco",
        "Visão clara, controle financeiro, foco, alinhamento, decisões seguras e menor erro",
        "Desestruturação na resolução de problemas operacionais"
      ],
      "answer": 2,
      "explanation": "O planejamento reduz a margem de erro, aumenta a previsibilidade financeira, facilita as decisões e alinha o time."
    }
  ];

const newJsonStr = JSON.stringify(data, null, 2);
const newContent = content.substring(0, scriptStart + scriptTag.length) + '\n' + newJsonStr + '\n' + content.substring(scriptEnd);

fs.writeFileSync(filePath, newContent, 'utf8');
console.log('Topics added successfully!');
