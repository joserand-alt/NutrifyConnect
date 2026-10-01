import json
import re
from datetime import datetime, timedelta

with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'const DATA\s*=\s*(\{.*?\});', html, re.DOTALL)
data = json.loads(m.group(1))
students = data.get('students', [])

# Reference date in dashboard (Setembro/2026)
# Let's check what reference date is used in template.html or DATA.meta
print('DATA.meta:', data.get('meta', {}))

# Parse student dates
monthly_counts = {}
last30 = 0
prev30 = 0

ref_date = datetime(2026, 9, 14) # current dashboard date

for s in students:
    dt_str = s.get('data_insc') or s.get('data_inscricao') or s.get('inscricao')
    if dt_str:
        try:
            if '/' in dt_str:
                p = dt_str.split('/')
                dt = datetime(int(p[2] if len(p[2])==4 else '20'+p[2]), int(p[1]), int(p[0]))
            elif '-' in dt_str:
                dt = datetime.fromisoformat(dt_str[:10])
            else:
                continue
            
            ym = dt.strftime('%Y-%m')
            monthly_counts[ym] = monthly_counts.get(ym, 0) + 1
            
            diff_days = (ref_date - dt).days
            if 0 <= diff_days <= 30:
                last30 += 1
            elif 31 <= diff_days <= 60:
                prev30 += 1
        except Exception as e:
            pass

print('Monthly enrollments distribution:')
for ym in sorted(monthly_counts.keys()):
    print(f'  {ym}: {monthly_counts[ym]} matriculas')

print(f'\nUltimos 30 dias (D-30): {last30}')
print(f'30 dias anteriores (D-31 a D-60): {prev30}')
if prev30 > 0:
    growth = ((last30 - prev30) / prev30) * 100
    print(f'Crescimento: {growth:+.1f}%')
else:
    print(f'Crescimento: +100% (ou N/A)')
