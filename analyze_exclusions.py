import sys, json, re

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    content = f.read()

m = content.find('const DATA = ')
end_m = content.find(';\n', m)
data = json.loads(content[m+len('const DATA = '):end_m])

students = data.get('students', [])
print(f"Total students atual: {len(students)}")

def should_exclude(s):
    email = str(s.get('email', '')).lower().strip()
    nome = str(s.get('nome', '')).lower().strip()
    curso = str(s.get('curso', '')).upper().strip()
    
    # 1. Curso nutrify connect
    if 'NUTRIFY' in curso:
        return True, f"Curso Nutrify Connect ({curso})"
    
    # 2. Domínios corporativos/internos
    if any(dom in email for dom in ['@infectocast', '@integralmedica', '@nutrify']):
        return True, f"Dominio interno ({email})"
        
    # 3. Palavra teste no nome ou email
    if 'teste' in email or 'teste' in nome:
        return True, f"Palavra teste ({nome} / {email})"
        
    return False, ""

to_exclude = []
remaining = []

for s in students:
    exc, reason = should_exclude(s)
    if exc:
        to_exclude.append((s, reason))
    else:
        remaining.append(s)

print(f"Registros a excluir: {len(to_exclude)}")
print(f"Registros remanescentes (Matrículas Reais Oficiais): {len(remaining)}")

print("\n--- Lista de Registros Excluídos ---")
for idx, (s, reason) in enumerate(to_exclude, 1):
    print(f"{idx}. {s.get('nome')} | {s.get('email')} | Curso: {s.get('curso')} | Motivo: {reason}")
