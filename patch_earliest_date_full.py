import re

# 1. Update gerador.py
with open('gerador.py', 'r', encoding='utf-8') as f:
    gen_content = f.read()

# Replace the date inference block in gerador.py
target_block_start = gen_content.find('# Garantir que 100% dos alunos possuam data_insc real')
target_block_end = gen_content.find('# =========================================================================\n    # AUTO-HEALING DE CURSOS:', target_block_start)

new_gen_date_block = '''# Garantir que 100% dos alunos possuam data_insc real e CORRETA (sempre a data mais antiga / primeiro pagamento)
    for s in students:
        em_clean = str(s.get('email', '')).lower().strip()
        nm_clean = str(s.get('nome', '')).lower().strip()
        
        all_candidate_dates = []
        
        # 1. Checar Vindi (buscar menor data entre faturas e assinaturas)
        if s.get('vindi') and isinstance(s['vindi'], dict):
            fts = s['vindi'].get('faturas', [])
            for f in fts:
                dt_cand = f.get('data_pagamento') or f.get('data_pagamento_iso') or f.get('vencimento') or f.get('vencimento_iso')
                if dt_cand:
                    try:
                        all_candidate_dates.append(pd.to_datetime(str(dt_cand).split('T')[0], dayfirst=True))
                    except:
                        pass
            if s['vindi'].get('created_at'):
                try:
                    all_candidate_dates.append(pd.to_datetime(str(s['vindi']['created_at']).split('T')[0]))
                except:
                    pass

        # 2. Checar Asaas (buscar menor data entre faturas)
        if s.get('asaas') and isinstance(s['asaas'], dict):
            fts = s['asaas'].get('faturas', [])
            for f in fts:
                dt_cand = f.get('data_pagamento') or f.get('data_pagamento_iso') or f.get('vencimento') or f.get('vencimento_iso')
                if dt_cand:
                    try:
                        all_candidate_dates.append(pd.to_datetime(str(dt_cand).split('T')[0], dayfirst=True))
                    except:
                        pass
            if s['asaas'].get('created_at'):
                try:
                    all_candidate_dates.append(pd.to_datetime(str(s['asaas']['created_at']).split('T')[0]))
                except:
                    pass

        # 3. Checar Cativa Users Metadata
        if 'cativa_users_meta' in locals() and em_clean in cativa_users_meta:
            c_meta_st = cativa_users_meta[em_clean]
            if c_meta_st.get('created_at'):
                try:
                    all_candidate_dates.append(pd.to_datetime(str(c_meta_st['created_at']).split('T')[0]))
                except:
                    pass
            elif c_meta_st.get('last_login_at'):
                try:
                    all_candidate_dates.append(pd.to_datetime(str(c_meta_st['last_login_at']).split('T')[0]))
                except:
                    pass

        # 4. Checar primeiro log de acesso
        if s.get('first'):
            try:
                all_candidate_dates.append(pd.to_datetime(str(s['first']).split('T')[0], dayfirst=True))
            except:
                pass

        # 5. Data de inscrição existente
        dt_orig = s.get('data_insc') or s.get('data_inscricao') or s.get('inscricao')
        if dt_orig:
            try:
                dt_orig_parsed = pd.to_datetime(str(dt_orig).split('T')[0], dayfirst=True)
                # Só aceitar se não for no futuro em relação a hoje
                if dt_orig_parsed.date() <= datetime.date.today():
                    all_candidate_dates.append(dt_orig_parsed)
            except:
                pass

        # 6. Escolher a data mais antiga real (primeiro marco temporal)
        final_dt_str = None
        if all_candidate_dates:
            valid_dates = [d for d in all_candidate_dates if pd.notnull(d) and d.date() <= datetime.date.today()]
            if valid_dates:
                earliest_d = min(valid_dates)
                final_dt_str = earliest_d.strftime('%d/%m/%Y')

        if not final_dt_str and dt_orig:
            final_dt_str = str(dt_orig)[:10]

        if final_dt_str:
            s['data_insc'] = final_dt_str
            s['data_inscricao'] = final_dt_str
            s['inscricao'] = final_dt_str

    '''

if target_block_start != -1 and target_block_end != -1:
    gen_content = gen_content[:target_block_start] + new_gen_date_block + gen_content[target_block_end:]
    with open('gerador.py', 'w', encoding='utf-8') as f:
        f.write(gen_content)
    print("gerador.py updated with earliest date auto-healing!")
else:
    print("WARNING: Could not find target block in gerador.py")

# 2. Update template.html
with open('template.html', 'r', encoding='utf-8') as f:
    tmpl = f.read()

# Update getMatriculasAuditoriaData in template.html
get_mat_start = tmpl.find('function getMatriculasAuditoriaData() {')
get_mat_end = tmpl.find('function getSync24hData() {', get_mat_start)

