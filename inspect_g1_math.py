with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

exec_idx = tmpl.find('function drawExecView')
diff_idx = tmpl.find('const diffMoM =', exec_idx)

print("--- drawExecView calculation of G1 metrics ---")
print(tmpl[exec_idx:diff_idx+200].encode('ascii', 'replace').decode('ascii'))
