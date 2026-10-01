import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = """// Totalizadores Consolidados Financeiros Unificados
    const finUnifiedGlobal = computeUnifiedFinancialDataset('all');
    const uKpis = finUnifiedGlobal.global.kpis || {};"""

replacement = """// Totalizadores Consolidados Financeiros Unificados
    const vKpis = vindi.kpis || {};
    const aKpis = asaas.kpis || {};
    const finUnifiedGlobal = computeUnifiedFinancialDataset('all');
    const uKpis = finUnifiedGlobal.global.kpis || {};"""

if target in text:
    text = text.replace(target, replacement)
    print("Added vKpis and aKpis definition!")

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'w', encoding='utf-8') as f:
    f.write(text)

# Extract JS and test with node
scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_verify_all.js', 'w', encoding='utf-8') as f:
        mock_env = """
        const mockEl = (id) => ({
            id: id || '',
            style: {},
            textContent: '',
            innerHTML: '',
            value: '',
            classList: { add(){}, remove(){}, toggle(){ return true; } },
            setAttribute(){},
            appendChild(){},
            addEventListener(){},
            scrollIntoView(){}
        });
        global.document = {
            getElementById: (id) => mockEl(id),
            querySelector: (sel) => mockEl(sel),
            querySelectorAll: (sel) => [mockEl(sel)],
            createElement: (tag) => mockEl(tag),
            body: { appendChild(){}, removeChild(){} }
        };
        global.window = {
            location: { href: '', pathname: '', search: '' },
            addEventListener: () => {}
        };
        """
        f.write(mock_env + '\n' + scripts[0] + '\n' + """
        console.log('Testing drawExecView...');
        drawExecView(true);
        console.log('drawExecView executed successfully!');
        console.log('Testing drawFinanceiro...');
        drawFinanceiro(true);
        console.log('drawFinanceiro executed successfully!');
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_verify_all.js'], capture_output=True, text=True)
    print("Node output:\n", res.stdout)
    if res.stderr:
        print("Node stderr:\n", res.stderr)
