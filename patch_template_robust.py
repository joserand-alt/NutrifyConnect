import os, re

target_paths = [
    r"c:\Users\DELL\Desktop\Dash_InfectoCast\template.html",
    r"c:\Users\DELL\Desktop\Acompanhamento de acessos\template.html"
]

patch_pendente_block = """            if (isPendente) {
                const rawInscStr = s.data_insc || s.data_inscricao || s.data_matricula || s.first || (s.asaas && s.asaas.faturas && s.asaas.faturas[0] && (s.asaas.faturas[0].data_criacao || s.asaas.faturas[0].dateCreated || s.asaas.faturas[0].vencimento_iso || s.asaas.faturas[0].vencimento)) || (s.vindi && s.vindi.faturas && s.vindi.faturas[0] && (s.vindi.faturas[0].vencimento_iso || s.vindi.faturas[0].vencimento)) || s.created_at;
                const dtInsc = parseDateUniversal(rawInscStr);
                if (dtInsc && dtInsc <= now) {
                    const pad = n => n < 10 ? '0' + n : n;
                    const dtFmt = pad(dtInsc.getDate()) + '/' + pad(dtInsc.getMonth()+1) + '/' + dtInsc.getFullYear() + (dtInsc.getHours() === 0 && dtInsc.getMinutes() === 0 ? '' : ' ' + pad(dtInsc.getHours()) + ':' + pad(dtInsc.getMinutes()));
                    
                    const diffMs = now.getTime() - dtInsc.getTime();
                    const t48hCalendar = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 2, 0, 0, 0);
                    const is48h = (dtInsc >= t48hCalendar && dtInsc <= now) || (diffMs >= -3600000 && diffMs <= 48 * 3600 * 1000) || (dtInsc.getHours() === 0 && diffMs <= 72 * 3600 * 1000 && diffMs >= -3600000);
                    const t30dCalendar = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30, 0, 0, 0);
                    const is30d = (dtInsc >= t30dCalendar && dtInsc <= now) || (diffMs <= 30 * 24 * 3600 * 1000);

                    let fatVal = 0;
                    let origStr = 'Cadastro Plataforma (' + (s.plataforma || 'Academy') + ')';
                    if (s.asaas && s.asaas.faturas && s.asaas.faturas.length > 0) {
                        fatVal = Number(s.asaas.faturas[0].valor || 0);
                        origStr = 'Pedido Asaas (' + (s.asaas.faturas[0].forma_pagamento || 'Boleto/PIX') + ')';
                    } else if (s.vindi && s.vindi.faturas && s.vindi.faturas.length > 0) {
                        fatVal = Number(s.vindi.faturas[0].valor || 0);
                        origStr = 'Assinatura Vindi';
                    }

                    matriculasPendentes.push({
                        nome: nm || 'Lead / Inscrição',
                        email: em,
                        curso: s.curso || 'PLATAFORMA GERAL',
                        data: dtInsc,
                        data_fmt: dtFmt,
                        origem: origStr,
                        gateway: s.plataforma || 'Academy',
                        tipo: 'pendente',
                        origem_label: 'Matrícula Pendente (Aguardando Pagamento)',
                        valor: fatVal,
                        aulas_feitas: Number(s.aulas_feitas || 0),
                        is_48h: is48h,
                        is_24h: is48h,
                        is_30d: is30d
                    });
                }
            }"""

for target_path in target_paths:
    if os.path.exists(target_path):
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the isPendente block inside getMatriculasAuditoriaData
        pattern = r'if\s*\(\s*isPendente\s*\)\s*\{\s*const rawInscStr = s\.data_insc.*?\n\s*\}\s*\}\s*\}\s*\)\s*;\s*matriculasConfirmadas\.sort'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            new_inner = patch_pendente_block + "\n            }\n        }\n    });\n\n    matriculasConfirmadas.sort"
            content_new = content[:match.start()] + new_inner + content[match.end():]
            
            # Also ensure confirmed is48h has calendar support
            content_new = content_new.replace(
                "const is48h = (diffMs <= 48 * 3600 * 1000) || (effDate.getHours() === 0 && diffMs <= 72 * 3600 * 1000 && diffMs >= -3600000);",
                "const t48hCalendar = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 2, 0, 0, 0);\n                const is48h = (effDate >= t48hCalendar && effDate <= now) || (diffMs >= -3600000 && diffMs <= 48 * 3600 * 1000) || (effDate.getHours() === 0 && diffMs <= 72 * 3600 * 1000 && diffMs >= -3600000);"
            )
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content_new)
            print(f"Patched {target_path} successfully!")
        else:
            print(f"Regex pattern match failed in {target_path}")
