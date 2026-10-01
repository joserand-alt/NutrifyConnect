template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace block 1
idx1 = text.find('function switchTab')
end1 = text.find('// TIMELINE', idx1)
assert idx1 != -1 and end1 != -1, "Block 1 not found"

new_block_1 = """function selectTab(pId) {
    if (!pId) return;
    $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.p === pId));
    $$('.panel').forEach(p => p.classList.toggle('on', p.id === 'p-' + pId));

    if (pId === 'home') drawHome(true);
    if (pId === 'prog') renderRows();
    if (pId === 'tl') drawTimeline(true);
    if (pId === 'mod') renderModules();
    if (pId === 'origem') drawOrigem(true);
    if (pId === 'fin') drawFinanceiro(true);
    if (pId === 'funil') {
        drawFunil(true);
        if ($('.filters')) $('.filters').style.display = 'none';
    } else {
        if ($('.filters')) $('.filters').style.display = 'flex';
    }
}
window.selectTab = selectTab;
window.switchTab = selectTab;

// TABS LISTENERS
$$('.tab').forEach(t => {
    t.onclick = e => {
        e.preventDefault();
        selectTab(t.dataset.p);
    };
});

"""

text = text[:idx1] + new_block_1 + text[end1:]
print("Block 1 updated with selectTab")

# 2. Remove block 2 (duplicate tab click listener)
idx2 = text.find('b.dataset.p')
if idx2 != -1:
    start2 = text.rfind("$$('.tab').forEach", 0, idx2)
    end2 = text.find("$$('.tab')[0].click();", idx2)
    if start2 != -1 and end2 != -1:
        text = text[:start2] + "// Tabs inicializadas via selectTab\n" + text[end2:]
        print("Block 2 (duplicate tab listener) removed!")

# 3. Ensure drawFinanceiro can always draw cleanly even on first load
p_check = text.find("function drawFinanceiro(force) {")
if p_check != -1:
    # Let's inspect the first lines of drawFinanceiro
    slice_df = text[p_check:p_check+250]
    print("drawFinanceiro head:", repr(slice_df))

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved template.html successfully!")
