import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://academy.infectocast.com.br/app_assets/js/setup.js', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
    code = resp.read().decode('utf-8', errors='ignore')

matches = re.findall(r'(/api/[^\s"\'\)\;]+)', code)
print('Endpoints in setup.js:', set(matches))

aspx_files = re.findall(r'([a-zA-Z0-9_\-]+\.aspx)', code)
print('ASPX files in setup.js:', set(aspx_files))

ajax_calls = re.findall(r'url:\s*["\']([^"\']+)["\']', code)
print('Ajax URLs in setup.js:', set(ajax_calls))
