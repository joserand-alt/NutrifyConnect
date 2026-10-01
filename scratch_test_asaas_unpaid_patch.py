import sys
sys.path.insert(0, r"c:\Users\DELL\Desktop\Dash_InfectoCast")
import asaas_service, json

students_asaas, financeiro_global = asaas_service._process(
    asaas_service.fetch_all_customers(),
    asaas_service.fetch_all_payments()
)

print(f"Total entries in students_asaas: {len(students_asaas)}")
clareana = students_asaas.get('draclareana.geraldes@gmail.com') or students_asaas.get('100261')
print("Clareana in students_asaas:", clareana)
