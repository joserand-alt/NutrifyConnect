import sys
import os
import re
from datetime import datetime

# Test the exact modification on asaas_service.py logic
with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\asaas_service.py', 'r', encoding='utf-8') as f:
    code = f.read()

print("asaas_service.py read successfully. Length:", len(code))
assert 'def _process(customers, payments):' in code
print("Target function located!")
