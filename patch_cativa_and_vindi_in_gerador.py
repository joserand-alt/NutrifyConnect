import os
import re

gerador_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py'

with open(gerador_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Enhance student construction in gerador.py for Cativa users and Vindi subscribers
cativa_enhancement = """
        # Check Cativa platform and login metadata
        if email_str in cativa_users_meta:
            c_meta = cativa_users_meta[email_str]
            student_data["plataforma"] = "Cativa"
            if c_meta.get('first_name') or c_meta.get('last_name'):
                full_c_name = f"{c_meta.get('first_name', '')} {c_meta.get('last_name', '')}".strip()
                if full_c_name: student_data["nome"] = full_c_name
            
            last_login_s = c_meta.get('last_login_at')
            if last_login_s:
                dt_c_login = pd.to_datetime(last_login_s[:19], errors='coerce')
                if pd.notna(dt_c_login):
                    student_data["acessou"] = True
                    login_ev = {
                        "d": dt_c_login.strftime("%d/%m/%Y %H:%M"),
                        "acao": "LOGIN WEB (Cativa)",
                        "cat": "login",
                        "item": "Plataforma Cativa Digital",
                        "mod": ""
                    }
                    student_data.setdefault("events", []).insert(0, login_ev)
                    if not student_data.get("last_fmt") or dt_c_login.date() > pd.to_datetime(student_data.get("last", "1970-01-01")).date():
                        student_data["last_fmt"] = dt_c_login.strftime("%d/%m/%Y")
                        student_data["last"] = dt_c_login.strftime("%d/%m/%Y")
                        student_data["dias_inativo"] = max(0, (hoje - dt_c_login.date()).days)
"""

# Also update the Vindi subscriber creation block in gerador.py
old_vindi_create = """                new_v_st = {
                    "email": em_clean,
                    "nome": v_obj.get('customer_name') or 'Aluno Vindi',
                    "curso": c_inferido,
                    "curso_inferido": True,
                    "curso_origem": c_orig,
                    "telefone": "",
                    "acessou": False,
                    "data_insc": None,
                    "data_inscricao": None,
                    "inscricao": None,
                    "dias_desde_insc": 0,
                    "plataforma": "Academy",
                    "id_aluno": str(v_obj.get('customer_id', '')),
                    "events": [],
                    "vindi": v_obj,
                    "asaas": None
                }"""

new_vindi_create = """                # Check if this Vindi subscriber has Cativa account / login
                st_plat = "Academy"
                st_nome = v_obj.get('customer_name') or 'Aluno Vindi'
                st_tel = ""
                st_acessou = False
                st_events = []
                st_last_fmt = None
                st_dias_inativo = None
                
                if em_clean in cativa_users_meta:
                    c_meta = cativa_users_meta[em_clean]
                    st_plat = "Cativa"
                    st_tel = normalize_phone(c_meta.get('phone', ''))
                    if c_meta.get('first_name') or c_meta.get('last_name'):
                        c_fullname = f"{c_meta.get('first_name', '')} {c_meta.get('last_name', '')}".strip()
                        if c_fullname: st_nome = c_fullname
                    
                    last_login_s = c_meta.get('last_login_at')
                    if last_login_s:
                        dt_c_login = pd.to_datetime(last_login_s[:19], errors='coerce')
                        if pd.notna(dt_c_login):
                            st_acessou = True
                            st_events.append({
                                "d": dt_c_login.strftime("%d/%m/%Y %H:%M"),
                                "acao": "LOGIN WEB (Cativa)",
                                "cat": "login",
                                "item": "Plataforma Cativa Digital",
                                "mod": ""
                            })
                            st_last_fmt = dt_c_login.strftime("%d/%m/%Y")
                            st_dias_inativo = max(0, (hoje - dt_c_login.date()).days)

                new_v_st = {
                    "email": em_clean,
                    "nome": st_nome,
                    "curso": c_inferido,
                    "curso_inferido": True,
                    "curso_origem": c_orig,
                    "telefone": st_tel,
                    "acessou": st_acessou,
                    "data_insc": None,
                    "data_inscricao": None,
                    "inscricao": None,
                    "dias_desde_insc": 0,
                    "plataforma": st_plat,
                    "id_aluno": str(v_obj.get('customer_id', '')),
                    "events": st_events,
                    "last_fmt": st_last_fmt,
                    "dias_inativo": st_dias_inativo,
                    "vindi": v_obj,
                    "asaas": None
                }"""

if old_vindi_create in code:
    code = code.replace(old_vindi_create, new_vindi_create)
    print("Replaced old_vindi_create!")
else:
    print("Could not find exact old_vindi_create string.")

with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("gerador.py updated successfully.")
