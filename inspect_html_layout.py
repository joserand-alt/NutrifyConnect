import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect where #kpis, .filters, and tab panels are placed in HTML
pos_body = text.find('<body>')
pos_nav = text.find('<nav class="tabs"')
pos_script = text.find('<script>')

print("--- HTML between <body> and <nav> ---")
print(text[pos_body:pos_nav])

print("--- HTML between <nav> and <script> ---")
print(text[pos_nav:pos_nav+3000])
