import json
import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\dashboard_gerado.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const DATA = (\{.*?\});\s*(?:let|const|var|function|\n\s*let|\n\s*const)', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    students = data.get('students', [])
    v_fat = data.get('financeiro', {}).get('faturas_tabela', [])
    a_fat = data.get('financeiro_asaas', {}).get('faturas_tabela', [])

    emails_to_check = [
        'leticia.figueiredogomes@gmail.com',
        'alicia_morais@hotmail.com',
        'silviamariane11@hotmail.com',
        'priscila.brandao3005@gmail.com',
        'tatianacamposm2014@gmail.com',
        'marcoseduardocabral@hotmail.com',
        'laurawarlitzer@gmail.com',
        'victorialopes3021@gmail.com'
    ]

    print("=== 1. SEARCH IN DATA.students ===")
    found_st = {}
    for s in students:
        em = str(s.get('email', '')).lower().strip()
        if em in emails_to_check:
            found_st[em] = s
            print(f"EMAIL: {em}")
            print(f"  Nome: {s.get('nome')}")
            print(f"  Curso: '{s.get('curso')}'")
            print(f"  Plataforma: {s.get('plataforma')}")
            print(f"  ID Aluno: {s.get('id_aluno')}")
            print(f"  Vindi plano: {s.get('vindi', {}).get('plano') if s.get('vindi') else None}")
            print(f"  Asaas plano: {s.get('asaas', {}).get('plano') if s.get('asaas') else None}")
            print("-" * 50)

    for em in emails_to_check:
        if em not in found_st:
            print(f"NOT FOUND in DATA.students: {em}")

    print("\n=== 2. SEARCH IN VINDI FATURAS ===")
    for f in v_fat:
        em = str(f.get('email', '')).lower().strip()
        if em in emails_to_check:
            print(f"VINDI FATURA: {em} | Aluno: {f.get('aluno')} | Plano: '{f.get('plano')}' | Status: {f.get('status')} | Curso field: '{f.get('curso')}'")
            # print only 1 per student
            emails_to_check.remove(em)

    print("\n=== 3. SEARCH IN ASAAS FATURAS ===")
    for f in a_fat:
        em = str(f.get('email', '')).lower().strip()
        if em in emails_to_check:
            print(f"ASAAS FATURA: {em} | Aluno: {f.get('aluno')} | Plano: '{f.get('plano')}' | Status: {f.get('status')} | Description: '{f.get('description')}'")
