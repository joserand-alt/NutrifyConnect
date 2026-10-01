import os
import re

dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"
template_path = os.path.join(dash_dir, "template.html")

with open(template_path, "r", encoding="utf-8") as f:
    t_code = f.read()

# Refine buildCourseSpecificFin in template.html
old_fin_pattern = r"const proj30 = projecao_mensal\.length > 0 \? projecao_mensal\[0\]\.previsto : 0;\s*const mrr = projecao_mensal\.slice\(0, 2\)\.reduce\(\(acc, p\) => acc \+ p\.previsto, 0\) \/ Math\.max\(1, Math\.min\(2, projecao_mensal\.length\)\);"

new_fin_block = """// Mapear faturas e assinaturas ativas do curso específico
            const vSubsList = (vindi.subscriptions || (DATA && DATA.financeiro && DATA.financeiro.subscriptions) || []);
            const courseSubs = vSubsList.filter(sub => {
                const c = resolveCanonicalCourse(sub.curso || (DATA && DATA.students && DATA.students.find(s=>s.email===sub.customer_email)?.curso) || '');
                return c === activeCurso && sub.status_financeiro === 'adimplente';
            });
            const courseMrrVindi = courseSubs.reduce((acc, sub) => acc + (Number(sub.valor_parcela) || 0), 0);

            let courseMrrAsaas = 0;
            Object.values(asaas.data || {}).forEach(stInfo => {
                const c = resolveCanonicalCourse(stInfo.curso || '');
                if (c === activeCurso && stInfo.status_financeiro === 'adimplente') {
                    courseMrrAsaas += (Number(stInfo.valor_parcela || stInfo.mrr) || 0);
                }
            });
            const mrr = (courseMrrVindi + courseMrrAsaas) > 0 ? (courseMrrVindi + courseMrrAsaas) : (projecao_mensal.length > 0 ? projecao_mensal[0].previsto : 0);
            const proj30 = mrr;"""

t_code_new = re.sub(old_fin_pattern, new_fin_block, t_code, flags=re.DOTALL)

with open(template_path, "w", encoding="utf-8") as f:
    f.write(t_code_new)

print("template.html refined for Finance tab consistency!")