new_tmpl_get_mat = '''function getMatriculasAuditoriaData() {
    const rawStudents = (DATA && DATA.students) ? DATA.students : [];
    const vindi = (DATA && DATA.financeiro) ? DATA.financeiro : {};
    const asaas = (DATA && DATA.financeiro_asaas) ? DATA.financeiro_asaas : {};
    const vFaturas = (vindi.faturas_tabela || []);
    const aFaturas = (asaas.faturas_tabela || []);

    const isInvalidOrInternal = s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().toLowerCase().trim();
        const cr = (s.curso || '').toString().toUpperCase().trim();
        if (cr.includes('NUTRIFY')) return true;
        if (em.includes('@infectocast') || em.includes('@integralmedica') || em.includes('@nutrify') || em.includes('@cativa') || em.includes('@estrategia1') || em.includes('@adtivo')) return true;
        if (em.includes('teste') || nm.includes('teste')) return true;
        if (em.includes('gcotta29') || em.includes('j.o.s.e.r.a.n.d@gmail.com') || em.includes('email@email.com') || em.includes('wgww@gmail.com')) return true;
        return false;
    };

    // Mapear primeiro pagamento de cada aluno (menor data de pagamento ou vencimento da fatura paga)
    const firstPayMap = new Map();
    [...vFaturas, ...aFaturas].forEach(f => {
        const st = (f.status || '').toLowerCase();
        if (st === 'pago' || st === 'paid' || st === 'received' || st === 'confirmed') {
            const em = (f.email || '').toString().toLowerCase().trim();
            const nm = (f.aluno || '').toString().toLowerCase().trim();
            const dtStr = (f.data_pagamento || f.data_pagamento_iso || f.vencimento || f.vencimento_iso || f.data || '').toString();
            const d = parseDateUniversal(dtStr);
            const gw = (f.gateway || (vFaturas.includes(f) ? 'Vindi' : 'Asaas'));
            if (d) {
                if (em) {
                    if (!firstPayMap.has(em) || d < firstPayMap.get(em).date) {
                        firstPayMap.set(em, { date: d, gateway: gw, valor: f.valor });
                    }
                }
                if (nm) {
                    if (!firstPayMap.has(nm) || d < firstPayMap.get(nm).date) {
                        firstPayMap.set(nm, { date: d, gateway: gw, valor: f.valor });
                    }
                }
            }
        }
    });

    const now = new Date();
    const t24h = new Date(now.getTime() - 24 * 3600 * 1000);
    const t30d = new Date(now.getTime() - 30 * 24 * 3600 * 1000);

    const validStudents = rawStudents.filter(s => !isInvalidOrInternal(s));
    const allMatriculas = [];

    validStudents.forEach(s => {
        const em = (s.email || '').toString().toLowerCase().trim();
        const nm = (s.nome || '').toString().trim();
        
        // Candidatos temporais (menor data = primeiro evento real do aluno)
        const candidates = [];
        
        // 1. Primeiro Pagamento
        const payInfo = firstPayMap.get(em) || firstPayMap.get(nm.toLowerCase());
        if (payInfo) {
            candidates.append ? null : candidates.push({ date: payInfo.date, origem: `Primeiro Pagamento (${payInfo.gateway})`, tipo: 'gateway' });
        }

        // 2. Faturas Vindi no objeto do aluno (menor vencimento)
        if (s.vindi && s.vindi.faturas && Array.isArray(s.vindi.faturas)) {
            s.vindi.faturas.forEach(vf => {
                const d = parseDateUniversal(vf.data_pagamento || vf.vencimento);
                if (d) candidates.push({ date: d, origem: 'Primeiro Pagamento (Vindi)', tipo: 'gateway' });
            });
        }

        // 3. Faturas Asaas no objeto do aluno
        if (s.asaas && s.asaas.faturas && Array.isArray(s.asaas.faturas)) {
            s.asaas.faturas.forEach(af => {
                const d = parseDateUniversal(af.data_pagamento || af.vencimento);
                if (d) candidates.push({ date: d, origem: 'Primeiro Pagamento (Asaas)', tipo: 'gateway' });
            });
        }

        // 4. Primeiro Acesso / Log
        if (s.first) {
            const d = parseDateUniversal(s.first);
            if (d) candidates.push({ date: d, origem: 'Primeiro Acesso / Log', tipo: 'log' });
        }

        // 5. Data de Inscrição da Plataforma
        const dtInsc = parseDateUniversal(s.data_insc || s.data_inscricao || s.data_matricula);
        if (dtInsc && dtInsc <= now) {
            const plat = s.plataforma || 'Academy';
            candidates.push({ date: dtInsc, origem: `Cadastro ${plat}`, tipo: 'plataforma' });
        }

        if (candidates.length > 0) {
            // Filtrar apenas datas não nulas e menores ou iguais a agora
            const valid = candidates.filter(c => c.date && c.date <= now);
            if (valid.length > 0) {
                // Ordenar pela menor data (marco temporal inicial)
                valid.sort((a, b) => a.date - b.date);
                const chosen = valid[0];
                const effDate = chosen.date;
                const dtFmt = `${String(effDate.getDate()).padStart(2,'0')}/${String(effDate.getMonth()+1).padStart(2,'0')}/${effDate.getFullYear()} ${String(effDate.getHours()).padStart(2,'0')}:${String(effDate.getMinutes()).padStart(2,'0')}`;
                
                allMatriculas.push({
                    nome: nm || 'Aluno',
                    email: em,
                    curso: s.curso || 'PLATAFORMA GERAL',
                    data: effDate,
                    data_fmt: dtFmt,
                    origem_sinal: chosen.origem,
                    tipo_sinal: chosen.tipo,
                    status: s.status || 'Ativo',
                    is_24h: effDate >= t24h,
                    is_30d: effDate >= t30d
                });
            }
        }
    });

    // Ordenar decrescente por data de matrícula para exibição
    allMatriculas.sort((a, b) => b.data - a.data);

    const list24h = allMatriculas.filter(m => m.is_24h);
    const list30d = allMatriculas.filter(m => m.is_30d);

    return {
        count24h: list24h.length,
        count30d: list30d.length,
        total: allMatriculas.length,
        list24h: list24h,
        list30d: list30d,
        allRecords: allMatriculas
    };
}

'''

if get_mat_start != -1 and get_mat_end != -1:
    tmpl = tmpl[:get_mat_start] + new_tmpl_get_mat + tmpl[get_mat_end:]
    with open('template.html', 'w', encoding='utf-8') as f:
        f.write(tmpl)
    print("template.html updated with robust earliest event logic!")
else:
    print("WARNING: Could not find getMatriculasAuditoriaData in template.html")
