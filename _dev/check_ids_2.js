const fs = require('fs');

function checkId(filePath) {
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    const scriptTag = '<script id="studyPlanData" type="application/json">';
    const scriptStart = content.indexOf(scriptTag);
    if (scriptStart !== -1) {
      const scriptEnd = content.indexOf('</script>', scriptStart);
      let jsonStr = content.substring(scriptStart + scriptTag.length, scriptEnd).trim();
      const data = JSON.parse(jsonStr);
      console.log('ID in file:', data.id);
    } else {
      console.log('No JSON found in', filePath);
    }
  } else {
    console.log('File not found:', filePath);
  }
}

console.log('14/08:');
checkId('C:/Maintply/planos-estudos-engenharia/planos/manutencao-industrial/2026-08-14/index.html');
console.log('16/08:');
checkId('C:/Maintply/planos-estudos-engenharia/planos/relacoes-etnico-raciais-e-diferentes-culturas/2026-08-16/index.html');
