import os, re, json

wa_log_path = 'Log mensagems.csv'
if not os.path.exists(wa_log_path):
    if os.path.exists(os.path.join('BD', 'Log mensagems.csv')):
        wa_log_path = os.path.join('BD', 'Log mensagems.csv')

print('Using log file:', wa_log_path)
inbound_by_phone = {} # mensagens enviadas pelo cliente (sent_by_us == False)
outbound_by_phone = {} # mensagens enviadas por nos (sent_by_us == True)

if os.path.exists(wa_log_path):
    with open(wa_log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    rows = content.split('\n"')
    for r in rows:
        if '@c.us' not in r: continue
        parts = r.split('","')
        if len(parts) < 4: continue
        msg_id = parts[0]
        sent_by_us = 'true_' in msg_id
        phone_m = re.search(r'(\d{10,13})@c\.us', msg_id)
        if not phone_m: continue
        ph = phone_m.group(1)
        if ph.startswith('55'): ph = ph[2:]
        if len(ph) >= 8:
            ph_key = ph[-8:]
            if sent_by_us:
                outbound_by_phone[ph_key] = outbound_by_phone.get(ph_key, 0) + 1
            else:
                inbound_by_phone[ph_key] = inbound_by_phone.get(ph_key, 0) + 1

print(f'Total de contatos que responderam/enviaram mensagem (INBOUND): {len(inbound_by_phone)}')
print(f'Total de contatos que receberam disparos (OUTBOUND): {len(outbound_by_phone)}')

# Cruzar com os clientes do RD Conversas
with open('rd_conversas_cache.json', 'r', encoding='utf-8') as f:
    rdc = json.load(f)
customers = rdc.get('customers', [])
resp_count = 0
out_only_count = 0
for c in customers:
    raw_ph = re.sub(r'\D', '', str(c.get('cel_phone') or ''))
    if len(raw_ph) >= 8:
        if raw_ph[-8:] in inbound_by_phone:
            resp_count += 1
        elif raw_ph[-8:] in outbound_by_phone:
            out_only_count += 1

print(f'Contatos do RD Conversas com resposta confirmada do cliente (INBOUND - OPORTUNIDADE REAL): {resp_count}')
print(f'Contatos do RD Conversas somente com disparo enviado (OUTBOUND ATIVO - DISPARO): {out_only_count}')
