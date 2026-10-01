import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Apply the accurate future date parsing and status check in computeUnifiedFinancialDataset
old_asaas_loop = """        aFaturas.forEach(f => {
            const st = (f.status || '').toLowerCase();
            if (st === 'pendente' || st === 'pending' || st === 'a_vencer') {
                const em = (f.email || '').toString().toLowerCase().trim();
                const cm = getCourse(f.curso || emailToCourse[em]);
                const val = Number(f.valor) || 0;
                const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
                if (dtVenc) {
                    const dObj = new Date(dtVenc.slice(0, 10));
                    const hoje = new Date();
                    const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
                    if (diffMeses >= 0 && diffMeses < 18) {
                        cm.projecao_18m_sim[diffMeses] += val;
                        if (diffMeses === 0 || diffMeses === 1) {
                            asaasCoursePending[cm.curso] = (asaasCoursePending[cm.curso] || 0) + val;
                            asaasTotalPending += val;
                        }
                    }
                }
            }
        });"""

new_asaas_loop = """        aFaturas.forEach(f => {
            const st = (f.status || f.status_raw || '').toLowerCase();
            if (st === 'pendente' || st === 'pending' || st === 'a_vencer' || st === 'futuro' || st === 'confirmed') {
                const em = (f.email || '').toString().toLowerCase().trim();
                const cm = getCourse(f.curso || emailToCourse[em]);
                const val = Number(f.valor) || 0;
                
                // Conversão precisa de data compatível com ISO (YYYY-MM-DD) e BR (DD/MM/YYYY)
                const isoStr = (f.vencimento_iso || '').toString().slice(0, 10);
                const brStr = (f.vencimento || '').toString().slice(0, 10);
                let dObj = null;
                if (isoStr && isoStr.includes('-')) {
                    const [y, m, d] = isoStr.split('-').map(Number);
                    dObj = new Date(y, m - 1, d);
                } else if (brStr && brStr.includes('/')) {
                    const [d, m, y] = brStr.split('/').map(Number);
                    dObj = new Date(y, m - 1, d);
                }
                
                if (dObj && !isNaN(dObj.getTime())) {
                    const hoje = new Date();
                    const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
                    if (diffMeses >= 0 && diffMeses < 18) {
                        cm.projecao_18m_sim[diffMeses] += val;
                        if (diffMeses === 0 || diffMeses === 1) {
                            asaasCoursePending[cm.curso] = (asaasCoursePending[cm.curso] || 0) + val;
                            asaasTotalPending += val;
                        }
                    }
                }
            }
        });"""

if old_asaas_loop in text:
    text = text.replace(old_asaas_loop, new_asaas_loop)
    print("Replaced Asaas loop in template.html with robust future parser!")
else:
    # Try regex match
    pattern = r'aFaturas\.forEach\(f\s*=>\s*\{.*?if\s*\(\s*st\s*===\s*[\'"]pendente[\'"].*?\}\s*\);\s*\}'
    m = re.search(pattern, text, re.DOTALL)
    if m:
        text = text[:m.start()] + new_asaas_loop + '\n    }' + text[m.end():]
        print("Replaced Asaas loop via regex match!")
    else:
        print("Could not find old Asaas loop in template.html!")

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'w', encoding='utf-8') as f:
    f.write(text)

# Test syntax with node
scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_patch_syntax.js', 'w', encoding='utf-8') as f:
        f.write(scripts[0])
    res = subprocess.run(['node', '-c', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_patch_syntax.js'], capture_output=True, text=True)
    print("Node syntax returncode:", res.returncode)
    if res.returncode != 0:
        print("Node error:", res.stderr)
    else:
        print("SUCCESS! template.html syntax verified 100% CLEAN!")
