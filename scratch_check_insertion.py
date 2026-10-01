with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Inspect header buttons section
idx_sync24h = text.find('id="api-cnt-sync24h"')
print('idx_sync24h:', idx_sync24h)
if idx_sync24h != -1:
    print('--- CONTEXT AROUND SYNC24H ---')
    print(text[idx_sync24h-200:idx_sync24h+400])

# 2. Inspect end of script tags in template.html
idx_script_end = text.rfind('</script>')
print('Last </script> at:', idx_script_end)
