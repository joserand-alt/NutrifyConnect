import json

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos_c = html.find('"curriculum":')
pos_s = html.find('"students":', pos_c)
raw = html[pos_c + 13 : pos_s].strip().rstrip(',')
curric = json.loads(raw)
print('Total courses in curriculum:', len(curric))
for k in sorted(curric.keys()):
    print('COURSE:', k)
