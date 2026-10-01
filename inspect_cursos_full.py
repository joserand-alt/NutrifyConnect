import pandas as pd

excel_path = r'C:\Users\DELL\Desktop\Acompanhamento de acessos\BD\CURSOS.xlsx'
df_cursos = pd.read_excel(excel_path, sheet_name=0)
print("=== SHEET: CURSOS ===")
print(df_cursos.to_string())

df_mods = pd.read_excel(excel_path, sheet_name=1)
print("\n=== SHEET: MÓDULOS ===")
print(df_mods[['CURSO', 'ID MÓDULO', 'Nome']].to_string())
