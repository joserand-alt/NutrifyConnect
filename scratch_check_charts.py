import re

with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# check chart libraries
libs = []
if 'Chart(' in text or 'chart.js' in text.lower():
    libs.append('Chart.js')
if 'ApexCharts' in text:
    libs.append('ApexCharts')
if 'echarts' in text:
    libs.append('ECharts')
if '<canvas' in text:
    libs.append('HTML5 Canvas')
if '<svg' in text:
    libs.append('Inline SVG')

print("Chart technologies detected:", libs)

# Let's inspect how _drawFinChart or drawTimeline renders
m_draw = re.search(r'function\s+_drawFinChart\s*\([^)]*\)\s*\{', text)
if m_draw:
    pos = m_draw.start()
    print("Found _drawFinChart snippet:\n", text[pos:pos+1500])
else:
    m_tl = re.search(r'function\s+drawTimeline\s*\([^)]*\)\s*\{', text)
    if m_tl:
        pos = m_tl.start()
        print("Found drawTimeline snippet:\n", text[pos:pos+1500])
