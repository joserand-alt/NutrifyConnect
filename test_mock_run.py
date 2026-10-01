with open('test_exec_debug.js', 'r', encoding='utf-8') as f:
    js = f.read()

mock_prefix = """
const document = {
    getElementById: (id) => ({
        innerHTML: '',
        value: '',
        style: {},
        classList: { add: ()=>{}, remove: ()=>{} },
        querySelectorAll: ()=>[],
        addEventListener: ()=>{}
    }),
    querySelectorAll: () => [],
    querySelector: () => ({ style: {}, classList: { add: ()=>{}, remove: ()=>{} } })
};
const window = { addEventListener: ()=>{} };
"""

suffix = """
console.log("Testing drawExecView execution in Node...");
try {
    drawExecView(true);
    console.log(">>> drawExecView executed successfully with 0 errors! <<<");
} catch(e) {
    console.error(">>> ERROR in drawExecView:", e);
}
"""

with open('test_exec_runtime_mock.js', 'w', encoding='utf-8') as f:
    f.write(mock_prefix + "\n" + js + "\n" + suffix)

print("test_exec_runtime_mock.js generated.")
