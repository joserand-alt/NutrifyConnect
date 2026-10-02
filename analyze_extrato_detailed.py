import re
import json
from collections import defaultdict

with open("transactions_debug.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's parse all transactions per day
# A day block starts with "==================== DATE: DD/09/2026 ===================="
# Within a day block, between "Total de saídas" and "Saldo do dia", we have individual outflow entries.

day_blocks = text.split("==================== DATE: ")

all_outflows = []
all_inflows = []
daily_summary = []

for block in day_blocks[1:]:
    lines = [l.strip() for l in block.split("\n") if l.strip()]
    if not lines:
        continue
    
    date_str = lines[0].replace("=", "").strip()
    
    in_saidas = False
    in_entradas = False
    
    total_ent = 0.0
    total_sai = 0.0
    saldo_dia = 0.0
    
    saida_lines = []
    entrada_lines = []
    
    for l in lines[1:]:
        # check header indicators
        if "Total de entradas" in l:
            in_entradas = True
            in_saidas = False
            m = re.search(r'Total de entradas\s*\+\s*([\d\.,]+)', l)
            if m:
                total_ent = float(m.group(1).replace('.', '').replace(',', '.'))
        elif "Total de saídas" in l or "Total de saidas" in l:
            in_saidas = True
            in_entradas = False
            m = re.search(r'Total de sa[íi]das\s*-\s*([\d\.,]+)', l)
            if m:
                total_sai = float(m.group(1).replace('.', '').replace(',', '.'))
        elif "Saldo do dia" in l:
            in_saidas = False
            in_entradas = False
            m = re.search(r'Saldo do dia\s*([\d\.,]+)', l)
            if m:
                saldo_dia = float(m.group(1).replace('.', '').replace(',', '.'))
        else:
            if in_saidas:
                saida_lines.append(l)
            elif in_entradas:
                entrada_lines.append(l)
                
    daily_summary.append({
        "data": date_str,
        "dia": int(date_str.split('/')[0]),
        "entradas": total_ent,
        "saidas": total_sai,
        "saldo": saldo_dia,
        "raw_saidas": saida_lines,
        "raw_entradas": entrada_lines
    })

print(f"Total days parsed: {len(daily_summary)}")

# Helper to categorize beneficiary/description
def categorize_outflow(desc):
    d_upper = desc.upper()
    
    # Cartão de crédito / Fatura
    if "PAGAMENTO DE FATURA" in d_upper:
        return "Cartão de Crédito / Fatura", "Cartão PJ (Nubank)"
        
    # Impostos / Governo
    if "RECEITA FEDERAL" in d_upper or "DARF" in d_upper or "SIMPLES NACIONAL" in d_upper or "PREFEITURA" in d_upper:
        return "Impostos & Tributos", "Receita Federal / Tributos"
        
    # Aluguel / Imóvel
    if "QUINTOANDAR" in d_upper or "QUINTO ANDAR" in d_upper:
        return "Aluguel & Infraestrutura", "QuintoAndar (Aluguel/Sede)"
        
    # Contabilidade & Jurídico
    if "CONTASS" in d_upper or "ASSESSORIA CONTABIL" in d_upper:
        return "Contabilidade & Jurídico", "Contass Assessoria Contábil"
    if "ADVOGAD" in d_upper or "OAB" in d_upper or "JURIDIC" in d_upper:
        return "Contabilidade & Jurídico", "Assessoria Jurídica"
        
    # Produção audiovisual / Marketing / Design / Foto e Filme
    if "ELLEMENTAR" in d_upper or "ESTUDIO DE FOTO" in d_upper:
        return "Produção Audiovisual & Marketing", "Ellementar Estúdio Foto e Filme"
    if "NANI.COM" in d_upper or "NANI" in d_upper:
        return "Produção Audiovisual & Marketing", "Nani.com (Marketing/Agência)"
    if "FOTO" in d_upper or "FILME" in d_upper or "AUDIOVISUAL" in d_upper:
        return "Produção Audiovisual & Marketing", "Audiovisual / Mídia"
        
    # Sócios / Retirada / Pró-labore
    if "JOSE RAND" in d_upper or "JOSÉ RAND" in d_upper:
        return "Sócios / Distribuição", "José Rand de Sousa Costa"
    if "ESTER ARAUJO" in d_upper or "ESTER ARAÚJO" in d_upper:
        return "Sócios / Distribuição", "Ester Araujo da Silva Fortunato"
        
    # Médicos, Professores & Equipe de Conteúdo
    if any(k in d_upper for k in ["SERVICOS MEDICOS", "SERVIÇOS MÉDICOS", "MEDICOS", "MÉDICOS", "INFECTOPEDS", "FACULDADE DE MEDICINA", "FUNDACAO FACULDADE"]):
        if "INFECTOPEDS" in d_upper:
            return "Corpo Docente & Especialistas", "InfectoPeds Serviços Médicos"
        if "FACULDADE DE MEDICINA" in d_upper:
            return "Parcerias Acadêmicas & Certificação", "Fundação Faculdade de Medicina"
        return "Corpo Docente & Especialistas", "Serviços Médicos / Professores"
        
    # Pessoas físicas (Geralmente professores, palestrantes, consultores)
    return "Professores & Prestadores PF", "Honorários / Prestadores"

# Let's extract items from saida_lines
parsed_outflow_items = []

for d in daily_summary:
    raw_s = "\n".join(d["raw_saidas"])
    # clean footer and headers noise
    clean_lines = []
    for l in d["raw_saidas"]:
        # remove prefix like [01/09/2026][S=True, E=False]
        clean_l = re.sub(r'\[.*?\]\[.*?\]\s*', '', l)
        if any(ign in clean_l for ign in ["INFECTOCAST SERVICOS", "CNPJ 54.", "476440809-8", "01 DE SETEMBRO", "VALORES EM R$", "Tem alguma dúvida", "metropolitanas", "Caso a solução", "disponíveis em", "Extrato gerado"]):
            continue
        clean_lines.append(clean_l)
        
    full_day_text = " ".join(clean_lines)
    
    # We can split by transaction patterns:
    # "Pagamento de fatura", "Transferência enviada pelo Pix", "Pagamento de boleto efetuado"
    # Match pattern: (Pagamento de fatura|Transferência enviada pelo Pix|Pagamento de boleto efetuado)(.*?)([\d\.]+,\d{2})
    
    # Let's use regex to find all transactions in full_day_text
    matches = re.finditer(r'(Pagamento de fatura|Transferência enviada pelo Pix|Pagamento de boleto efetuado)\s*(.*?)\s*([\d\.]+,\d{2})', full_day_text, re.IGNORECASE)
    
    day_items = []
    for m in matches:
        t_type = m.group(1).strip()
        t_desc = m.group(2).strip()
        t_val = float(m.group(3).replace('.', '').replace(',', '.'))
        
        # clean description from agency/account noise if any
        # extract primary beneficiary name
        beneficiary = t_desc
        # simplify beneficiary
        cat, subcat = categorize_outflow(t_type + " " + t_desc)
        
        item = {
            "data": d["data"],
            "dia": d["dia"],
            "tipo": t_type,
            "descricao_raw": t_desc,
            "categoria": cat,
            "subcategoria": subcat,
            "valor": t_val
        }
        day_items.append(item)
        parsed_outflow_items.append(item)
        
    d["items"] = day_items
    d["items_sum"] = sum(x["valor"] for x in day_items)

print(f"\nTotal individual outflow items parsed: {len(parsed_outflow_items)}")
print(f"Total calculated sum of items: R$ {sum(x['valor'] for x in parsed_outflow_items):,.2f}")
print(f"Total statement sum of saidas: R$ {sum(d['saidas'] for d in daily_summary):,.2f}")

# Category breakdown
category_totals = defaultdict(float)
category_count = defaultdict(int)
for item in parsed_outflow_items:
    category_totals[item["categoria"]] += item["valor"]
    category_count[item["categoria"]] += 1

print("\n--- DISTRIBUIÇÃO POR CATEGORIA DE SAÍDA (SETEMBRO/2026) ---")
for cat, val in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
    pct = (val / sum(category_totals.values())) * 100 if sum(category_totals.values()) else 0
    print(f"{cat:<35} | R$ {val:>10.2f} | {pct:>5.1f}% | ({category_count[cat]} lançamentos)")

# Save rich JSON
with open("extrato_setembro_analise.json", "w", encoding="utf-8") as f_out:
    json.dump({
        "daily_summary": daily_summary,
        "outflow_items": parsed_outflow_items,
        "category_totals": category_totals
    }, f_out, ensure_ascii=False, indent=2)

print("\nSaved extrato_setembro_analise.json")
