import re
import json
from collections import defaultdict

# Let's inspect the exact lines of 02/09, 04/09, 21/09 in transactions_debug.txt
with open("transactions_debug.txt", "r", encoding="utf-8") as f:
    text = f.read()

days = text.split("==================== DATE: ")

for d in days[1:]:
    lines = [l.strip() for l in d.split("\n") if l.strip()]
    d_str = lines[0].replace("=", "").strip()
    if d_str in ["02/09/2026", "04/09/2026", "21/09/2026"]:
        print(f"\n==================== {d_str} ====================")
        for l in lines[1:]:
            if any(k in l for k in ["Total de", "Saldo do dia", "William Dunke", "ESTER ARAUJO", "Ester Araujo", "Unidade Oetopedica"]):
                print("  ", l)
