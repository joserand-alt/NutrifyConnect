import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('mrr_ativo')
print("asaas_service.py mrr_ativo pos:", pos)
if pos != -1:
    print(text[max(0, pos-300):min(len(text), pos+400)])
