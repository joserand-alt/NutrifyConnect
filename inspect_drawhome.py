import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect drawHome in original_template.html
pos_home = text.find('function drawHome')
pos_funil = text.find('function drawFunil')
print(f"drawHome pos: {pos_home}, drawFunil pos: {pos_funil}")

print("--- drawHome snippet (first 1000 chars) ---")
print(text[pos_home:pos_home+1000])

print("--- drawHome end (1000 chars before drawFunil) ---")
print(text[pos_funil-1000:pos_funil])
