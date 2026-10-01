import os

dash_dir = r'C:\Users\DELL\Desktop\Dash_InfectoCast'
path = os.path.join(dash_dir, 'template.html')
with open(path, 'r', encoding='utf-8') as f:
    template_code = f.read()

# Let's extract everything inside <script>...</script>
script_match = template_code[template_code.find('<script>')+8:template_code.rfind('</script>')]

test_runner = f"""
const fs = require('fs');
const html = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html', 'utf-8');
const matchData = html.match(/const DATA = (\\{{[\\s\\S]*?\\}});/);
const DATA = JSON.parse(matchData[1]);

// Mock browser DOM globals
const domElements = new Map();
function getOrCreateElem(id) {{
    if (!domElements.has(id)) {{
        domElements.set(id, {{
            id: id,
            innerHTML: '',
            innerText: '',
            textContent: '',
            style: {{}},
            classList: {{
                add: () => {{}},
                remove: () => {{}},
                toggle: () => {{}},
                contains: () => false
            }},
            appendChild: () => {{}},
            setAttribute: () => {{}},
            getAttribute: () => '',
            querySelectorAll: () => [],
            addEventListener: () => {{}}
        }});
    }}
    return domElements.get(id);
}}

const document = {{
    getElementById: id => getOrCreateElem(id),
    querySelector: sel => getOrCreateElem(sel.replace('#', '')),
    querySelectorAll: sel => [getOrCreateElem(sel.replace('#', ''))],
    body: getOrCreateElem('body'),
    addEventListener: () => {{}}
}};

const window = {{
    document: document,
    addEventListener: () => {{}},
    innerWidth: 1920,
    innerHeight: 1080
}};

const $ = sel => getOrCreateElem(sel.replace('#', '').replace('.', ''));
const $$ = sel => [getOrCreateElem(sel.replace('#', '').replace('.', ''))];

try {{
    {script_match}
    
    console.log('Testing renderAll()...');
    renderAll();
    console.log('✅ renderAll() executed successfully!');
    
    console.log('Testing drawExecView(true)...');
    drawExecView(true);
    console.log('✅ drawExecView(true) executed successfully! Mount innerHTML length:', getOrCreateElem('exec-content-mount').innerHTML.length);
    
    console.log('Testing openModalMatriculas("24h_conf")...');
    openModalMatriculas('24h_conf');
    console.log('✅ openModalMatriculas executed successfully!');
    
}} catch (err) {{
    console.error('❌ RUNTIME ERROR:', err.message);
    console.error(err.stack);
}}
"""

with open('test_full_runtime.js', 'w', encoding='utf-8') as f:
    f.write(test_runner)

print("Created test_full_runtime.js")
