import pandas as pd

log_path = r'C:\Users\DELL\Desktop\Acompanhamento de acessos\BD\Log de uso.xlsx'
df = pd.read_excel(log_path)
print("Log columns:", df.columns.tolist())
print("\nUnique 'Ação / Local':")
print(df['Ação / Local'].value_counts())

# Check where 1014 or 1020 appear
for val in ['1014', 1014, 1014.0, '1020', 1020, 1020.0]:
    sub = df[(df['ID Item'] == val) | (df['Desc. Item'] == val)]
    if not sub.empty:
        print(f"\nFound {len(sub)} rows for {val}:")
        print(sub[['Ação / Local', 'ID Item', 'Desc. Item', 'Modulo', 'Curso', 'Nome aluno']].head(5))
