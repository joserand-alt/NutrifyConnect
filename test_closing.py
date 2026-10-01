with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's inspect lines 1450 to 1470
start = html.find('id="home-hourly-chart-container"')
print(html[start:start+400])
