import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_g6 = text.find('GRUPO 6 —')
pos_g7 = text.find('GRUPO 7 —')
pos_g8 = text.find('GRUPO 8 —')

print(f"G6 pos: {pos_g6}, G7 pos: {pos_g7}, G8 pos: {pos_g8}")
print("--- G7 Section and surrounding context ---")
print(text[pos_g7-500:pos_g8+1500])
