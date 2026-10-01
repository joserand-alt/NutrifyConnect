import json

with open('academy_students_cache.json', 'r', encoding='utf-8') as f:
    st_acad = json.load(f)

with open('academy_logs_cache.json', 'r', encoding='utf-8') as f:
    logs_acad = json.load(f)

print(f"Total students in academy cache: {len(st_acad)}")
print(f"Total logs in academy cache: {len(logs_acad)}")

# Check Daniele Sarto
dan_logs = [l for l in logs_acad if 'danielesarto' in l.get('E-mail', '') or 'daniele' in l.get('Nome aluno', '').lower()]
print(f"Daniele Sarto logs count: {len(dan_logs)}")
if dan_logs:
    print("Sample logs for Daniele Sarto:")
    for l in dan_logs[:5]:
        print(" ", l)

# Check courses inferred from logs
daniele_items = [l.get('Desc. Item') or l.get('ID Item') for l in dan_logs]
print("Daniele log items sample:", daniele_items[:10])
