import re
import json
from collections import defaultdict

# 1. Parse text and find all estornos
with open("transactions_debug.txt", "r", encoding="utf-8") as f:
    text = f.read()

day_blocks = text.split("==================== DATE: ")

all_outflows = []
all_estornos = []
daily_summary = []

def categorize_outflow(desc):
    d_upper = desc.upper()
    if "PAGAMENTO DE FATURA" in d_upper:
        return "Cartão de Crédito / Fatura", "Cartão PJ (Nubank)"
    if "RECEITA FEDERAL" in d_upper or "DARF" in d_upper or "SIMPLES NACIONAL" in d_upper or "PREFEITURA" in d_upper:
        return "Impostos & Tributos", "Receita Federal / Tributos"
    if "QUINTOANDAR" in d_upper or "QUINTO ANDAR" in d_upper:
        return "Aluguel & Infraestrutura", "QuintoAndar (Aluguel/Sede)"
    if "CONTASS" in d_upper or "ASSESSORIA CONTABIL" in d_upper:
        return "Contabilidade & Jurídico", "Contass Assessoria Contábil"
    if "ADVOGAD" in d_upper or "OAB" in d_upper or "JURIDIC" in d_upper:
        return "Contabilidade & Jurídico", "Assessoria Jurídica"
    if "ELLEMENTAR" in d_upper or "ESTUDIO DE FOTO" in d_upper:
        return "Produção Audiovisual & Marketing", "Ellementar Estúdio Foto e Filme"
    if "NANI.COM" in d_upper or "NANI" in d_upper:
        return "Produção Audiovisual & Marketing", "Nani.com (Marketing/Agência)"
    if "FOTO" in d_upper or "FILME" in d_upper or "AUDIOVISUAL" in d_upper:
        return "Produção Audiovisual & Marketing", "Audiovisual / Mídia"
    if "JOSE RAND" in d_upper or "JOSÉ RAND" in d_upper:
        return "Sócios / Distribuição", "José Rand de Sousa Costa"
    if "ESTER ARAUJO" in d_upper or "ESTER ARAÚJO" in d_upper:
        return "Sócios / Distribuição", "Ester Araujo da Silva Fortunato"
    if any(k in d_upper for k in ["SERVICOS MEDICOS", "SERVIÇOS MÉDICOS", "MEDICOS", "MÉDICOS", "INFECTOPEDS", "FACULDADE DE MEDICINA", "FUNDACAO FACULDADE"]):
        if "INFECTOPEDS" in d_upper:
            return "Corpo Docente & Especialistas", "InfectoPeds Serviços Médicos"
        if "FACULDADE DE MEDICINA" in d_upper:
            return "Parcerias Acadêmicas & Certificação", "Fundação Faculdade de Medicina"
        return "Corpo Docente & Especialistas", "Serviços Médicos / Professores"
    return "Professores & Prestadores PF", "Honorários / Prestadores"

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
        if "Total de entradas" in l:
            in_entradas = True
            in_saidas = False
            m = re.search(r'Total de entradas\s*\+\s*([\d\.,]+)', l)
            if m: total_ent = float(m.group(1).replace('.', '').replace(',', '.'))
        elif "Total de saídas" in l or "Total de saidas" in l:
            in_saidas = True
            in_entradas = False
            m = re.search(r'Total de sa[íi]das\s*-\s*([\d\.,]+)', l)
            if m: total_sai = float(m.group(1).replace('.', '').replace(',', '.'))
        elif "Saldo do dia" in l:
            in_saidas = False
            in_entradas = False
            m = re.search(r'Saldo do dia\s*([\d\.,]+)', l)
            if m: saldo_dia = float(m.group(1).replace('.', '').replace(',', '.'))
        else:
            if in_saidas:
                saida_lines.append(l)
            elif in_entradas:
                entrada_lines.append(l)

    # 1. Detect estornos in entradas for this day
    clean_ent_lines = []
    for l in entrada_lines:
        clean_l = re.sub(r'\[.*?\]\[.*?\]\s*', '', l)
        if any(ign in clean_l for ign in ["INFECTOCAST SERVICOS", "CNPJ 54.", "476440809-8", "01 DE SETEMBRO", "VALORES EM R$", "Tem alguma dúvida", "metropolitanas", "Caso a solução", "disponíveis em", "Extrato gerado"]):
            continue
        clean_ent_lines.append(clean_l)
    full_ent_text = " ".join(clean_ent_lines)

    # Find estornos in entradas
    # Pattern: Estorno - Transferência enviada pelo (Pix)? <DESC> <VALOR>
    estorno_matches = re.finditer(r'Estorno\s*-\s*Transferência enviada pelo (?:Pix)?\s*(.*?)\s*([\d\.]+,\d{2})', full_ent_text, re.IGNORECASE)
    day_estornos = []
    for em in estorno_matches:
        e_desc = em.group(1).strip()
        e_val = float(em.group(2).replace('.', '').replace(',', '.'))
        day_estornos.append({
            "data": date_str,
            "descricao": e_desc,
            "valor": e_val
        })
        all_estornos.append({
            "data": date_str,
            "descricao": e_desc,
            "valor": e_val
        })

    # 2. Extract raw saidas for this day
    clean_sai_lines = []
    for l in saida_lines:
        clean_l = re.sub(r'\[.*?\]\[.*?\]\s*', '', l)
        if any(ign in clean_l for ign in ["INFECTOCAST SERVICOS", "CNPJ 54.", "476440809-8", "01 DE SETEMBRO", "VALORES EM R$", "Tem alguma dúvida", "metropolitanas", "Caso a solução", "disponíveis em", "Extrato gerado"]):
            continue
        clean_sai_lines.append(clean_l)
    full_sai_text = " ".join(clean_sai_lines)

    sai_matches = re.finditer(r'(Pagamento de fatura|Transferência enviada pelo Pix|Pagamento de boleto efetuado)\s*(.*?)\s*([\d\.]+,\d{2})', full_sai_text, re.IGNORECASE)
    day_items = []
    for sm in sai_matches:
        t_type = sm.group(1).strip()
        t_desc = sm.group(2).strip()
        t_val = float(sm.group(3).replace('.', '').replace(',', '.'))
        cat, subcat = categorize_outflow(t_type + " " + t_desc)
        day_items.append({
            "data": date_str,
            "dia": int(date_str.split('/')[0]),
            "tipo": t_type,
            "descricao_raw": t_desc,
            "categoria": cat,
            "subcategoria": subcat,
            "valor": t_val,
            "estornado": False
        })

    # 3. Pair and cancel matching estornos against saidas
    estornos_valor_dia = 0.0
    for est in day_estornos:
        est_val = est["valor"]
        est_desc_clean = re.sub(r'[\d\.\-\/•]', '', est["descricao"]).strip().lower()
        
        # find matching salida that is not yet marked as estornado
        matched = False
        for item in day_items:
            if not item["estornado"] and abs(item["valor"] - est_val) < 0.01:
                item_desc_clean = re.sub(r'[\d\.\-\/•]', '', item["descricao_raw"]).strip().lower()
                # Check similarity or common words in name
                if any(w in item_desc_clean for w in est_desc_clean.split() if len(w) > 3) or not est_desc_clean:
                    item["estornado"] = True
                    estornos_valor_dia += est_val
                    matched = True
                    break
        if not matched:
            print(f"Aviso: Estorno de {est_val} em {date_str} não encontrou par exato de saída.")

    # Only keep NON-estornado items
    valid_items = [it for it in day_items if not it["estornado"]]
    
    # Adjust daily totals to reflect net movements (eliminating the inflated fake entries)
    net_entradas = total_ent - estornos_valor_dia
    net_saidas = total_sai - estornos_valor_dia

    daily_summary.append({
        "data": date_str,
        "dia": int(date_str.split('/')[0]),
        "entradas_brutas": total_ent,
        "entradas": round(net_entradas, 2),
        "saidas_brutas": total_sai,
        "saidas": round(net_saidas, 2),
        "estornos": round(estornos_valor_dia, 2),
        "saldo": saldo_dia,
        "items": valid_items
    })

    for it in valid_items:
        all_outflows.append(it)

