import os

target_paths = [
    r"c:\Users\DELL\Desktop\Dash_InfectoCast\sync_matriculas_rd.py",
    r"c:\Users\DELL\Desktop\Acompanhamento de acessos\sync_matriculas_rd.py"
]

for target_path in target_paths:
    if os.path.exists(target_path):
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target_str = 'dt_raw = s.get("data_insc") or s.get("data_inscricao") or s.get("data_matricula") or s.get("first") or s.get("createdAt")'
        replacement = '''dt_raw = (
                s.get("data_insc") or s.get("data_inscricao") or s.get("data_matricula") or s.get("first") or s.get("createdAt")
                or (s.get("asaas") and s["asaas"].get("faturas") and (s["asaas"]["faturas"][0].get("data_criacao") or s["asaas"]["faturas"][0].get("dateCreated") or s["asaas"]["faturas"][0].get("vencimento_iso")))
                or (s.get("vindi") and s["vindi"].get("faturas") and s["vindi"]["faturas"][0].get("vencimento_iso"))
            )'''
        if target_str in content:
            content_new = content.replace(target_str, replacement, 1)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content_new)
            print(f"Patched {target_path} successfully!")
        else:
            print(f"Target string not found in {target_path}")
