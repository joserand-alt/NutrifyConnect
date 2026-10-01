"""
Check Cativa cache for PG students - they should have course data from lessons-watched-report
"""
import json, os

CACHE_FILE = r"C:\Users\DELL\Desktop\Dash_InfectoCast\cativa_cache.json"
if not os.path.exists(CACHE_FILE):
    CACHE_FILE = r"C:\Users\DELL\Desktop\Acompanhamento de acessos\cativa_cache.json"

pg_emails = [
    'danielesarto@yahoo.com.br', 'beatriz.grinsztejn@gmail.com',
    'vivianvidal01@gmail.com', 'jucazita@yahoo.com.br',
    'limafilipe13@hotmail.com', 'souzaxp4i@gmail.com',
    'adrianammas@gmail.com', 'welisoncatarino13@hotmail.com',
    'secco.mayara@gmail.com', 'm.mlbmsantos@gmail.com',
    'marcosdavi2006@yahoo.com.br', 'raolisw@gmail.com',
    'costalg1@gmail.com', 'laura_orlandi@hotmail.com',
    'mclaramdp@gmail.com', 'markus_braga@hotmail.com',
    'daniela.torchi@gmail.com'
]

print(f"Loading Cativa cache from: {CACHE_FILE}")
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        cativa = json.load(f)
    
    students = cativa.get('students', [])
    users_meta = cativa.get('users_metadata', {})
    print(f"Total students in Cativa: {len(students)}")
    
    # Build email index
    cativa_by_email = {}
    for s in students:
        em = str(s.get('email', '')).lower().strip()
        if em:
            cativa_by_email[em] = s
    
    print(f"\n=== PG Students in Cativa ===\n")
    for email in pg_emails:
        s = cativa_by_email.get(email)
        if s:
            courses = s.get('courses', [])
            course_names = [c.get('courseName', '') for c in courses]
            n_lessons = sum(len(c.get('lessons', [])) for c in courses)
            print(f"  [{email}]")
            print(f"    nome: {s.get('fullName')}")
            print(f"    courses ({len(courses)}): {course_names}")
            print(f"    total lessons watched: {n_lessons}")
            
            # Show first course details
            for c in courses[:3]:
                cname = c.get('courseName', '')
                lessons = c.get('lessons', [])
                print(f"      -> {cname}: {len(lessons)} aulas")
            print()
        else:
            meta = users_meta.get(email, {})
            if meta:
                print(f"  [{email}] NO course data, but has user metadata: {meta.get('first_name')} {meta.get('last_name')}")
            else:
                print(f"  [{email}] NOT found in Cativa at all")
else:
    print("Cativa cache NOT found")
    
    # Try to find any cativa cache
    for root, dirs, files in os.walk(r"C:\Users\DELL\Desktop"):
        for f in files:
            if 'cativa' in f.lower() and f.endswith('.json'):
                print(f"  Found: {os.path.join(root, f)}")
