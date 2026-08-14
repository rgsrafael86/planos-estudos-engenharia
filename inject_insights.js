const fs = require('fs');
const filePath = 'C:/Maintply/planos-estudos-engenharia/planos/planejamento-estrategico/2026-08-13/index.html';
let content = fs.readFileSync(filePath, 'utf8');

const scriptTag = '<script id="studyPlanData" type="application/json">';
let tStart = content.indexOf(scriptTag);
if(tStart === -1) {
  const startTagLF = '<!-- STUDY_PLAN_START -->\n<script id="studyPlanData" type="application/json">';
  tStart = content.indexOf(startTagLF);
}
if(tStart === -1) {
  console.log('Not found');
  process.exit(1);
}

let tEnd = content.indexOf('</script>', tStart + scriptTag.length);
let jsonStr = content.substring(tStart + scriptTag.length, tEnd).trim();
let data = JSON.parse(jsonStr);

data.modules[0].topics = [
  "Steiner e Elementos do Planejamento: Propósitos, objetivos, estratégias, orçamentos, procedimentos e normas.",
  "Características do Planejamento: Tempo de alcance (curto, médio e longo prazo), e propriedades (complexidade, confidencial/público, formal/informal).",
  "Pilares do Planejamento: Processos, Tecnologias e Pessoas.",
  "Benefícios: Visão clara, controle financeiro, foco, alinhamento, decisões seguras e menor erro.",
  "Estratégia: Definição de direção (missão, visão e objetivos), posicionamento e alocação de recursos (onde investir).",
  "Matriz de Ansoff: Foco na matriz, Penetração de Mercado (Produto Atual + Mercado Atual), Desenvolvimento de Mercado e de Produto.",
  "Henry Mintzberg: A estratégia como processo emergente."
];

const newJsonStr = JSON.stringify(data, null, 2);
const newContent = content.substring(0, tStart + scriptTag.length) + '\n' + newJsonStr + '\n' + content.substring(tEnd);

fs.writeFileSync(filePath, newContent, 'utf8');
console.log('Topics added successfully!');
