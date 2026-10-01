import json
import re
import subprocess

with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

m = re.search(r'const DATA\s*=\s*(\{.*?\});', dash_html, re.DOTALL)
data_json = m.group(1) if m else '{}'

with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'r', encoding='utf-8') as f:
    template_html = f.read()

script_m = re.search(r'<script>(.*?)</script>', template_html, re.DOTALL)
script_code = script_m.group(1)

script_with_data = script_code.replace('const DATA = {};', f'const DATA = {data_json};', 1)

mock_dom_js = f'''
const elements = {{}};
function createElement(tag) {{
    return {{
        tagName: tag,
        innerHTML: '',
        textContent: '',
        style: {{}},
        classList: {{
            toggle: () => {{}},
            add: () => {{}},
            remove: () => {{}},
            contains: () => false
        }},
        dataset: {{}},
        addEventListener: () => {{}},
        querySelector: () => null,
        querySelectorAll: () => []
    }};
}}

function getEl(sel) {{
    if (!elements[sel]) {{
        elements[sel] = createElement('div');
    }}
    return elements[sel];
}}

global.document = {{
    readyState: 'complete',
    querySelector: (s) => getEl(s),
    querySelectorAll: (s) => [getEl(s)],
    getElementById: (id) => getEl('#' + id),
    createElement: createElement,
    addEventListener: () => {{}}
}};
global.window = global;
global.Intl = Intl;

{script_with_data}

console.log('Running initDashboard...');
initDashboard();

console.log('Testing drawCursoView for first course...');
drawCursoView('', true);
console.log('curso-content-mount innerHTML length:', elements['#curso-content-mount'].innerHTML.length);

console.log('Testing drawCursoView for SOS Antibiótico...');
drawCursoView('S.O.S ANTIBIOTICO', true);
console.log('curso-content-mount length for SOS:', elements['#curso-content-mount'].innerHTML.length);

console.log('Testing selectTab(\"curso\")...');
selectTab('curso');
console.log('SUCCESS!');
process.exit(0);
'''

with open('temp_test_curso_tab.js', 'w', encoding='utf-8') as f:
    f.write(mock_dom_js)

res = subprocess.run(['node', 'temp_test_curso_tab.js'], capture_output=True, text=True, encoding='utf-8')
print('Return code:', res.returncode)
print('Stdout:\n', res.stdout)
if res.stderr:
    print('Stderr:\n', res.stderr)
