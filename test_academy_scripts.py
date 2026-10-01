import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://academy.infectocast.com.br', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

scripts = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
print(f"Scripts encontrados ({len(scripts)}):")
for s in scripts:
    print(" ", s)
