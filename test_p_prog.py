with open('c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's inspect p-prog HTML
p_prog_start = html.find('id="p-prog"')
p_prog_end = html.find('</section>', p_prog_start)
print(html[p_prog_start-50:p_prog_end+20])
