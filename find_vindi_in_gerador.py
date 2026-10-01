import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\gerador.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('vindi')
while pos != -1:
    print(text[max(0, pos-40):min(len(text), pos+150)])
    print("---")
    pos = text.find('vindi', pos+100)
