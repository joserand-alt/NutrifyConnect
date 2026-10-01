import sys

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html', 'r', encoding='utf-8-sig') as f:
    text = f.read()

pos_header_end = text.find('</header>')
sys.stdout.buffer.write(text[pos_header_end:pos_header_end+2000].encode('utf-8'))
