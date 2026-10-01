import os

dash_dir = r'C:\Users\DELL\Desktop\Dash_InfectoCast'
path = os.path.join(dash_dir, 'dashboard_gerado.html')
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

script_start = html.find('<script>') + 8
script_end = html.rfind('</script>')
script_body = html[script_start:script_end]

test_code = f"""
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
    readyState: 'complete',
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
    {script_body}
    
    console.log('Mount content length:', getOrCreateElem('exec-content-mount').innerHTML.length);
    console.log('✅ Entire dashboard_gerado.html script executed successfully with ZERO errors!');
}} catch (err) {{
    console.error('❌ RUNTIME ERROR IN DASHBOARD:', err.message);
    console.error(err.stack);
}}
"""

with open('test_dash_exec.js', 'w', encoding='utf-8') as f:
    f.write(test_code)

print("Created test_dash_exec.js")
