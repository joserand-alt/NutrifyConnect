import cativa_api
import json

data = cativa_api.fetch_all_cativa_data(force_refresh=True)
students = data.get('students', [])
print(f"Total students fetched from Cativa API: {len(students)}")
for s in students:
    em = s.get('email')
    nm = s.get('fullName')
    courses = s.get('courses', [])
    for c in courses:
        enr = c.get('enrollmentDate')
        if any(x in str(enr) for x in ['2026-09-20', '2026-09-21', '2026-09-22', '2026-09-23', '2026-09-24']):
            print(f" -> RECENT: {nm} ({em}) | Course: {c.get('courseName')} | Enrolled: {enr}")
