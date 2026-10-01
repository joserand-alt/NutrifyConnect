import json
import re
import subprocess

# Let's read template.html and inject DATA from dashboard_gerado.html
with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

m = re.search(r'const DATA\s*=\s*(\{.*?\});', dash_html, re.DOTALL)
data_json = m.group(1) if m else '{}'

with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'r', encoding='utf-8') as f:
    template_html = f.read()

# Extract the script
script_m = re.search(r'<script>(.*?)</script>', template_html, re.DOTALL)
script_code = script_m.group(1)

# Replace const DATA = {}; with the real DATA
script_with_data = script_code.replace('const DATA = {};', f'const DATA = {data_json};', 1)

# Create a mock DOM test in JS
mock_dom_js = f'''
// Minimal DOM mock
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
        elements[sel] = createElement(sel.startsWith('#') ? 'div' : 'div');
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

// Test assertions
console.log('Testing initDashboard...');
initDashboard();

console.log('CURRENT_DATA.students count:', CURRENT_DATA.students ? CURRENT_DATA.students.length : 'undefined');
console.log('Filter curso HTML length:', elements['#filter-curso'] ? elements['#filter-curso'].innerHTML.length : 0);
console.log('Filter aluno HTML length:', elements['#filter-aluno'] ? elements['#filter-aluno'].innerHTML.length : 0);

// Test Progresso tab
console.log('Testing selectTab(\"prog\")...');
selectTab('prog');
console.log('Tbody innerHTML length:', elements['#tbody'] ? elements['#tbody'].innerHTML.length : 0);

// Test all other tabs
for (const tab of ['exec', 'home', 'mod', 'ret', 'tl', 'funil', 'origem', 'fin']) {{
    console.log('Testing selectTab(\"' + tab + '\")...');
    selectTab(tab);
}}

console.log('ALL TABS TESTED SUCCESSFULLY!');
'''

with open('temp_test_full_tabs.js', 'w', encoding='utf-8') as f:
    f.write(mock_dom_js)

res = subprocess.run(['node', 'temp_test_full_tabs.js'], capture_output=True, text=True, encoding='utf-8')
print('Return code:', res.returncode)
print('Output:\n', res.stdout)
if res.stderr:
    print('Stderr:\n', res.stderr)
