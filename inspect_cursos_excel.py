import pandas as pd

df = pd.read_excel(r'C:\Users\DELL\Desktop\Acompanhamento de acessos\BD\Log de uso.xlsx')
acao_col = df.columns[3]
id_col = df.columns[4]
desc_col = df.columns[5]

pg = df[df[acao_col].str.contains('PG INSCRI', na=False)]
print("Unique ID Item in PG INSCRIÇÃO TURMA:")
print(pg[id_col].value_counts())
print("\nUnique Desc. Item in PG INSCRIÇÃO TURMA:")
print(pg[desc_col].value_counts())

print("\n--- CURSOS.xlsx ---")
excel_path = r'C:\Users\DELL\Desktop\Acompanhamento de acessos\BD\CURSOS.xlsx'
xl = pd.ExcelFile(excel_path)
print("Sheet names in CURSOS.xlsx:", xl.sheet_names)
for sheet in xl.sheet_names:
    dfs = pd.read_excel(excel_path, sheet_name=sheet)
    print(f"\nSheet: {sheet} (shape {dfs.shape})")
    print(dfs.head(10))
