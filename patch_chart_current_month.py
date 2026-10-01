template_path = r'C:\Users\DELL\Desktop\Dash_InfectoCast\template.html'

with open(template_path, 'r', encoding='utf-8') as f:
    text = f.read()

old_bars_block = """        if (hv > 0) {
            const bh = Math.max(2, (hv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            svg += `<rect x="${cx - grpW / 2}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradGreen)" opacity="${isFuture ? 0.4 : 1}">
                <title>${labelsMap[mes]}: R$ ${hv.toLocaleString('pt-BR', {minimumFractionDigits:2})}</title></rect>`;
        }
        if (pv > 0 && isFuture) {
            const bh = Math.max(2, (pv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            svg += `<rect x="${cx + 2}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradBlue)" opacity="0.75">
                <title>Projeção ${labelsMap[mes]}: R$ ${pv.toLocaleString('pt-BR', {minimumFractionDigits:2})}</title></rect>`;
        }

        // X-axis label
        svg += `<text x="${cx}" y="${H - 4}" text-anchor="middle" font-size="9" fill="var(--muted)">${labelsMap[mes] || mes}</text>`;"""

new_bars_block = """        const isCurrent = (mes === today);
        const hasBoth = (hv > 0 && pv > 0 && (isCurrent || isFuture));

        // 1. Realizado (Verde)
        if (hv > 0) {
            const bh = Math.max(2, (hv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            const bx = hasBoth ? (cx - grpW / 2) : (cx - barW / 2);
            svg += `<rect x="${bx}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradGreen)" opacity="${isFuture ? 0.4 : 1}">
                <title>${labelsMap[mes]} - Realizado: R$ ${hv.toLocaleString('pt-BR', {minimumFractionDigits:2})}</title>
            </rect>`;
        }

        // 2. Projeção (Azul) - Exibe no mês atual E meses futuros
        if (pv > 0 && (isCurrent || isFuture)) {
            const bh = Math.max(2, (pv / maxVal) * (H - padT - padB));
            const by = H - padB - bh;
            const bx = hasBoth ? (cx + 2) : (cx - barW / 2);
            svg += `<rect x="${bx}" y="${by}" width="${barW}" height="${bh}" rx="3" fill="url(#gradBlue)" opacity="${isCurrent ? 0.95 : 0.75}">
                <title>${labelsMap[mes]} - Projeção: R$ ${pv.toLocaleString('pt-BR', {minimumFractionDigits:2})}</title>
            </rect>`;
        }

        // X-axis label com destaque no mês atual
        const labelColor = isCurrent ? 'var(--emerald)' : 'var(--muted)';
        const labelWeight = isCurrent ? '800' : '500';
        svg += `<text x="${cx}" y="${H - 4}" text-anchor="middle" font-size="9" fill="${labelColor}" font-weight="${labelWeight}">${labelsMap[mes] || mes}</text>`;"""

if old_bars_block in text:
    text = text.replace(old_bars_block, new_bars_block)
    print("Chart bars updated directly!")
else:
    import re
    p = re.compile(r"if \(hv > 0\) \{[\s\S]*?if \(pv > 0 && isFuture\) \{[\s\S]*?svg \+= `<text x=\"\$\{cx\}\" y=\"\$\{H - 4\}\" text-anchor=\"middle\" font-size=\"9\" fill=\"var\(--muted\)\">\$\{labelsMap\[mes\] \|\| mes\}</text>`;")
    text, n = p.subn(new_bars_block, text)
    print("Chart bars replaced via regex:", n)

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved template.html")
