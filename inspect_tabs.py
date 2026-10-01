import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

print("Searching tab navigation...")
# Find tab navigation in JS
for m in re.finditer(r'document\.querySelectorAll\([\'"]\.tab[\'"]\)|function switchTab|p-financeiro|p-fin|data-p="fin"|data-p="financeiro"', text):
    idx = m.start()
    snippet = text[max(0, idx-50):min(len(text), idx+300)]
    print(f"Match at {idx}:\n{snippet}\n---")

# Also find where _fin is called or where pages are activated
for m in re.finditer(r'page === [\'"]fin|page === [\'"]financeiro|p === [\'"]fin|target === [\'"]fin', text):
    idx = m.start()
    snippet = text[max(0, idx-50):min(len(text), idx+300)]
    print(f"Page match at {idx}:\n{snippet}\n---")
