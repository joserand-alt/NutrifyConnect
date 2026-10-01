import re

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update logs query for Cativa students
old_target = "logs = df_log[(df_log['E-mail'] == email) & (df_log['Curso'] == c_canon)]"
new_target = "logs = df_log[(df_log['E-mail'] == email) & ((df_log['Curso'] == c_canon) | (df_log['Curso'] == 'PLATAFORMA GERAL'))]"

if old_target in text:
    text = text.replace(old_target, new_target, 1)
    print("logs filter updated successfully")
else:
    print("old_target not found")

# 2. Update acao assignment in logs loop for Cativa students
old_acao = """                for _, r in logs.sort_values('Data log', ascending=False).iterrows():
                    acao = "ASSISTIU AULA"
                    cat = "concluiu" """

# Let's inspect exact indentation in file
pos = text.find("for _, r in logs.sort_values('Data log', ascending=False).iterrows():")
if pos != -1:
    snippet = text[pos:pos+250]
    print("Found snippet:\n", repr(snippet))
    
    # We replace:
    # acao = "ASSISTIU AULA"
    # cat = "concluiu"
    pattern = r'(\s+)(acao = "ASSISTIU AULA"\s+cat = "concluiu")'
    replacement = r'\1raw_acao = str(r.iloc[3] if len(r) > 3 else "ASSISTIU AULA").upper()\n\1acao = "LOGIN WEB (Cativa)" if "LOGIN" in raw_acao else "ASSISTIU AULA"\n\1cat = "login" if "LOGIN" in raw_acao else "concluiu"'
    text = re.sub(pattern, replacement, text, count=1)
    print("Acao assignment updated successfully")

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Finished patching gerador.py")
