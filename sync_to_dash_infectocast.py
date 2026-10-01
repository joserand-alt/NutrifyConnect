import os
import shutil

src_dir = r"C:\Users\DELL\Desktop\Acompanhamento de acessos"
dst_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"

files_to_copy = [
    "index.html",
    "dashboard_gerado.html",
    "template.html",
    "gerador.py",
    "vindi_service.py",
    "asaas_service.py",
    "cativa_api.py",
    "rd_service.py",
    "sync_matriculas_rd.py",
    "vindi_cache.json",
    "asaas_cache.json",
    "rd_tagged_matriculas.json",
    "rd_tagged_pendentes.json",
    "rd_students_cache.json",
    "academy_logs_cache.json"
]

print("Copiando arquivos atualizados para Dash_InfectoCast...")
for f in files_to_copy:
    src_path = os.path.join(src_dir, f)
    dst_path = os.path.join(dst_dir, f)
    if os.path.exists(src_path):
        shutil.copyfile(src_path, dst_path)
        sz = os.path.getsize(dst_path) / (1024*1024)
        print(f" -> {f} ({sz:.2f} MB) copiado com sucesso.")
    else:
        print(f" [!] Aviso: {f} nao encontrado em {src_dir}")

print("\nConcluído com sucesso!")
