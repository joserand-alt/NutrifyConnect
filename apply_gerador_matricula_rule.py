import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

GERADOR_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'

with open(GERADOR_PATH, 'r', encoding='utf-8') as f:
    code = f.read()

target = "    data = {\n        \"meta\": {"
assert target in code, "Target marker not found in gerador.py"

patch_code = '''    # =========================================================================
    # REGRA DE NEGÓCIO DEFINITIVA: SEM ACESSO E SEM PAGAMENTO NÃO É MATRÍCULA
    # Expurgar registros sem histórico de acesso e sem contrato/fatura financeira
    # =========================================================================
    fin_emails = set()
    fin_names = set()
    if isinstance(financeiro_data, dict):
        for f in financeiro_data.get('faturas_tabela', []):
            em = str(f.get('email', '')).lower().strip()
            nm = str(f.get('aluno', '')).lower().strip()
            if em: fin_emails.add(em)
            if nm: fin_names.add(nm)
    if isinstance(asaas_financeiro, dict):
        for f in asaas_financeiro.get('faturas_tabela', []):
            em = str(f.get('email', '')).lower().strip()
            nm = str(f.get('aluno', '')).lower().strip()
            if em: fin_emails.add(em)
            if nm: fin_names.add(nm)

    matriculas_legitimas = []
    expurgados_count = 0
    for s in students:
        em = str(s.get('email', '')).lower().strip()
        nm = str(s.get('nome', '')).lower().strip()
        acessou = bool(s.get('acessou', False))
        logins = int(s.get('logins', 0) or 0)
        has_access = (acessou and logins > 0)
        
        v = s.get('vindi') or {}
        a = s.get('asaas') or {}
        has_finance = bool(v or a or em in fin_emails or nm in fin_names)
        
        if has_access or has_finance:
            matriculas_legitimas.append(s)
        else:
            expurgados_count += 1

    print(f"[MATRÍCULAS] Base final sanitizada: {len(matriculas_legitimas)} matrículas legítimas ({expurgados_count} cadastros sem acesso e sem pagamento expurgados).")
    students = matriculas_legitimas

    data = {
        "meta": {'''

new_code = code.replace(target, patch_code)

with open(GERADOR_PATH, 'w', encoding='utf-8') as f:
    f.write(new_code)

print("gerador.py successfully patched!")
