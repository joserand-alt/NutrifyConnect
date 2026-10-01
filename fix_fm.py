import os

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

old_fm = "const fM = (n) => fmtMoney(n || 0);"
new_fm = "const fM = (n) => 'R$ ' + (Number(n) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });"

text = text.replace(old_fm, new_fm)

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully updated fM definition in template.html!')
