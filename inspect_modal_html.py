with open('template.html', 'r', encoding='utf-8') as f:
    content = f.read()

pos = content.find('id="modal-sync-24h"')
print('pos:', pos)
if pos != -1:
    print(content[pos-100:pos+3000].encode('ascii', 'replace').decode('ascii'))
