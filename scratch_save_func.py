with open(r'C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('function computeUnifiedFinancialDataset')
idx2 = text.find('return { courses: coursesMap, global: globalObj };', idx1)
end_idx = text.find('}', idx2) + 1

func_code = text[idx1:end_idx]

with open('scratch_current_func.js', 'w', encoding='utf-8') as f_out:
    f_out.write(func_code)

print("Saved current function, length:", len(func_code))
