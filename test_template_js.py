import sys, json

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace DATA placeholder with mock DATA
mock_data = {
    "students": [],
    "financeiro": {"kpis": {}, "faturas_tabela": []},
    "financeiro_asaas": {"kpis": {}, "faturas_tabela": []},
    "funil": {"kpis": {}},
    "action_counts": {}
}

html = html.replace('/*DATA_PLACEHOLDER*/', 'const DATA = ' + json.dumps(mock_data) + ';')

script_start = html.find('<script>')
script_end = html.rfind('</script>')

js_code = html[script_start+len('<script>'):script_end]

mock_env = '''
const makeEl = (id) => ({
  id,
  classList: { toggle: () => {}, add: () => {}, remove: () => {} },
  style: {},
  innerHTML: '',
  textContent: '',
  addEventListener: () => {},
  appendChild: () => {},
  click: () => {},
  value: '',
  dataset: { p: 'exec' }
});
global.window = global;
global.document = {
  getElementById: (id) => makeEl(id),
  querySelectorAll: () => [makeEl('tab')],
  querySelector: (s) => makeEl(s),
  createElement: (t) => makeEl(t)
};
global.$ = (s) => makeEl(s);
global.$$ = (s) => [makeEl(s)];
'''

with open('test_exec_template.js', 'w', encoding='utf-8') as f:
    f.write(mock_env + js_code + '\n\nconsole.log("Testing drawExecView on template.html...");\ntry { drawExecView(true); console.log("SUCCESS! drawExecView executed without errors!"); } catch(e) { console.error("ERROR IN drawExecView:", e); }\n')

print("Created test_exec_template.js")
