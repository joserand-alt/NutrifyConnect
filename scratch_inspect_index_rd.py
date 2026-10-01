with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx_students = text.find('"students":')
print('students found at:', idx_students)

# Let's inspect the first student with rd_funnel
idx_rd = text.find('"rd_funnel":', idx_students)
print('rd_funnel found at:', idx_rd)
print(text[idx_rd:idx_rd+500])
