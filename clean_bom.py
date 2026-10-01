import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'rb') as f:
    raw = f.read()

# Strip UTF-8 BOM if present
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]

text = raw.decode('utf-8')
# Clean any non-printable BOM
text = text.replace('\ufeff', '')

# Ensure import re and other imports are clean
if 'import re' not in text:
    text = 'import re\n' + text

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS: UTF-8 BOM removed and asaas_service.py cleaned!")
