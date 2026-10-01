import json
import re

def is_checkout_event(ev):
    if not ev:
        return False
    cat = (ev.get('categoria') or '').lower()
    raw = (ev.get('evento_raw') or '').lower()
    clean = (ev.get('evento_clean') or '').lower()
    if 'checkout' in cat or 'matrícula' in cat or 'matricula' in cat:
        return True
    if any(k in raw for k in ['checkout', 'pago', 'pendente', 'recorrencia', 'compra', 'problema', 'pagamento']):
        return True
    if any(k in clean for k in ['checkout', 'pagamento', 'compra']):
        return True
    return False

def is_checkout_string(s):
    if not s:
        return False
    low = str(s).lower()
    return any(k in low for k in ['checkout', 'pagamento', 'pago', 'pendente', 'recorrencia', 'compra', 'problema'])

# Test on extracted DATA
with open('extracted_data.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx_start = text.find('const DATA = {')
idx_end = text.rfind('};')
data_json = text[len('const DATA = '):idx_end+1]
data = json.loads(data_json)

removed_events = 0
cleaned_students = 0
students = data.get('students', [])

for s in students:
    rd = s.get('rd_funnel')
    if rd:
        evs_det = rd.get('eventos_detalhados', [])
        evs_fmt = rd.get('eventos', [])
        
        new_det = [e for e in evs_det if not is_checkout_event(e)]
        new_fmt = [e for e in evs_fmt if not is_checkout_string(e)]
        
        diff = len(evs_det) - len(new_det)
        if diff > 0:
            removed_events += diff
            cleaned_students += 1
            rd['eventos_detalhados'] = new_det
            rd['eventos'] = new_fmt
            rd['conversoes_antes'] = len(new_det)
            if new_det and new_det[0].get('data'):
                rd['dt_primeira'] = new_det[0]['data']
            elif not new_det:
                rd['dt_primeira'] = '—'
                rd['dias_venda'] = ''

print(f"Total students: {len(students)}")
print(f"Students with checkout events cleaned: {cleaned_students}")
print(f"Total checkout events removed: {removed_events}")
