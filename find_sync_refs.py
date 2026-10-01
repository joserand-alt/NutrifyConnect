with open('template.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [(m.start(), m.group(0)) for m in re.finditer(r'(getSync24hData|openModalSync24h|closeSyncModal24h|renderSync24hTable|_syncedStudentsList24h|modal-sync-24h|api-cnt-sync24h)', content)]
print(f"Total matches: {len(matches)}")
for pos, txt in matches:
    print(f"Pos {pos}: {txt}")
