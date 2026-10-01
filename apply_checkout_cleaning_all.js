const fs = require('fs');

function isCheckoutEvent(ev) {
    if (!ev) return false;
    const cat = (ev.categoria || '').toLowerCase();
    const raw = (ev.evento_raw || '').toLowerCase();
    const clean = (ev.evento_clean || '').toLowerCase();
    if (cat.includes('checkout') || cat.includes('matrícula') || cat.includes('matricula')) return true;
    if (raw.includes('checkout') || raw.includes('pago') || raw.includes('pendente') || raw.includes('recorrencia') || raw.includes('compra') || raw.includes('problema') || raw.includes('hotmart') || raw.includes('woocommerce')) return true;
    if (clean.includes('checkout') || clean.includes('pagamento') || clean.includes('compra')) return true;
    return false;
}

function isCheckoutString(s) {
    if (!s) return false;
    const low = s.toString().toLowerCase();
    return low.includes('checkout') || low.includes('pagamento') || low.includes('pago') || low.includes('pendente') || low.includes('recorrencia') || low.includes('compra') || low.includes('problema') || low.includes('hotmart') || low.includes('woocommerce');
}

// Read updated template.html to copy the updated UI functions
const templateHtml = fs.readFileSync('C:/Users/DELL/Desktop/Dash_InfectoCast/template.html', 'utf8');

const idx_rd_start = templateHtml.indexOf("let rdHtml = '';\n  if (s.rd_funnel) {");
const idx_rd_end = templateHtml.indexOf("</div>\n      </div>`;\n  }", idx_rd_start) + "</div>\n      </div>`;\n  }".length;
const new_rdhtml_code = templateHtml.slice(idx_rd_start, idx_rd_end);

const idx_origem_start = templateHtml.indexOf('// ORIGENS & ATRIBUIÇÃO DE MATRÍCULAS');
const idx_origem_end = templateHtml.indexOf('// ==================== VISÃO GERAL / HOME ====================', idx_origem_start);
const new_origem_code = templateHtml.slice(idx_origem_start, idx_origem_end);

const files = [
    'C:/Users/DELL/Desktop/Dash_InfectoCast/index.html',
    'C:/Users/DELL/Desktop/Dash_InfectoCast/dashboard_gerado.html'
];

files.forEach(filePath => {
    console.log(`\nProcessing ${filePath}...`);
    let html = fs.readFileSync(filePath, 'utf8');

    // 1. Replace UI functions
    const rStart = html.indexOf("let rdHtml = '';\n  if (s.rd_funnel) {");
    if (rStart !== -1) {
        const rEnd = html.indexOf("</div>\n      </div>`;\n  }", rStart) + "</div>\n      </div>`;\n  }".length;
        html = html.slice(0, rStart) + new_rdhtml_code + html.slice(rEnd);
        console.log('  Replaced rdHtml');
    }

    const oStart = html.indexOf('// ORIGENS & ATRIBUI');
    if (oStart !== -1) {
        const oEnd = html.indexOf('// ==================== VISÃO GERAL / HOME ====================', oStart);
        html = html.slice(0, oStart) + new_origem_code + html.slice(oEnd);
        console.log('  Replaced Origem section');
    }

    // 2. Parse and clean DATA
    const dStart = html.indexOf('const DATA = {');
    const cdIdx = html.indexOf('let CURRENT_DATA', dStart);
    const dEnd = html.lastIndexOf('};', cdIdx);
    
    const jsDataStr = html.slice(dStart + 'const DATA = '.length, dEnd + 1);
    try {
        const dataObj = JSON.parse(jsDataStr);
        let cleanedStudents = 0;
        let eventsRemoved = 0;

        (dataObj.students || []).forEach(s => {
            if (s.rd_funnel) {
                const evs = s.rd_funnel.eventos_detalhados || [];
                const fmt = s.rd_funnel.eventos || [];

                const newEvs = evs.filter(e => !isCheckoutEvent(e));
                const newFmt = fmt.filter(e => !isCheckoutString(e));

                if (evs.length !== newEvs.length || fmt.length !== newFmt.length) {
                    cleanedStudents++;
                    eventsRemoved += (evs.length - newEvs.length);
                    s.rd_funnel.eventos_detalhados = newEvs;
                    s.rd_funnel.eventos = newFmt;
                    s.rd_funnel.conversoes_antes = newEvs.length;
                    if (newEvs.length > 0 && newEvs[0].data) {
                        s.rd_funnel.dt_primeira = newEvs[0].data;
                    } else if (newEvs.length === 0) {
                        s.rd_funnel.dt_primeira = '—';
                        s.rd_funnel.dias_venda = '';
                    }
                }
            }
        });

        console.log(`  Cleaned ${cleanedStudents} students, removed ${eventsRemoved} checkout events from embedded DATA.`);
        const newJsonStr = JSON.stringify(dataObj);
        html = html.slice(0, dStart + 'const DATA = '.length) + newJsonStr + html.slice(dEnd + 1);
    } catch (e) {
        console.error('  Error parsing embedded DATA JSON:', e.message);
    }

    fs.writeFileSync(filePath, html, 'utf8');
    console.log(`Successfully updated and saved ${filePath}`);
});
