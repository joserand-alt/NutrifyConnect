import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)

if scripts:
    with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_exec.js', 'w', encoding='utf-8') as f:
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
        console.log('drawExecView executed successfully with Dynamic G7!');
        console.log('Testing drawFinanceiro...');
        drawFinanceiro(true);
        console.log('drawFinanceiro executed successfully!');
        """)
    res = subprocess.run(['node', r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test_exec.js'], capture_output=True, text=True)
    print("Node run returncode:", res.returncode)
    print("Node stdout:\n", res.stdout)
    if res.stderr:
        print("Node stderr:\n", res.stderr)
