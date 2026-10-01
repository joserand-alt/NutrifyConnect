with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<main class="hud-main-content">')
end = html.find('</main>')
chunk = html[start:start+3000].encode('ascii', 'replace').decode('ascii')
print(chunk)
