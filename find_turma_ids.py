import os
import pandas as pd

dirs = [r'C:\Users\DELL\Desktop\Acompanhamento de acessos', r'C:\Users\DELL\Desktop\Acompanhamento de acessos\BD']
ids_to_find = [1002, 1004, 1005, 1006, 1008, 1013, 1014, 1015, 1016, 1017, 1019, 1020, 1021]

for d in dirs:
    for f in os.listdir(d):
        if f.endswith('.xlsx') or f.endswith('.xls') or f.endswith('.csv'):
            fpath = os.path.join(d, f)
            try:
                if f.endswith('.csv'):
                    df = pd.read_csv(fpath, low_memory=False, nrows=5000)
                    for col in df.columns:
                        for target in ids_to_find:
                            cnt = (df[col].astype(str).str.contains(f'^{target}(\\.0)?$', regex=True, na=False)).sum()
                            if cnt > 0:
                                print(f"File {f} | Col '{col}' has {cnt} rows matching ID {target}")
                else:
                    xl = pd.ExcelFile(fpath)
                    for s in xl.sheet_names:
                        df = pd.read_excel(fpath, sheet_name=s)
                        for col in df.columns:
                            for target in ids_to_find:
                                cnt = (df[col].astype(str).str.contains(f'^{target}(\\.0)?$', regex=True, na=False)).sum()
                                if cnt > 0:
                                    print(f"File {f} | Sheet '{s}' | Col '{col}' has {cnt} rows matching ID {target}")
            except Exception as e:
                pass
