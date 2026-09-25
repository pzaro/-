
from html import escape

def euro(x):
    return f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X",".")

def build_html_report(case, result):
    name = escape(case.get("identity",{}).get("name","ΙΤΧ"))
    rows = "".join(
        f"<tr><td>{escape(k)}</td><td>{v:.1f}/100</td></tr>"
        for k,v in result["domain_scores"].items()
    )
    flags = "".join(f"<li>{escape(x)}</li>" for x in result["red_flags"]) or "<li>Κανένα δηλωμένο hard-stop.</li>"
    gaps = "".join(f"<li>{escape(x)}</li>" for x in result["gaps"])
    icer = result["economics"]["icer"]
    icer_txt = "Μη υπολογίσιμο (ΔEffect=0)" if icer is None else euro(icer) + " ανά μονάδα αποτελέσματος"

    return f"""<!doctype html>
<html lang="el"><head><meta charset="utf-8">
<title>HTA Report - {name}</title>
<style>
body{{font-family:Arial,sans-serif;max-width:980px;margin:40px auto;line-height:1.5;color:#222}}
h1,h2{{color:#123b63}} table{{border-collapse:collapse;width:100%}}
td,th{{border:1px solid #ddd;padding:8px}} th{{background:#f3f5f7}}
.box{{padding:16px;background:#f7f9fb;border-left:4px solid #123b63;margin:16px 0}}
.warn{{padding:16px;background:#fff4e5;border-left:4px solid #d17b00;margin:16px 0}}
small{{color:#666}}
</style></head><body>
<h1>MedTech HTA Assessment Report</h1>
<p><b>Τεχνολογία:</b> {name}</p>
<p><b>Κατασκευαστής:</b> {escape(case.get("identity",{}).get("manufacturer",""))}</p>
<p><b>Μοντέλο:</b> {escape(case.get("identity",{}).get("model",""))}</p>

<div class="box"><b>Evidence readiness:</b> {result["readiness_score"]:.1f}/100<br>
<b>Uncertainty:</b> {escape(result["uncertainty"])}</div>

<h2>Domain profile</h2>
<table><tr><th>Domain</th><th>Score</th></tr>{rows}</table>

<h2>PICO</h2>
<p><b>Population:</b> {escape(case.get("pico",{}).get("population",""))}</p>
<p><b>Intervention:</b> {escape(case.get("pico",{}).get("intervention",""))}</p>
<p><b>Comparator:</b> {escape(case.get("pico",{}).get("comparator",""))}</p>
<p><b>Outcomes:</b> {escape(case.get("pico",{}).get("outcomes",""))}</p>

<h2>Economic snapshot</h2>
<ul>
<li>Annualized fixed cost: {euro(result["economics"]["annualized_fixed_cost"])}</li>
<li>Device cost / case: {euro(result["economics"]["device_cost_per_case"])}</li>
<li>Incremental cost / case: {euro(result["economics"]["incremental_cost_per_case"])}</li>
<li>ICER: {icer_txt}</li>
</ul>

<h2>Budget impact snapshot</h2>
<ul><li>Year 1: {euro(result["budget_impact"]["year1"])}</li>
<li>Year 3: {euro(result["budget_impact"]["year3"])}</li></ul>

<h2>Red flags</h2><div class="warn"><ul>{flags}</ul></div>
<h2>Evidence gaps / actions</h2><ul>{gaps}</ul>

<h2>Decision-support interpretation</h2>
<p>{escape(result["interpretation"])}</p>

<hr><small>
Το report είναι εργαλείο υποστήριξης HTA και όχι επίσημη κανονιστική, αποζημιωτική ή HTA απόφαση.
Τα scores πρέπει να τεκμηριώνονται με παραπομπές και να ελέγχονται από ανεξάρτητο reviewer.
</small></body></html>"""
