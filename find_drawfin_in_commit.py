import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8')

out = subprocess.run(['git', 'show', '69501e6:template.html'], cwd=r'C:\Users\DELL\Desktop\Dash_InfectoCast', capture_output=True)
text = out.stdout.decode('utf-8', errors='ignore')

pos = text.find('function drawFinanceiro')
print('function drawFinanceiro pos in 69501e6:', pos)
if pos != -1:
    print(text[pos:pos+1500])
