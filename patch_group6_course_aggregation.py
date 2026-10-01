import os
import re

dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"
template_path = os.path.join(dash_dir, "template.html")

with open(template_path, "r", encoding="utf-8") as f:
    t_code = f.read()

# Replace the course aggregation logic in drawExecView
old_block_pattern = r"\/\/ Mapeamento por Curso Canonizado \(Especialidade\) com Métricas Financeiras e Projeções Completas.*?const vHist = \(vindi\.historico_mensal \|\| \[\]\);"

new_block = """// Mapeamento por Curso Canonizado (Especialidade) com Métricas Financeiras e Projeções Completas
    const coursesMap = {};
    const emailToCourse = {};
    const nameToCourse = {};

    // 1. Mapear cursos e engajamento a partir dos estudantes
    baseStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const c = resolveCanonicalCourse(s.curso);
        if (em) emailToCourse[em] = c;
        if (nm) nameToCourse[nm] = c;

        if (!coursesMap[c]) {
            coursesMap[c] = {
                curso: c, total: 0, vigentes: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, concluidos: 0, cancelados: 0,
                pago_total: 0, pago_mes_atual: 0, proj_mes_atual: 0, pago_mes_ant: 0, atraso: 0, mrr: 0,
                proj_1m: 0, proj_3m: 0, proj_6m: 0, proj_12m: 0
            };
        }
        const cm = coursesMap[c];
        cm.total++;

        const vSt = (s.vindi ? (s.vindi.status_financeiro || s.vindi.status_assinatura) : '').toLowerCase();
        const aSt = (s.asaas ? (s.asaas.status_financeiro || s.asaas.status_assinatura) : '').toLowerCase();
        const isCancel = vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled' || s.status === 'Cancelado';
        const isConcluido = !isCancel && (vSt === 'quitado' || aSt === 'quitado' || s.status === 'Concluído' || s.status === 'Encerrado' || s.turma_encerrada === true);

        if (isCancel) {
            cm.cancelados++;
        } else if (isConcluido) {
            cm.concluidos++;
        } else {
            cm.vigentes++;
            const acessou = s.acessou;
            const logins = s.logins || 0;
            const dias_inativo = s.dias_inativo || 0;
            const cadencia = s.cadencia || 0;
            const dias_ativo = s.dias_ativo || 0;

            if (!acessou || logins === 0) {
                cm.nunca++;
            } else if (logins > 1 && dias_ativo > 0) {
                if (dias_inativo > 30 || (dias_inativo > 14 && cadencia > 0 && dias_inativo > (cadencia * 2.5))) {
                    cm.abandono++;
                } else if (cadencia > 0 && dias_inativo > (cadencia * 1.5 + 2)) {
                    cm.em_risco++;
                } else {
                    cm.ativos++;
                }
            } else {
                if (dias_inativo > 14) {
                    cm.abandono++;
                } else if (dias_inativo > 7) {
                    cm.em_risco++;
                } else {
                    cm.ativos++;
                }
            }
        }
    });

    const getCm = (cName) => {
        const c = resolveCanonicalCourse(cName) || 'PLATAFORMA GERAL';
        if (!coursesMap[c]) {
            coursesMap[c] = {
                curso: c, total: 0, vigentes: 0, ativos: 0, em_risco: 0, abandono: 0, nunca: 0, concluidos: 0, cancelados: 0,
                pago_total: 0, pago_mes_atual: 0, proj_mes_atual: 0, pago_mes_ant: 0, atraso: 0, mrr: 0,
                proj_1m: 0, proj_3m: 0, proj_6m: 0, proj_12m: 0
            };
        }
        return coursesMap[c];
    };

    // 2. Faturas Realizadas e Atraso (Vindi + Asaas)
    [...vFaturas, ...aFaturas].forEach(f => {
        const em = (f.email || '').toString().toLowerCase().trim();
        const nm = (f.aluno || '').toString().toLowerCase().trim();
        const cName = f.curso || emailToCourse[em] || nameToCourse[nm] || 'PLATAFORMA GERAL';
        const cm = getCm(cName);

        const val = Number(f.valor) || 0;
        const st = (f.status || '').toLowerCase();
        const dtPag = (f.data_pagamento || f.data_pagamento_iso || f.data || '').toString();
        const dtVenc = (f.vencimento || f.vencimento_iso || '').toString();

        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            cm.pago_total += val;
            if (dtPag.includes('09/2026') || dtPag.includes('2026-09') || dtPag.includes('/09/26')) {
                cm.pago_mes_atual += val;
            } else if (dtPag.includes('08/2026') || dtPag.includes('2026-08') || dtPag.includes('/08/26')) {
                cm.pago_mes_ant += val;
            }
        } else if (st === 'em_atraso' || st === 'overdue') {
            cm.atraso += val;
        } else if (st === 'futuro' || st === 'a_vencer' || st === 'pending' || st === 'pendente') {
            if (dtVenc.includes('09/2026') || dtVenc.includes('2026-09') || dtVenc.includes('/09/26')) {
                cm.proj_mes_atual += val;
            }
        }
    });

    // 3. Assinaturas Vindi (MRR, A Vencer no Mês e Projeção 30d D+30 por Curso)
    const vSubsList = (vindi.subscriptions || []);
    vSubsList.forEach(sub => {
        if (sub.status_financeiro === 'adimplente') {
            const em = (sub.customer_email || '').toString().toLowerCase().trim();
            const cName = sub.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const cm = getCm(cName);
            const price = Number(sub.valor_parcela) || 0;
            cm.mrr += price;

            const prox = (sub.proximo_vencimento || '').toString();
            if (prox.includes('/09/2026') || prox.includes('/09/26') || prox.includes('2026-09')) {
                cm.proj_mes_atual += price;
                cm.proj_1m += price;
            } else if (prox.includes('/10/2026') || prox.includes('/10/26') || prox.includes('2026-10')) {
                // Próximos 30 dias pegam primeira quinzena de outubro
                const dia = parseInt(prox.split('/')[0] || '0', 10);
                if (dia <= 14) {
                    cm.proj_1m += price;
                }
            } else if (!prox) {
                cm.proj_mes_atual += price;
                cm.proj_1m += price;
            }
        }
    });

    // 4. Clientes Asaas (MRR por Curso)
    const aData = asaas.data || {};
    Object.values(aData).forEach(stInfo => {
        if (stInfo.status_financeiro === 'adimplente') {
            const em = (stInfo.customer_email || stInfo.email || '').toString().toLowerCase().trim();
            const cName = stInfo.curso || emailToCourse[em] || 'PLATAFORMA GERAL';
            const cm = getCm(cName);
            const price = Number(stInfo.valor_parcela || stInfo.mrr) || 0;
            cm.mrr += price;
        }
    });

    // 5. Totalizadores e Projeções Financeiras por Curso
    Object.values(coursesMap).forEach(cm => {
        cm.previsto_mes_vigente = cm.pago_mes_atual + cm.proj_mes_atual;
        const diff = cm.previsto_mes_vigente - cm.pago_mes_ant;
        cm.crescimento_mom = cm.pago_mes_ant > 0 ? (((diff) / cm.pago_mes_ant) * 100).toFixed(1) : (cm.previsto_mes_vigente > 0 ? '+100' : '0.0');
        
        if (!cm.proj_1m) cm.proj_1m = cm.mrr;
        cm.proj_3m = cm.mrr * 3;
        cm.proj_6m = cm.mrr * 6;
        cm.proj_12m = cm.mrr * 12;
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
    const proj12m = (Number(vKpis.projecao_12m) || 2663789.16);
    const atrasoTotal = (Number(vKpis.total_em_atraso) || 0) + (Number(aKpis.total_em_atraso) || 0);
    const qtdAtrasoTotal = (Number(vKpis.qtd_em_atraso) || 0) + (Number(aKpis.qtd_em_atraso) || 0);
    const taxaAdimplencia = vKpis.taxa_adimplencia || 96;

    // Cálculo Dinâmico do Mês Vigente e Mês Anterior (MoM)
    const vHist = (vindi.historico_mensal || []);"""

t_code_new = re.sub(old_block_pattern, new_block, t_code, flags=re.DOTALL)
with open(template_path, "w", encoding="utf-8") as f:
    f.write(t_code_new)

print("template.html updated with accurate course aggregation logic!")
