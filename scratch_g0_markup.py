with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('<!-- G0 – MONITORAMENTO AO VIVO -->')
end_pos = text.find('<!-- G1', pos)
if end_pos == -1: end_pos = pos + 4000
with open('g0_full_markup.html', 'w', encoding='utf-8') as out:
    out.write(text[pos:end_pos])
print("Saved g0_full_markup.html")