print(f"Total Estornos identificados e anulados: {len(all_estornos)}")
total_estornos_val = sum(e['valor'] for e in all_estornos)
print(f"Valor Total de Estornos Anulados: R$ {total_estornos_val:,.2f}")

print(f"\nTotal Lançamentos Reais de Saída após anulação: {len(all_outflows)} (antes: 90)")
total_saidas_liquidas = sum(d['saidas'] for d in daily_summary)
total_entradas_liquidas = sum(d['entradas'] for d in daily_summary)

print(f"Total Entradas Líquidas: R$ {total_entradas_liquidas:,.2f} (antes: R$ 360.727,66)")
print(f"Total Saídas Líquidas:   R$ {total_saidas_liquidas:,.2f} (antes: R$ 470.870,94)")
print(f"Resultado Líquido do Mês: R$ {(total_entradas_liquidas - total_saidas_liquidas):,.2f}")

# Categoria breakdown após eliminação dos estornos
cat_totals = defaultdict(float)
cat_counts = defaultdict(int)
for it in all_outflows:
    cat_totals[it["categoria"]] += it["valor"]
    cat_counts[it["categoria"]] += 1

print("\n--- DISTRIBUIÇÃO POR CATEGORIA SANEADA (SEM ESTORNOS) ---")
for cat, val in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
    pct = (val / total_saidas_liquidas) * 100
    print(f"{cat:<35} | R$ {val:>10.2f} | {pct:>5.1f}% | ({cat_counts[cat]} lançamentos)")

# Beneficiários após anulação
benef_map = defaultdict(lambda: {"total": 0.0, "count": 0, "categoria": ""})
for it in all_outflows:
    raw = it['descricao_raw']
    t_type = it['tipo']
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
    elif t_type == "Pagamento de fatura":
        name = "Fatura Cartão de Crédito PJ (Nubank)"
    else:
        parts = raw.split("-")[0].strip()
        name = parts if len(parts) > 3 else raw

    benef_map[name]["total"] += it["valor"]
    benef_map[name]["count"] += 1
    benef_map[name]["categoria"] = it["categoria"]

print("\n--- TOP BENEFICIÁRIOS SANEADOS (SEM ESTORNOS) ---")
for b_name, b_info in sorted(benef_map.items(), key=lambda x: x[1]["total"], reverse=True)[:15]:
    pct = (b_info["total"] / total_saidas_liquidas) * 100
    print(f"{b_name:<45} | R$ {b_info['total']:>10.2f} ({pct:>4.1f}%) | {b_info['count']:>2d}x | {b_info['categoria']}")

# Save clean analysis
with open("extrato_setembro_analise.json", "w", encoding="utf-8") as f_out:
    json.dump({
        "daily_summary": daily_summary,
        "outflow_items": all_outflows,
        "category_totals": cat_totals,
        "estornos_anulados": all_estornos
    }, f_out, ensure_ascii=False, indent=2)

print("\nSaved updated extrato_setembro_analise.json with estornos purged!")
