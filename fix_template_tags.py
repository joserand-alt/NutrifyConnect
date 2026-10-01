import re

def fix_template():
    paths = [
        'c:/Users/DELL/Desktop/Dash_InfectoCast/template.html',
        'c:/Users/DELL/Desktop/Acompanhamento de acessos/template.html'
    ]

    for p in paths:
        with open(p, 'r', encoding='utf-8') as f:
            html = f.read()

        # Fix broken </div ... > in home-live-section
        broken_pattern = r'</div\s*<div class="kpis" id="home-kpis-grid"[^>]*></div>\s*<!-- SEÇÃO AO VIVO & MONITORAMENTO DE 24H -->\s*>'
        # Let's inspect the exact broken text in home section
        broken_text = """    </div

    <div class="kpis" id="home-kpis-grid" style="margin-top:0; margin-bottom:24px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));"></div>

    <!-- SEÇÃO AO VIVO & MONITORAMENTO DE 24H -->

    >"""

        clean_home_live_end = """    </div>

    <div class="kpis" id="home-kpis-grid" style="margin-top:0; margin-bottom:24px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));"></div>"""

        if broken_text in html:
            html = html.replace(broken_text, clean_home_live_end)
            print(f"Fixed broken text in {p}")
        else:
            # Try regex replacement if whitespace differed
            html = re.sub(
                r'</div\s+<div class="kpis" id="home-kpis-grid"[^>]*></div>\s+<!--[^\n]*-->\s+>',
                clean_home_live_end,
                html
            )
            print(f"Regex replacement attempted on {p}")

        # Also check the end of p-home
        # The end of p-home had an extra unclosed </div> before </section>
        # Let's clean up the end of p-home
        end_p_home_old = """      </div>
    </div>
  </div>
  </section>"""
        end_p_home_clean = """      </div>
    </div>
  </section>"""
        if end_p_home_old in html:
            html = html.replace(end_p_home_old, end_p_home_clean)
            print(f"Fixed extra </div> at end of p-home in {p}")

        with open(p, 'w', encoding='utf-8') as f:
            f.write(html)

    print("Template files updated!")

if __name__ == '__main__':
    fix_template()
