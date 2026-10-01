import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('def _process(')
pos_end = text.find('def get_asaas_data(')
print(text[pos:pos+4000])
print("\n--- Next part of _process ---")
print(text[pos+4000:pos_end])
