import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

GERADOR_PATH = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'

with open(GERADOR_PATH, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the sanitization block in gerador.py
old_marker = '''    # =========================================================================
    # REGRA DE NEGÓCIO DEFINITIVA: SEM ACESSO E SEM PAGAMENTO NÃO É MATRÍCULA
    # Expurgar registros sem histórico de acesso e sem contrato/fatura financeira
    # ========================================================================='''

assert old_marker in code, "old_marker not found"

new_sanitization = '''    # =========================================================================
    # REGRA DE NEGÓCIO DEFINITIVA: 
    # 1. Desconsiderar curso NUTRIFY CONNECT
    # 2. Desconsiderar e-mails @infectocast, @integralmedica, @nutrify
    # 3. Desconsiderar palavra 'teste' no nome ou e-mail
    # 4. Desconsiderar registros sem acesso (0 logins) e sem pagamento/contrato
    # =========================================================================
    def is_invalid_or_internal(email, nome='', curso=''):
        em = str(email or '').lower().strip()
        nm = str(nome or '').lower().strip()
        cr = str(curso or '').upper().strip()
        
        if 'NUTRIFY' in cr:
            return True
        if any(dom in em for dom in ['@infectocast', '@integralmedica', '@nutrify', '@vectorcomunica']):
            return True
        if 'teste' in em or 'teste' in nm:
            return True
        if any(x in em for x in ['gcotta29', 'j.o.s.e.r.a.n.d@gmail.com', 'email@email.com']):
            return True
        return False

    fin_emails = set()
    fin_names = set()
    if isinstance(financeiro_data, dict):
        for f in financeiro_data.get('faturas_tabela', []):
            em = str(f.get('email', '')).lower().strip()
            nm = str(f.get('aluno', '')).lower().strip()
            cr = str(f.get('curso', '')).upper().strip()
            if not is_invalid_or_internal(em, nm, cr):
                if em: fin_emails.add(em)
                if nm: fin_names.add(nm)

    if isinstance(asaas_financeiro, dict):
        for f in asaas_financeiro.get('faturas_tabela', []):
            em = str(f.get('email', '')).lower().strip()
            nm = str(f.get('aluno', '')).lower().strip()
            cr = str(f.get('curso', '')).upper().strip()
            if not is_invalid_or_internal(em, nm, cr):
                if em: fin_emails.add(em)
                if nm: fin_names.add(nm)

    matriculas_legitimas = []
    expurgados_count = 0
    for s in students:
        em = str(s.get('email', '')).lower().strip()
        nm = str(s.get('nome', '')).lower().strip()
        cr = str(s.get('curso', '')).upper().strip()
        
        # 1. Regra de exclusão de internos, testes e Nutrify Connect
        if is_invalid_or_internal(em, nm, cr):
            expurgados_count += 1
            continue
            
        acessou = bool(s.get('acessou', False))
        logins = int(s.get('logins', 0) or 0)
        has_access = (acessou and logins > 0)
        
        v = s.get('vindi') or {}
        a = s.get('asaas') or {}
        has_finance = bool(v or a or em in fin_emails or nm in fin_names)
        
        # 2. Regra de vínculo (tem acesso ou tem contrato/pagamento)
        if has_access or has_finance:
            matriculas_legitimas.append(s)
        else:
            expurgados_count += 1

    print(f"[MATRÍCULAS] Base final oficial sanitizada: {len(matriculas_legitimas)} matrículas ({expurgados_count} desconsiderados por serem teste/internos/Nutrify Connect/sem vínculo).")
    students = matriculas_legitimas'''

idx_start = code.find(old_marker)
idx_end = code.find('    data = {\n        "meta": {', idx_start)
assert idx_end != -1, "data marker not found"

new_code = code[:idx_start] + new_sanitization + '\n\n' + code[idx_end:]

with open(GERADOR_PATH, 'w', encoding='utf-8') as f:
    f.write(new_code)

print("gerador.py updated with complete exclusion rules!")
