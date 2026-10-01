import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('mrr =')
if pos == -1:
    pos = text.find('mrr')
print(text[max(0, pos-200):min(len(text), pos+600)])
