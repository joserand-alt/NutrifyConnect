import json
import re

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vc = json.load(f)

v_data = vc.get('data', {})

def parse_plan_cycles(plano_str):
    if not plano_str: return 12
    s = str(plano_str).upper()
    m = re.search(r'(\d+)\s*X', s)
    if m:
        return int(m.group(1))
    if 'ANUAL' in s or '12M' in s: return 12
    if 'SEMESTRAL' in s or '6M' in s: return 6
    if 'TRIMESTRAL' in s or '3M' in s: return 3
    if 'MENSAL' in s or '1M' in s: return 12 # Recurring continuous
    return 12

plan_counts = {}
for em, s in v_data.items():
    if isinstance(s, dict) and s.get('has_vindi'):
        p = s.get('plano') or 'Sem Plano'
        cycles = parse_plan_cycles(p)
        plan_counts[p] = (plan_counts.get(p, (0, cycles))[0] + 1, cycles)

print("=== VINDI PLAN CYCLES BREAKDOWN ===")
for p, (cnt, cyc) in sorted(plan_counts.items(), key=lambda x: x[1][0], reverse=True):
    print(f"- {p} ({cnt} subs) -> {cyc} ciclos")
