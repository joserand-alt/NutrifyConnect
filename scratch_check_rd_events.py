import sys, os, json

for fname in [r"c:\Users\DELL\Desktop\Dash_InfectoCast\rd_conversas_cache.json", r"c:\Users\DELL\Desktop\Dash_InfectoCast\rd_students_cache.json"]:
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as f:
            d = json.load(f)
        print(f"File {os.path.basename(fname)}: {len(d)} records")
        # Check recent dates
        recent_events = []
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, dict):
                    events = v.get('events', [])
                    for ev in events:
                        recent_events.append((ev.get('created_at') or ev.get('timestamp') or '', k, ev.get('event_name') or ev.get('event_type') or ''))
        recent_events.sort(key=lambda x: str(x[0]), reverse=True)
        print("Recent 10 events:")
        for re in recent_events[:10]:
            print("  ", re)
