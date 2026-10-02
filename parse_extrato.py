import pdfplumber
import re
import json
from collections import defaultdict

pdf_path = r"C:\Users\DELL\Downloads\662fb63c-ec99-4d33-8d14-d018c5021603-2026-09-01-2026-09-30.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    full_text = []
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"\n--- PAGE {i+1} (Length: {len(text) if text else 0}) ---")
        if text:
            print(text[:500])
            full_text.append(text)

joined_text = "\n".join(full_text)
with open("extracted_extrato.txt", "w", encoding="utf-8") as f:
    f.write(joined_text)
print("\nExtracted full text to extracted_extrato.txt")
