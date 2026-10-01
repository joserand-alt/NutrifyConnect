import sys
code = open('template.html', encoding='utf-8').read()

old_v = "const vindiActive = s.vindi && (s.vindi.status_assinatura === 'active' || s.vindi.status_financeiro === 'adimplente');"
new_v = "const vindiActive = s.vindi && (s.vindi.status_assinatura === 'active');"

old_a = "const asaasActive = s.asaas && (s.asaas.status_assinatura === 'active' || s.asaas.status_financeiro === 'adimplente' || s.asaas.status_financeiro === 'pago');"
new_a = "const asaasActive = s.asaas && (s.asaas.status_assinatura === 'active');"

old_v2 = "const vindiActive = vSt === 'active' || vSt === 'ativo' || vSt === 'adimplente' || vSt === 'em_dia';"
new_v2 = "const vindiActive = vSt === 'active' || vSt === 'ativo';"

old_a2 = "const asaasActive = aSt === 'active' || aSt === 'ativo' || aSt === 'received' || aSt === 'confirmed' || aSt === 'adimplente' || aSt === 'em_dia';"
new_a2 = "const asaasActive = aSt === 'active' || aSt === 'ativo' || aSt === 'received' || aSt === 'confirmed';"

code = code.replace(old_v, new_v)
code = code.replace(old_a, new_a)
code = code.replace(old_v2, new_v2)
code = code.replace(old_a2, new_a2)

open('template.html', 'w', encoding='utf-8').write(code)
