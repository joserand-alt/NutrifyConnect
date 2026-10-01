import os, re

def update():
    base_dir = r"c:\Users\DELL\Desktop\Acompanhamento de acessos"
    dash_dir = r"C:\Users\DELL\Desktop\Dash_InfectoCast"
    
    tmpl_path = os.path.join(base_dir, "template.html")
    dash_path = os.path.join(base_dir, "dashboard_gerado.html")
    
    with open(tmpl_path, "r", encoding="utf-8") as f:
        tmpl = f.read()
        
    with open(dash_path, "r", encoding="utf-8") as f:
        dash = f.read()
        
    # Extract DATA from dashboard_gerado.html
    m = re.search(r"const DATA = (\{.*?\});", dash)
    if not m:
        print("DATA not found in dashboard_gerado.html")
        return
        
    data_str = m.group(1)
    
    # Inject into template
    start_str = "const DATA = {"
    end_str = "};"
    start_idx = tmpl.find(start_str)
    end_idx = tmpl.find(end_str, start_idx) + 1
    
    new_html = tmpl[:start_idx] + "const DATA = " + data_str + ";" + tmpl[end_idx:]
    
    with open(dash_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("Updated", dash_path)
    
    index_local = os.path.join(base_dir, "index.html")
    with open(index_local, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("Updated", index_local)
    
    # Also update Dash_InfectoCast
    if os.path.exists(dash_dir):
        dash_pub = os.path.join(dash_dir, "dashboard_gerado.html")
        index_pub = os.path.join(dash_dir, "index.html")
        with open(dash_pub, "w", encoding="utf-8") as f:
            f.write(new_html)
        with open(index_pub, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("Updated", dash_pub, "and", index_pub)

if __name__ == "__main__":
    update()
