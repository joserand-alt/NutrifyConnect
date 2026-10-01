with open('vindi_service.py', 'r', encoding='utf-8') as f:
    vindi_src = f.read()

pos_subs = vindi_src.find('for s in subs:')
if pos_subs == -1:
    pos_subs = vindi_src.find('for sub in subs:')
if pos_subs == -1:
    pos_subs = vindi_src.find('subs')

print("=== vindi_service subs processing ===")
print(vindi_src[pos_subs:pos_subs+3000])
