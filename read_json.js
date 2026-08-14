const fs = require('fs');
const content = fs.readFileSync('C:/Maintply/planos-estudos-engenharia/planos/planejamento-estrategico/2026-08-13/index.html', 'utf8');

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
console.log(jsonStr.substring(0, 300));
