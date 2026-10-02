import json
from collections import defaultdict

with open("extrato_setembro_analise.json", "r", encoding="utf-8") as f:
    data = json.load(f)

daily = data["daily_summary"]
items = data["outflow_items"]
categories = data["category_totals"]

print("==================== TOP DIAS DE SAÍDA DE CAIXA ====================")
sorted_days = sorted(daily, key=lambda x: x["saidas"], reverse=True)
for d in sorted_days:
    if d["saidas"] > 0:
        net = d["entradas"] - d["saidas"]
        print(f"Dia {d['data']} | Saídas: R$ {d['saidas']:>10.2f} | Entradas: R$ {d['entradas']:>10.2f} | Líquido: R$ {net:>10.2f} | Saldo Final: R$ {d['saldo']:>10.2f}")

print("\n==================== TOP 15 MAIORES LANÇAMENTOS DE SAÍDA ====================")
sorted_items = sorted(items, key=lambda x: x["valor"], reverse=True)
for i, item in enumerate(sorted_items[:20], 1):
    desc = item['descricao_raw'][:60]
    print(f"{i:2d}. {item['data']} | R$ {item['valor']:>10.2f} | {item['categoria']:<30} | {item['tipo']} {desc}")

print("\n==================== AGRUPAMENTO POR BENEFICIÁRIO / DESTINO ====================")
beneficiarios = defaultdict(lambda: {"total": 0.0, "count": 0, "categoria": ""})

for item in items:
    # simplify name
    raw = item['descricao_raw']
    # extract name before CPF/CNPJ or agency
    name = raw
    if "José Rand" in raw or "JOSÉ RAND" in raw:
        name = "José Rand de Sousa Costa (Sócio)"
    elif "ESTER ARAUJO" in raw.upper():
        name = "Ester Araujo da Silva Fortunato (Sócia)"
    elif "WILLIAM DUNKE" in raw.upper():
        name = "William Dunke de Lima"
    elif "INFECTOPEDS" in raw.upper():
        name = "InfectoPeds Serviços Médicos"
    elif "NANI.COM" in raw.upper() or "NANI" in raw.upper():
        name = "Nani.com (Marketing / Agência)"
    elif "ELLEMENTAR" in raw.upper():
        name = "Ellementar Estúdio Foto e Filme"
    elif "FACULDADE DE MEDICINA" in raw.upper():
        name = "Fundação Faculdade de Medicina"
    elif "QUINTOANDAR" in raw.upper() or "QUINTO ANDAR" in raw.upper():
        name = "QuintoAndar (Aluguel/Sede)"
    elif "GABRIELA INGRID" in raw.upper():
        name = "Gabriela Ingrid da Silva"
    elif "RECEITA FEDERAL" in raw.upper() or "DARF" in raw.upper():
        name = "Receita Federal (Tributos/DARF)"
    elif item['tipo'] == "Pagamento de fatura":
        name = "Fatura Cartão de Crédito PJ (Nubank)"
    else:
        # clean simple name
        parts = raw.split('-')[0].strip()
        name = parts if len(parts) > 3 else raw
        
    beneficiarios[name]["total"] += item["valor"]
    beneficiarios[name]["count"] += 1
    beneficiarios[name]["categoria"] = item["categoria"]

for b_name, b_info in sorted(beneficiarios.items(), key=lambda x: x[1]["total"], reverse=True):
    pct = (b_info["total"] / 470870.94) * 100
    print(f"{b_name:<45} | R$ {b_info['total']:>10.2f} ({pct:>4.1f}%) | {b_info['count']:>2d}x | {b_info['categoria']}")
