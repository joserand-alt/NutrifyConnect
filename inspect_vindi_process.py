import json

with open('vindi_service.py', 'r', encoding='utf-8') as f:
    vindi_src = f.read()

# Let's check how subscriptions are processed in vindi_service.py
pos_sub = vindi_src.find('def _process(')
print("=== vindi_service _process definition ===")
print(vindi_src[pos_sub:pos_sub+2500])
