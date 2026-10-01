with open('C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove nav tab button
nav_btn = '<button class="tab" data-p="apilogs"><span class="num">7</span>Logs de Alunos (API)</button>'
if nav_btn in text:
    text = text.replace(nav_btn, '')
    print('Nav button removed!')
else:
    # Try fuzzy replace
    import re
    text = re.sub(r'<button class="tab" data-p="apilogs">.*?</button>', '', text)
    print('Nav button removed via regex!')

# 2. Remove panel section
idx_start = text.find('id="p-apilogs"')
if idx_start != -1:
    # Find preceding section start
    sec_start = text.rfind('<section', 0, idx_start)
    sec_end = text.find('</section>', idx_start) + len('</section>')
    # Also find any preceding comment like <!-- PANEL 7: API LOGS -->
    comment_start = text.rfind('<!--', 0, sec_start)
    if comment_start != -1 and 'API LOGS' in text[comment_start:sec_start]:
        sec_start = comment_start
    text = text[:sec_start] + text[sec_end:]
    print('Panel section removed!')

# 3. Remove JS functions related to API Logs
idx_js = text.find('let API_LOGS_DATA = [];')
if idx_js != -1:
    idx_js_end = text.find('function _resolveFinCourse', idx_js)
    if idx_js_end != -1:
        text = text[:idx_js] + text[idx_js_end:]
        print('JS functions removed!')

with open('C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('template.html cleaned up successfully!')
