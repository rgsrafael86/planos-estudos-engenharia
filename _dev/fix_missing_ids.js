const fs = require('fs');

function fixId(filePath, correctId) {
  const content = fs.readFileSync(filePath, 'utf8');
  const scriptTag = '<script id="studyPlanData" type="application/json">';
  const scriptStart = content.indexOf(scriptTag);
  const scriptEnd = content.indexOf('</script>', scriptStart);
  
  let jsonStr = content.substring(scriptStart + scriptTag.length, scriptEnd).trim();
  const data = JSON.parse(jsonStr);
  
  data.id = correctId;
  
  const newJsonStr = JSON.stringify(data, null, 2);
  const newContent = content.substring(0, scriptStart + scriptTag.length) + '\n' + newJsonStr + '\n' + content.substring(scriptEnd);
  
  fs.writeFileSync(filePath, newContent, 'utf8');
  console.log('Fixed', correctId);
}

fixId('C:/Maintply/planos-estudos-engenharia/planos/manutencao-industrial/2026-08-14/index.html', 'manutencao-industrial-2026-08-14-1850');
fixId('C:/Maintply/planos-estudos-engenharia/planos/relacoes-etnico-raciais-e-diferentes-culturas/2026-08-16/index.html', 'relacoes-etnico-raciais-e-diferentes-culturas-2026-08-16-1430');
