import json

with open('vindi_cache.json', 'r', encoding='utf-8') as f:
    vindi = json.load(f)

print("Vindi cache top keys:", list(vindi.keys()))
for k in vindi.keys():
    v = vindi[k]
    if isinstance(v, dict):
        print(f"Key {k} dict len: {len(v)}")
        # Check if gislayne is in keys
        matches = [x for x in v.keys() if 'gislayne' in str(x).lower()]
        if matches:
            print(f"Found in {k}:", matches)
            print("Value:", v[matches[0]])
    elif isinstance(v, list):
        print(f"Key {k} list len: {len(v)}")
        matches = [x for x in v if 'gislayne' in str(x).lower()]
        if matches:
            print(f"Found in {k}:", len(matches))
            print("First match:", matches[0])
