import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# Update Nunca Acessaram subtitle
old_sub = '<div class="exec-card-sub">${fN(totalReproducoes)} reproduções de aulas · ${fN(totalLogins)} logins</div>'
new_sub = '<div class="exec-card-sub">Alunos com contrato ativo sem 1º login registrado</div>'

if old_sub in text:
    text = text.replace(old_sub, new_sub)
    print("Replaced Nunca Acessaram subtitle.")

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("Template updated!")
