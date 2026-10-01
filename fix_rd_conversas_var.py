import os

dash_dir = r'C:\Users\DELL\Desktop\Dash_InfectoCast'
path = os.path.join(dash_dir, 'template.html')

with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

target = '''    const ev = (CURRENT_DATA && CURRENT_DATA.action_counts) ? CURRENT_DATA.action_counts : ((DATA && DATA.action_counts) ? DATA.action_counts : {});'''
replacement = '''    const ev = (CURRENT_DATA && CURRENT_DATA.action_counts) ? CURRENT_DATA.action_counts : ((DATA && DATA.action_counts) ? DATA.action_counts : {});
    const rdConversasData = (DATA && DATA.rd_conversas) ? DATA.rd_conversas : {};'''

if target in code:
    code = code.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("SUCCESS: Added rdConversasData definition to drawExecView in template.html!")
else:
    print("Target not found!")
