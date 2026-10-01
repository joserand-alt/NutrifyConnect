import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\original_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_logs = text.find('let API_LOGS_DATA')
pos_end_logs = text.find('function openAllocModal')
print(f"API logs code span: {pos_logs} to {pos_end_logs}")

print("--- Before API_LOGS_DATA ---")
print(text[pos_logs-300:pos_logs])

print("--- After API_LOGS_DATA ---")
print(text[pos_end_logs:pos_end_logs+400])
