import re

template_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Tabs
tabs = re.findall(r'<div[^>]*id=["\'](tab-[^"\']+)["\']', text)
print('Tabs found:', tabs)

# Select dropdowns
selects = re.findall(r'<select[^>]*id=["\']([^"\']+)["\']', text)
print('Select IDs found:', selects)

# Tab buttons / navigation
nav_btns = re.findall(r'<button[^>]*data-tab=["\']([^"\']+)["\']', text)
print('Nav buttons data-tab:', nav_btns)

# Render functions
renders = re.findall(r'function\s+(render[a-zA-Z0-9_]*)', text)
print('Render functions:', sorted(set(renders)))
