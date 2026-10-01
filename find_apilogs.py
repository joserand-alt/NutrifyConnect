import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all occurrences of apilogs or API_LOGS
for m in re.finditer(r'apilogs|API_LOGS|consultApiLogs|setApiPreset|renderApiLogsTable|exportApiLogsToCSV', text, re.IGNORECASE):
    idx = m.start()
    print(f"Match '{m.group(0)}' at {idx}: {repr(text[max(0, idx-40):min(len(text), idx+100)])}")
