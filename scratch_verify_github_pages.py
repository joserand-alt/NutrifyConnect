import urllib.request
import time
import json

url = f'https://joserand-alt.github.io/Dash_InfectoCast/?_nocache={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, timeout=15) as response:
        html = response.read().decode('utf-8')
        print(f"Fetched HTML size: {len(html)} bytes")
        
        pos = html.find('const DATA = {')
        if pos != -1:
            end_pos = html.find('let CURRENT_DATA', pos)
            semicolon_pos = html.rfind(';', pos, end_pos + 10)
            data_str = html[pos + len('const DATA = '):semicolon_pos]
            data = json.loads(data_str)
            meta = data.get('meta', {})
            print(f"Generated: {meta.get('generated')}")
            print(f"Updated At: {meta.get('updated_at')}")
            
            fats_asaas = (data.get('financeiro_asaas') or {}).get('faturas_tabela', [])
            print(f"Asaas Faturas Count: {len(fats_asaas)}")
            
            students = data.get('students', [])
            print(f"Students Count: {len(students)}")
            
        print("Sound button present:", 'id="hud-sound-btn"' in html)
        print("Web Audio present:", 'window.playVictorySound' in html)
except Exception as e:
    print("Fetch error:", e)
