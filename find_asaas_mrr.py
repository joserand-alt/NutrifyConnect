import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\DELL\Desktop\Acompanhamento de acessos\asaas_api.py', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

pos = text.find('mrr_ativo')
print("asaas_api.py pos:", pos)
if pos != -1:
    print(text[max(0, pos-200):min(len(text), pos+400)])
