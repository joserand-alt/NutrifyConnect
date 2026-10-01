import sys, json
sys.stdout.reconfigure(encoding='utf-8')

# 1. Read asaas_service.py
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

print("Length of asaas_service.py:", len(text))
pos_pay = text.find('def sync_asaas_data')
if pos_pay == -1: pos_pay = text.find('fetch_payments')
print("Snippet around sync/payments in asaas_service.py:")
print(text[pos_pay:pos_pay+3500])
