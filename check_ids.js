const fs = require('fs');
const filePath = 'C:/Maintply/planos-estudos-engenharia/planos/manutencao-industrial/2026-08-14/index.html';
const content = fs.readFileSync(filePath, 'utf8');
const scriptTag = '<script id="studyPlanData" type="application/json">';
const scriptStart = content.indexOf(scriptTag);
const scriptEnd = content.indexOf('</script>', scriptStart);
let jsonStr = content.substring(scriptStart + scriptTag.length, scriptEnd).trim();
const data = JSON.parse(jsonStr);
console.log('14/08 Manutencao Industrial ID:', data.id);

const filePath16 = 'C:/Maintply/planos-estudos-engenharia/planos/relacoes-etnico-raciais/2026-08-16/index.html';
if (fs.existsSync(filePath16)) {
  const content16 = fs.readFileSync(filePath16, 'utf8');
  const scriptStart16 = content16.indexOf(scriptTag);
  const scriptEnd16 = content16.indexOf('</script>', scriptStart16);
  let jsonStr16 = content16.substring(scriptStart16 + scriptTag.length, scriptEnd16).trim();
  const data16 = JSON.parse(jsonStr16);
  console.log('16/08 Relacoes ID:', data16.id);
} else {
  console.log('16/08 Relacoes DOES NOT EXIST');
}
