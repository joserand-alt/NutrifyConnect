import os

dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"

# 1. Fix vindi_service.py imports
v_path = os.path.join(dash_dir, "vindi_service.py")
with open(v_path, "r", encoding="utf-8") as f:
    v_code = f.read()

v_code = "from datetime import datetime, date, timedelta\nimport calendar\n" + v_code
with open(v_path, "w", encoding="utf-8") as f:
    f.write(v_code)
print("vindi_service.py import fixed!")

# 2. Fix asaas_service.py imports
a_path = os.path.join(dash_dir, "asaas_service.py")
with open(a_path, "r", encoding="utf-8") as f:
    a_code = f.read()

if "from datetime import datetime, date, timedelta" not in a_code:
    a_code = "from datetime import datetime, date, timedelta\nimport calendar\n" + a_code
with open(a_path, "w", encoding="utf-8") as f:
    f.write(a_code)
print("asaas_service.py import fixed!")
