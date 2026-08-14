const fs = require('fs');
const filePath = 'C:/Maintply/planos-estudos-engenharia/planos/planejamento-estrategico/2026-08-12/index.html';
let content = fs.readFileSync(filePath, 'utf8');

const marker = '<!-- STUDY_PLAN_START -->';
let tStart = content.indexOf(marker);
const scriptTag = '<script id="studyPlanData" type="application/json">';
let scriptStart = content.indexOf(scriptTag, tStart);
let scriptEnd = content.indexOf('</script>', scriptStart);

let jsonStr = content.substring(scriptStart + scriptTag.length, scriptEnd).trim();
let data = JSON.parse(jsonStr);

data.id = "planejamento-estrate-gico-2026-08-12-1700";
data.studyDate = "12 de Agosto de 2026";
data.scheduledStart = "17:00";
data.scheduledEnd = "17:50";
data.availableMinutes = 50;

// The schedule array must also be updated to fit 17:00 - 17:50 (50 min)
data.schedule = [
  {
    "start": "17:00",
    "end": "17:05",
    "duration": "5m",
    "activity": "Leitura do material pré-aula e organização do ambiente."
  },
  {
    "start": "17:05",
    "end": "17:35",
    "duration": "30m",
    "activity": "Estudo dos módulos teóricos de Estrutura Organizacional."
  },
  {
    "start": "17:35",
    "end": "17:50",
    "duration": "15m",
    "activity": "Resolução do simulado teórico (6 questões)."
  }
];

const newJsonStr = JSON.stringify(data, null, 2);
const newContent = content.substring(0, scriptStart + scriptTag.length) + '\n' + newJsonStr + '\n' + content.substring(scriptEnd);

fs.writeFileSync(filePath, newContent, 'utf8');

// Now update agenda_semestre.json to set VALIDATED and the URL for 12/08
const agendaPath = 'g:/Meu Drive/Engenharia_de_Producao_UNIASSELVI/agenda_semestre.json';
const agenda = JSON.parse(fs.readFileSync(agendaPath, 'utf8'));
const session = agenda.sessions.find(s => s.session_id === data.id);
if (session) {
  session.plan_status = "VALIDATED";
  session.plan_url = "https://rgsrafael86.github.io/planos-estudos-engenharia/planos/planejamento-estrategico/2026-08-12/index.html";
  session.plan_validation = "APPROVED";
  fs.writeFileSync(agendaPath, JSON.stringify(agenda, null, 2), 'utf8');
  console.log('Updated agenda_semestre.json');
}

console.log('Fixed 12/08 plan!');
