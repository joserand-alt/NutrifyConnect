import pdfplumber
import re
import json
from collections import defaultdict

pdf_path = r"C:\Users\DELL\Downloads\662fb63c-ec99-4d33-8d14-d018c5021603-2026-09-01-2026-09-30.pdf"

months = {
    'SET': '09', 'AGO': '08', 'OUT': '10'
}

with pdfplumber.open(pdf_path) as pdf:
    full_text_pages = [page.extract_text() for page in pdf.pages if page.extract_text()]

all_text = "\n".join(full_text_pages)

# Let's inspect transaction types in Nubank statement
# Patterns:
# - Transferência enviada pelo Pix <BENEFICIARIO> <VALOR>
# - Pagamento de fatura <VALOR>
# - Pagamento de boleto efetuado <BENEFICIARIO> <VALOR>
# - Transferência recebida pelo Pix <ORIGEM> <VALOR>
# - Depósito recebido <ORIGEM> <VALOR>

transactions = []
current_date = None

lines = [l.strip() for l in all_text.split("\n") if l.strip()]

# Regex to detect date section
date_regex = re.compile(r'^(\d{1,2})\s+(SET|AGO|OUT)\s+2026', re.IGNORECASE)

# Value extraction regex at end of line or in line
# Brazilian currency format: 12.345,67 or 345,67
val_regex = re.compile(r'([\d\.]+,\d{2})$')

def parse_val(v_str):
    return float(v_str.replace('.', '').replace(',', '.'))

# Let's write a smarter block parser
# Let's see how each day's transactions are structured

with open("transactions_debug.txt", "w", encoding="utf-8") as out_f:
    current_day_str = "01/09/2026"
    in_saidas = False
    in_entradas = False
    
    for idx, line in enumerate(lines):
        m_d = date_regex.match(line)
        if m_d:
            d_num = m_d.group(1).zfill(2)
            current_day_str = f"{d_num}/09/2026"
            in_saidas = False
            in_entradas = False
            out_f.write(f"\n==================== DATE: {current_day_str} ====================\n")
            
        if "Total de saídas" in line or "Total de saidas" in line:
            in_saidas = True
            in_entradas = False
        elif "Total de entradas" in line:
            in_entradas = True
            in_saidas = False
        elif "Saldo do dia" in line:
            in_saidas = False
            in_entradas = False
            
        out_f.write(f"[{current_day_str}][S={in_saidas}, E={in_entradas}] {line}\n")

print("Wrote transaction debug log to transactions_debug.txt")
