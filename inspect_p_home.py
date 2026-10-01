with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's inspect from <section class="panel" id="p-home"> to <section class="panel" id="p-prog">
start = html.find('<section class="panel" id="p-home">')
end = html.find('<section class="panel" id="p-prog">')
chunk = html[start:end].encode('ascii', 'replace').decode('ascii')
print(chunk)
