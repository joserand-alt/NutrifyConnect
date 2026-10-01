import os

target_paths = [
    r"c:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py",
    r"c:\Users\DELL\Desktop\Acompanhamento de acessos\asaas_service.py"
]

patch_code = '''        if c_mail:

            students_asaas[c_mail] = st_obj

    # Incluir tambem clientes com cobrancas pendentes/a vencer (Matriculas Pendentes)
    for c in customers:
        cid = c.get("id")
        if not cid or cid in payments_by_cid:
            continue
        c_payments = [p for p in payments if p.get("customer") == cid]
        if not c_payments:
            continue
        cust = cust_by_id.get(cid, c)
        ext = (cust.get("externalReference") or "").strip()
        c_mail = (cust.get("email") or "").lower().strip()
        if not ext and not c_mail:
            continue

        unpaid_faturas = []
        for p in c_payments:
            valor = float(p.get("value") or 0)
            status_raw = p.get("status", "PENDING")
            due_iso = p.get("dueDate") or ""
            created_iso = p.get("dateCreated") or due_iso
            unpaid_faturas.append({
                "id": p.get("id"),
                "status": "a_vencer" if status_raw == "PENDING" else "em_atraso",
                "status_raw": status_raw,
                "status_label": "A Vencer" if status_raw == "PENDING" else "Em Atraso",
                "status_color": "#d97706" if status_raw == "PENDING" else "#e11d48",
                "status_bg": "rgba(217,119,6,0.1)",
                "valor": valor,
                "valor_fmt": f"R$ {valor:,.2f}".replace(",","X").replace(".",",").replace("X","."),
                "vencimento": _fmt_date(due_iso),
                "vencimento_iso": due_iso,
                "data_criacao": created_iso,
                "dateCreated": created_iso,
                "data_pagamento": "",
                "data_pagamento_iso": "",
                "forma_pagamento": p.get("billingType", ""),
                "url": p.get("invoiceUrl", ""),
                "dias_atraso": 0,
                "aluno": cust.get("name", ""),
                "email": cust.get("email", ""),
                "cpfcnpj": cust.get("cpfCnpj", ""),
                "customer_ext_ref": ext,
                "description": p.get("description", ""),
                "plano": (p.get("description") or "").split(" - ")[0],
            })

        st_obj = {
            "has_asaas": True,
            "customer_id": cid,
            "customer_name": cust.get("name", ""),
            "customer_email": cust.get("email", ""),
            "cpfcnpj": cust.get("cpfCnpj", ""),
            "aluno_id_extref": ext,
            "status_financeiro": "PENDING",
            "status_assinatura": "PENDING",
            "status_label": "Matrícula Pendente (Aguardando Pagamento)",
            "status_color": "#d97706",
            "status_bg": "rgba(217,119,6,0.1)",
            "dias_atraso": 0,
            "valor_atraso": 0,
            "total_pago": 0.0,
            "faturas": sorted(unpaid_faturas, key=lambda x: x.get("dateCreated") or x.get("vencimento_iso") or "", reverse=True),
        }
        if ext:
            students_asaas[ext] = st_obj
        if c_mail:
            students_asaas[c_mail] = st_obj
'''

for target_path in target_paths:
    if os.path.exists(target_path):
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        target_str = '        if c_mail:\n\n            students_asaas[c_mail] = st_obj'
        if target_str in content:
            new_content = content.replace(target_str, patch_code, 1)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Patched {target_path} successfully!")
        else:
            print(f"Target string not found in {target_path}")
