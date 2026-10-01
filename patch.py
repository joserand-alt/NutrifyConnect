import sys
code = open('template.html', encoding='utf-8').read()
code = code.replace("if (topChip) topChip.textContent = `${matInfo.count24h} matrículas (48h) ⚡`;", "if (topChip) topChip.textContent = `${matInfo.count24h} Conf. | ${matInfo.countPendentes24h} Pend. (48h) ⚡`;")
open('template.html', 'w', encoding='utf-8').write(code)
