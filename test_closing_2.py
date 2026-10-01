with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('home-chart-range-label')
end = html.find('id="p-prog"')
print(html[start:end].encode('ascii', 'replace').decode('ascii'))
