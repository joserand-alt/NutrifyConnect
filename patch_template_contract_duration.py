import os
import re

dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"
template_path = os.path.join(dash_dir, "template.html")

with open(template_path, "r", encoding="utf-8") as f:
    t_code = f.read()

# Replace the course projection calculation to model contract duration/runoff
old_calc_pattern = r"\/\/ 5\. Totalizadores e Projeções Financeiras por Curso.*?const proj12m = \(Number\(vKpis\.projecao_12m\) \|\| 2663789\.16\);"

new_calc = """// 5. Totalizadores e Projeções Financeiras por Curso com Modelo de Duração de Contrato (Runoff / Encerramentos Reais)
    // Para cada curso, simulamos o fluxo mês a mês (1 a 12) baseado nas parcelas restantes de cada contrato ativo
    const courseMonthlyProjection = {};

    vSubsList.forEach(sub => {
        if (sub.status_financeiro === 'adimplente') {
            const em = (sub.customer_email || '').toString().toLowerCase().trim();
            const cName = sub.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
            const price = Number(sub.valor_parcela) || 0;
            
            // Duração do plano e parcelas pagas
            const planoStr = (sub.plano || '').toString().toUpperCase();
            let totalCycles = 18; // Padrão de Pós-Graduação (18 meses)
            if (planoStr.includes('24')) totalCycles = 24;
            else if (planoStr.includes('12') || planoStr.includes('ANUAL')) totalCycles = 12;
            else if (planoStr.includes('6') || planoStr.includes('SEMESTRAL')) totalCycles = 6;
            
            const faturasArr = sub.faturas || [];
            const paidCount = faturasArr.filter(f => (f.status === 'paid' || f.status === 'pago')).length;
            const remainingCycles = Math.max(0, totalCycles - paidCount);

            if (!courseMonthlyProjection[c]) {
                courseMonthlyProjection[c] = Array(12).fill(0);
            }
            // Adiciona a parcela nos meses em que o contrato ainda está vigente
            for (let m = 0; m < 12; m++) {
                if (m < remainingCycles) {
                    courseMonthlyProjection[c][m] += price;
                }
            }
        }
    });

    // Mapear faturas pendentes do Asaas nos meses futuros
    [...aFaturas].forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pendente' || st === 'pending' || st === 'a_vencer') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const cName = f.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
            const val = Number(f.valor) || 0;
            const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();
            
            if (dtVenc) {
                // Estimar mês relativo (0 = mês 1, 1 = mês 2, ..., 11 = mês 12)
                const dObj = new Date(dtVenc.slice(0, 10));
                const hoje = new Date();
                const diffMeses = (dObj.getFullYear() - hoje.getFullYear()) * 12 + (dObj.getMonth() - hoje.getMonth());
                if (diffMeses >= 0 && diffMeses < 12) {
                    if (!courseMonthlyProjection[c]) courseMonthlyProjection[c] = Array(12).fill(0);
                    courseMonthlyProjection[c][diffMeses] += val;
                }
            }
        }
    });

    // Consolidar Projeções Contratuais Reais por Curso
    Object.values(coursesMap).forEach(cm => {
        cm.previsto_mes_vigente = cm.pago_mes_atual + cm.proj_mes_atual;
        const diff = cm.previsto_mes_vigente - cm.pago_mes_ant;
        cm.crescimento_mom = cm.pago_mes_ant > 0 ? (((diff) / cm.pago_mes_ant) * 100).toFixed(1) : (cm.previsto_mes_vigente > 0 ? '+100' : '0.0');
        
        const mArr = courseMonthlyProjection[cm.curso] || Array(12).fill(0);
        const p1mContratual = mArr[0] > 0 ? mArr[0] : (cm.proj_1m || cm.mrr);
        const p3mContratual = mArr.slice(0, 3).reduce((a, b) => a + b, 0);
        const p6mContratual = mArr.slice(0, 6).reduce((a, b) => a + b, 0);
        const p12mContratual = mArr.slice(0, 12).reduce((a, b) => a + b, 0);

        cm.proj_1m = p1mContratual;
        cm.proj_3m = p3mContratual > 0 ? p3mContratual : cm.mrr * 3;
        cm.proj_6m = p6mContratual > 0 ? p6mContratual : cm.mrr * 6;
        cm.proj_12m = p12mContratual > 0 ? p12mContratual : cm.mrr * 12;
    });

    // Projeções Globais Consolidadas da Carteira (Soma dos fluxos de contrato de todos os cursos)
    let globalProj3m = 0, globalProj6m = 0, globalProj12m = 0;
    Object.values(coursesMap).forEach(cm => {
        globalProj3m += cm.proj_3m;
        globalProj6m += cm.proj_6m;
        globalProj12m += cm.proj_12m;
    });

    // Totalizadores Consolidados Financeiros
    const vKpis = vindi.kpis || {};
    const aKpis = asaas.kpis || {};

    const recRealizadaTotal = (Number(vKpis.total_recebido) || 0) + (Number(aKpis.total_recebido) || 0);
    const recMesAtual = (Number(vKpis.recebido_mes_atual) || 0) + (Number(aKpis.recebido_mes_atual) || Number(aKpis.recebido_mes) || 0);
    const aVencerMesVigente = (Number(vKpis.a_vencer_mes_atual) || Number(vKpis.projecao_mensal?.[0]?.previsto) || 0) + (Number(aKpis.a_vencer_mes_atual) || Number(aKpis.projecao_mensal?.[0]?.previsto) || 0);
    const totalPrevistoMesVigente = recMesAtual + aVencerMesVigente;
    const mrrConsolidado = (Number(vKpis.mrr_ativo) || 0) + (Number(aKpis.mrr_ativo) || 0);
    const proj30d = (Number(vKpis.projecao_30d) || 0) + (Number(aKpis.projecao_30d) || 0);
    const proj3mConsolidada = globalProj3m > 0 ? globalProj3m : mrrConsolidado * 3;
    const proj6mConsolidada = globalProj6m > 0 ? globalProj6m : mrrConsolidado * 6;
    const proj12m = globalProj12m > 0 ? globalProj12m : mrrConsolidado * 12;"""

t_code_new = re.sub(old_calc_pattern, new_calc, t_code, flags=re.DOTALL)

# Update descriptions on Cards 6, 7, 8 to reflect contract terms
t_code_new = t_code_new.replace(
    '<div class="exec-card-sub">Previsão contratual da carteira para os próximos 3 meses</div>',
    '<div class="exec-card-sub">Receita contratada real (considerando encerramentos e parcelas restantes)</div>'
)
t_code_new = t_code_new.replace(
    '<div class="exec-card-sub">Previsão contratual da carteira para os próximos 6 meses</div>',
    '<div class="exec-card-sub">Receita contratada real (considerando encerramentos e parcelas restantes)</div>'
)
t_code_new = t_code_new.replace(
    '<div class="exec-card-sub">Previsão contratual de faturamento anual da carteira</div>',
    '<div class="exec-card-sub">Receita contratada restante até o fim dos contratos ativos da carteira</div>'
)

with open(template_path, "w", encoding="utf-8") as f:
    f.write(t_code_new)

print("template.html updated with contract expiration model!")
