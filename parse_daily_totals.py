import re
import json

with open("extracted_extrato.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect the entire document structure by splitting lines
lines = [l.strip() for l in text.split("\n") if l.strip()]

days_data = []
current_day = None

# Months map
months = {
    'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04', 'MAI': '05', 'JUN': '06',
    'JUL': '07', 'AGO': '08', 'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
}

print("Searching for daily summaries in text...")
day_header_regex = re.compile(r'(\d{1,2})\s+(SET|AGO|OUT)\s+2026', re.IGNORECASE)
total_entradas_regex = re.compile(r'Total de entradas\s*\+\s*([\d\.,]+)', re.IGNORECASE)
total_saidas_regex = re.compile(r'Total de sa[íi]das\s*-\s*([\d\.,]+)', re.IGNORECASE)
saldo_dia_regex = re.compile(r'Saldo do dia\s*([\d\.,]+)', re.IGNORECASE)

# Let's scan lines
i = 0
parsed_days = {}
current_date_str = None

while i < len(lines):
    line = lines[i]
    
    # Check day match
    m_day = day_header_regex.search(line)
    if m_day:
        d_num = m_day.group(1).zfill(2)
        m_month = months.get(m_day.group(2).upper(), '09')
        current_date_str = f"{d_num}/{m_month}/2026"
        if current_date_str not in parsed_days:
            parsed_days[current_date_str] = {
                "date": current_date_str,
                "day_num": int(d_num),
                "entradas": 0.0,
                "saidas": 0.0,
                "saldo": None,
                "raw_transactions": []
            }
            
    # Check total entradas
    m_ent = total_entradas_regex.search(line)
    if m_ent and current_date_str:
        val = float(m_ent.group(1).replace('.', '').replace(',', '.'))
        parsed_days[current_date_str]["entradas"] = val

    # Check total saidas
    m_sai = total_saidas_regex.search(line)
    if m_sai and current_date_str:
        val = float(m_sai.group(1).replace('.', '').replace(',', '.'))
        parsed_days[current_date_str]["saidas"] = val

    # Check saldo dia
    m_sal = saldo_dia_regex.search(line)
    if m_sal and current_date_str:
        val = float(m_sal.group(1).replace('.', '').replace(',', '.'))
        parsed_days[current_date_str]["saldo"] = val

    i += 1

print("\n--- RESUMO DE DIAS IDENTIFICADOS ---")
for d, info in sorted(parsed_days.items(), key=lambda x: x[1]['day_num']):
    print(f"Data: {d} | Entradas: R$ {info['entradas']:>10.2f} | Saídas: R$ {info['saidas']:>10.2f} | Saldo: {info['saldo']}")

total_saidas_mes = sum(info['saidas'] for info in parsed_days.values())
total_entradas_mes = sum(info['entradas'] for info in parsed_days.values())
print(f"\nTOTAL ENTRADAS SET/2026: R$ {total_entradas_mes:,.2f}")
print(f"TOTAL SAÍDAS SET/2026:   R$ {total_saidas_mes:,.2f}")
print(f"SALDO LÍQUIDO MÊS:       R$ {(total_entradas_mes - total_saidas_mes):,.2f}")
