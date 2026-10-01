import json

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_cache.json', 'r', encoding='utf-8') as f:
    cache = json.load(f)

data = cache.get('data', {})

target_emails = [
    'welisoncatarino13@hotmail.com', 'rafael.farmaco@gmail.com',
    'limafilipe13@hotmail.com', 'souzaxp4i@gmail.com',
    'adrianammas@gmail.com', 'kyllianmunhoz@gmail.com',
    'gcotta29@gmail.com', 'costalg1@gmail.com',
    'laura_orlandi@hotmail.com', 'mclaramdp@gmail.com',
    'markus_braga@hotmail.com', 'daniela.torchi@gmail.com',
    'danielesarto@yahoo.com.br'
]

for k, v in data.items():
    email = (v.get('customer_email') or '').lower()
    if email in target_emails:
        nome = v.get('customer_name', '?')
        faturas = v.get('faturas', [])
        
        # Get all unique descriptions
        descs = set()
        planos = set()
        for ft in faturas:
            d = ft.get('description', '')
            p = ft.get('plano', '')
            if d: descs.add(d)
            if p: planos.add(p)
        
        total_bruto = sum(ft.get('valor', 0) for ft in faturas)
        
        print(f"{nome} ({email})")
        print(f"  Key: {k}")
        print(f"  Total faturas: {len(faturas)}")
        print(f"  Total bruto: R$ {total_bruto:.2f}")
        print(f"  Descriptions: {descs}")
        print(f"  Planos: {planos}")
        print()
