import sys, os
sys.path.insert(0, r"c:\Users\DELL\Desktop\Dash_InfectoCast")
import json, datetime
import pandas as pd

# Check Cativa API
import cativa_api
try:
    cativa_data = cativa_api.fetch_all_cativa_data(force_refresh=True)
    c_students = cativa_data.get('students', [])
    c_meta = cativa_data.get('users_metadata', {})
    print(f"Cativa total students: {len(c_students)}, users_meta: {len(c_meta)}")
    
    # Check created_at or last_login in Cativa
    recent_cativa = []
    for s in c_students:
        created = s.get('created_at') or s.get('createdAt') or ''
        recent_cativa.append((created, s.get('name') or s.get('fullName'), s.get('email'), s.get('status')))
    
    for em, m in c_meta.items():
        cr = m.get('created_at') or m.get('createdAt') or ''
        ll = m.get('last_login_at') or ''
        recent_cativa.append((cr or ll, f"{m.get('first_name','')} {m.get('last_name','')}", em, 'meta'))
        
    recent_cativa.sort(key=lambda x: str(x[0]), reverse=True)
    print("Recent Cativa records:")
    for r in recent_cativa[:15]:
        print("  Cativa:", r)
except Exception as e:
    print("Cativa error:", e)

# Check RD Station
try:
    with open(r"c:\Users\DELL\Desktop\Dash_InfectoCast\rd_students_cache.json", 'r', encoding='utf-8') as f:
        rd_data = json.load(f)
    print(f"RD Station cache students: {len(rd_data)}")
except Exception as e:
    print("RD cache error:", e)

# Check Academy logs or students
try:
    with open(r"c:\Users\DELL\Desktop\Dash_InfectoCast\academy_logs_cache.json", 'r', encoding='utf-8') as f:
        acad_logs = json.load(f)
    print(f"Academy logs count: {len(acad_logs)}")
    
    # Find recent academy logs
    acad_sorted = sorted(acad_logs, key=lambda x: str(x.get('Data log') or ''), reverse=True)
    print("Recent 10 Academy logs:")
    for al in acad_sorted[:10]:
        print("  Academy Log:", al.get('Data log'), "|", al.get('Nome aluno'), "|", al.get('Ação / Local'), "|", al.get('Curso'))
except Exception as e:
    print("Academy logs error:", e)
