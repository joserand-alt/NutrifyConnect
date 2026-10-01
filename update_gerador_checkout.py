gerador_path = r'C:/Users/DELL/Desktop/Dash_InfectoCast/gerador.py'

with open(gerador_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update categorize_rd_event and add is_checkout_event
old_cat = """def categorize_rd_event(ev_name):
    low = ev_name.lower().strip()
    if any(x in low for x in ['ebook', 'e-book', 'biofilme', 'candidiase', 'imuno', 'orto', 'ist']): return 'E-book / Material'
    if any(x in low for x in ['jornada', 'live', 'infectoxpert', 'congresso', 'webinar', 'webnar', 'evento', 'aula']): return 'Evento / Live'
    if any(x in low for x in ['fale-conosco', 'duvida', 'contato', 'form_3', 'fluentform', 'atendimento']): return 'Fale Conosco / Contato'
    if any(x in low for x in ['lista-espera', 'lista de espera', 'pre-inscricao', 'pr-inscrio', 'pre_antifungico', 'sos', 'grade_pos']): return 'Lista de Espera / Grade'
    if any(x in low for x in ['ex alunos', 'alunos infectoped', 'ex-alunos']): return 'Comunidade / Base Prvia'
    if any(x in low for x in ['pago', 'pendente', 'recorrencia', 'checkout', 'compra']): return 'Checkout / Matrcula'
    return 'Outras Aes'"""

new_cat = """def is_checkout_event(ev_name):
    low = (ev_name or '').lower().strip()
    return any(x in low for x in [
        'pago', 'pendente', 'recorrencia', 'checkout', 'compra',
        'pagamento', 'problema', 'hotmart', 'woocommerce'
    ])

def categorize_rd_event(ev_name):
    low = (ev_name or '').lower().strip()
    if is_checkout_event(low): return 'Checkout / Matrícula'
    if any(x in low for x in ['ebook', 'e-book', 'biofilme', 'candidiase', 'imuno', 'orto', 'ist']): return 'E-book / Material'
    if any(x in low for x in ['jornada', 'live', 'infectoxpert', 'congresso', 'webinar', 'webnar', 'evento', 'aula']): return 'Evento / Live'
    if any(x in low for x in ['fale-conosco', 'duvida', 'contato', 'form_3', 'fluentform', 'atendimento']): return 'Fale Conosco / Contato'
    if any(x in low for x in ['lista-espera', 'lista de espera', 'pre-inscricao', 'pré-inscrição', 'pre_antifungico', 'sos', 'grade_pos']): return 'Lista de Espera / Grade'
    if any(x in low for x in ['ex alunos', 'alunos infectoped', 'ex-alunos']): return 'Comunidade / Base Prévia'
    return 'Outras Ações'"""

if old_cat in text:
    text = text.replace(old_cat, new_cat, 1)
    print("Replaced categorize_rd_event in gerador.py")
else:
    # Try finding with regex or substring
    idx = text.find('def categorize_rd_event')
    idx_end = text.find('def clean_rd_event_name', idx)
    text = text[:idx] + new_cat + '\n\n' + text[idx_end:]
    print("Replaced categorize_rd_event via index in gerador.py")

# 2. Update loop for conv_list
idx_loop = text.find('for ev in conv_list:')
if idx_loop != -1:
    idx_loop_end = text.find("s['rd_funnel'] = {", idx_loop)
    idx_loop_end = text.find('}', idx_loop_end) + 1
    
    old_loop_chunk = text[idx_loop:idx_loop_end]
    new_loop_chunk = """for ev in conv_list:
                    data_f = ev.get('data_formatada', '')
                    ident = ev.get('evento', '')
                    cat = categorize_rd_event(ident)
                    clean_name = clean_rd_event_name(ident)
                    
                    # Desconsiderar tudo que for Checkout / Matrícula (conversão final de compra)
                    if cat == 'Checkout / Matrícula' or is_checkout_event(ident):
                        continue
                    
                    if (data_f, ident) == last_ident:
                        continue
                    last_ident = (data_f, ident)
                    
                    fmt_eventos.append(f"<span style='color:var(--muted)'>{data_f}</span> &mdash; <b>{clean_name}</b>")
                    eventos_raw_list.append({
                        'data': data_f,
                        'evento_raw': ident,
                        'evento_clean': clean_name,
                        'categoria': cat
                    })
                
                # Calcular dias de maturação com precisão (Data Matrícula - 1ª Conversão RD Pré-Matrícula)
                dias_maturacao = ''
                dt_primeira_real = ast.get('dt_primeira')
                if eventos_raw_list:
                    dt_primeira_real = eventos_raw_list[0].get('data') or ast.get('dt_primeira')
                else:
                    dt_primeira_real = '—'
                
                try:
                    dt_insc_raw = s.get('data_insc') or s.get('data_inscricao') or s.get('inscricao')
                    if dt_insc_raw and dt_primeira_real and dt_primeira_real not in ('?', '—', '-'):
                        d_insc = pd.to_datetime(dt_insc_raw, dayfirst=True)
                        d_pri = pd.to_datetime(dt_primeira_real[:10], dayfirst=True)
                        diff = (d_insc.date() - d_pri.date()).days
                        if diff >= 0:
                            dias_maturacao = int(diff)
                except Exception as e_mat:
                    pass
                    
                s['rd_funnel'] = {
                    'origem': ast.get('origem_funil') or 'Desconhecido',
                    'conversoes': ast.get('total_conversoes', 0),
                    'conversoes_antes': len(eventos_raw_list),
                    'scoring': ast.get('score_interesse', 0),
                    'dias_venda': dias_maturacao,
                    'dt_primeira': dt_primeira_real,
                    'dt_ultima': ast.get('dt_ultima', '—'),
                    'eventos': fmt_eventos,
                    'eventos_detalhados': eventos_raw_list,
                    'fonte': 'API Oficial RD Station'
                }"""
    text = text[:idx_loop] + new_loop_chunk + text[idx_loop_end:]
    print("Replaced conv_list loop in gerador.py")

with open(gerador_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("gerador.py successfully updated and saved")
