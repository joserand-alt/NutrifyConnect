with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('function computeUnifiedFinancialDataset')
idx2 = text.find('function fM(val)', idx1)
code = text[idx1:idx2]
print('computeUnifiedFinancialDataset length:', len(code))
print('Has parsePlanCycles:', 'parsePlanCycles' in code)
print('Has totalCycles = 6:', 'totalCycles = 6' in code)

idx_curso = text.find('function drawCursoView')
print('drawCursoView index:', idx_curso)

# Check all occurrences of computeUnifiedFinancialDataset in index.html
import re
matches = [m.start() for m in re.finditer(r'function computeUnifiedFinancialDataset', text)]
print('All declarations of computeUnifiedFinancialDataset:', matches)
