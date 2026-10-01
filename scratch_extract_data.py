with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx_start = text.find('const DATA = {')
if idx_start == -1:
    idx_start = text.find('var DATA = {')

# Find the matching closing of DATA = { ... };
# DATA ends right before functions start or next const
idx_next = text.find('const $ =', idx_start)
if idx_next == -1:
    idx_next = text.find('function', idx_start)

data_js = text[idx_start:idx_next].strip()
if data_js.endswith(';'):
    data_js = data_js[:-1]

with open('extracted_data.js', 'w', encoding='utf-8') as f_out:
    f_out.write(data_js + ';\nmodule.exports = DATA;\n')
print("Clean extracted_data.js written, size:", len(data_js))
