"""
Patch: Regra Inteligente de Status Financeiro
=============================================
Corrige o problema onde um aluno com assinatura CANCELADA em um gateway
(ex: Vindi/Cativa) mas ATIVA em outro (ex: Asaas/Academy) era incorretamente
marcado como 'Cancelado'.

Nova regra: Só marca como 'Cancelado' se NÃO existir nenhuma assinatura ativa
em qualquer gateway. A assinatura ativa sempre prevalece.
"""

template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================================
# PATCH 1: Lógica principal de status (linhas ~1544-1555)
# ============================================================================
old_block_1 = """        // REGRA DE STATUS FINANCEIRO:
        // Se o aluno tem assinatura CANCELADA na Vindi, o status dele eh sempre 'Cancelado',
        // independente do status calculado pela plataforma (Abandonou, Nunca acessou, etc.)
        const vindiStatus = scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : null;
        const asaasStatus = scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : null;
        if (vindiStatus === 'cancelado' || vindiStatus === 'canceled') {
            scopy.status = 'Cancelado';
            scopy.status_motivo = 'Assinatura cancelada no sistema financeiro (Vindi).';
        } else if (asaasStatus === 'cancelado' || asaasStatus === 'canceled') {
            scopy.status = 'Cancelado';
            scopy.status_motivo = 'Cobran\u00e7a cancelada no sistema financeiro (Asaas).';
        }"""

new_block_1 = """        // REGRA INTELIGENTE DE STATUS FINANCEIRO:
        // Só marca como 'Cancelado' se NÃO existir assinatura ATIVA em nenhum gateway.
        // Se o aluno tem Vindi cancelada mas Asaas ativa (ou vice-versa), a ativa prevalece.
        const vindiStatus = scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : null;
        const asaasStatus = scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : null;
        const vindiCanceled = vindiStatus === 'cancelado' || vindiStatus === 'canceled';
        const asaasCanceled = asaasStatus === 'cancelado' || asaasStatus === 'canceled';
        const vindiActive = vindiStatus && !vindiCanceled;
        const asaasActive = asaasStatus && !asaasCanceled;
        // Só cancela se existe pelo menos um cancelamento E nenhum gateway ativo
        if ((vindiCanceled || asaasCanceled) && !vindiActive && !asaasActive) {
            if (vindiCanceled) {
                scopy.status = 'Cancelado';
                scopy.status_motivo = 'Assinatura cancelada no sistema financeiro (Vindi).';
            } else {
                scopy.status = 'Cancelado';
                scopy.status_motivo = 'Cobrança cancelada no sistema financeiro (Asaas).';
            }
        }"""

if old_block_1 in content:
    content = content.replace(old_block_1, new_block_1)
    print("PATCH 1 (status principal): OK")
else:
    print("PATCH 1: BLOCO NÃO ENCONTRADO - verificando variação...")
    # Tenta encontrar padrão sem acentuação
    import re
    # Pattern alternativo
    alt_pattern = "// REGRA DE STATUS FINANCEIRO:"
    if alt_pattern in content:
        # Find the start index
        idx = content.index(alt_pattern)
        # Find the closing of this block (next 'return scopy;')
        end_marker = "return scopy;"
        end_idx = content.index(end_marker, idx)
        old_section = content[idx:end_idx]
        print(f"  Found block of length {len(old_section)}")
        print(f"  Preview: {old_section[:200]}...")
    else:
        print("  Pattern not found at all")


# ============================================================================
# PATCH 2: Visão executiva (linhas ~3597-3601)
# ============================================================================
old_block_2 = """            const vSt = scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : null;
            const aSt = scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : null;

            if (vSt === 'cancelado' || vSt === 'canceled' || aSt === 'cancelado' || aSt === 'canceled') {
                scopy.status = 'Cancelado';"""

new_block_2 = """            const vSt = scopy.vindi ? (scopy.vindi.status_financeiro || scopy.vindi.status_assinatura) : null;
            const aSt = scopy.asaas ? (scopy.asaas.status_financeiro || scopy.asaas.status_assinatura) : null;
            const _vCan = vSt === 'cancelado' || vSt === 'canceled';
            const _aCan = aSt === 'cancelado' || aSt === 'canceled';
            const _vAct = vSt && !_vCan;
            const _aAct = aSt && !_aCan;

            if ((_vCan || _aCan) && !_vAct && !_aAct) {
                scopy.status = 'Cancelado';"""

if old_block_2 in content:
    content = content.replace(old_block_2, new_block_2)
    print("PATCH 2 (visão executiva): OK")
else:
    print("PATCH 2: BLOCO NÃO ENCONTRADO")

# ============================================================================
# PATCH 3: isMatriculaCancelada (linhas ~4264-4267)
# ============================================================================
old_block_3 = """    const isMatriculaCancelada = s => {
        const vSt = s.vindi ? (s.vindi.status_assinatura || s.vindi.status_financeiro) : null;
        const aSt = s.asaas ? (s.asaas.status_assinatura || s.asaas.status_financeiro) : null;
        return s.status === 'Cancelado' || vSt === 'canceled' || vSt === 'cancelado' || aSt === 'canceled' || aSt === 'cancelado';
    };"""

new_block_3 = """    const isMatriculaCancelada = s => {
        const vSt = s.vindi ? (s.vindi.status_assinatura || s.vindi.status_financeiro) : null;
        const aSt = s.asaas ? (s.asaas.status_assinatura || s.asaas.status_financeiro) : null;
        const _vCan = vSt === 'canceled' || vSt === 'cancelado';
        const _aCan = aSt === 'canceled' || aSt === 'cancelado';
        const _vAct = vSt && !_vCan;
        const _aAct = aSt && !_aCan;
        // Só considera cancelada se existe cancelamento E nenhum gateway ativo
        if (s.status === 'Cancelado') return true;
        return (_vCan || _aCan) && !_vAct && !_aAct;
    };"""

if old_block_3 in content:
    content = content.replace(old_block_3, new_block_3)
    print("PATCH 3 (isMatriculaCancelada): OK")
else:
    print("PATCH 3: BLOCO NÃO ENCONTRADO")


# ============================================================================
# Salvar
# ============================================================================
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nTemplate atualizado com sucesso!")
print("Próximo passo: rodar gerador.py para recompilar o dashboard.")
