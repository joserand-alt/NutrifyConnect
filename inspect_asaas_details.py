import json

with open('asaas_cache.json', 'r', encoding='utf-8') as f:
    asaas = json.load(f)

for em in ['danielesarto@yahoo.com.br', 'beatriz.grinsztejn@gmail.com', 'adrianammas@gmail.com', 'daniela.torchi@gmail.com']:
    print(f"\n--- ASAAS DATA FOR {em} ---")
    st = asaas.get('data', {}).get(em)
    if st:
        print("Keys:", list(st.keys()))
        print("Aluno:", st.get('aluno') or st.get('customer_name'))
        print("Curso:", st.get('curso'))
        print("Description:", st.get('description'))
        print("Valor:", st.get('valor_parcela'))
        print("Payments count:", len(st.get('faturas', [])))
        for p in st.get('faturas', []):
            print("  Payment:", p.get('id'), p.get('valor'), p.get('description'), p.get('status'), p.get('vencimento'), p.get('data_pagamento'))
