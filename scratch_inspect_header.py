with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('<header')
end_pos = text.find('</header>', pos)
header_html = text[pos:end_pos+9]
print("Header Length:", len(header_html))
with open('header_snippet.html', 'w', encoding='utf-8') as out:
    out.write(header_html)
print("Saved header_snippet.html")
