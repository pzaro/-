
DOMAIN_LABELS = {
    "regulatory": "Regulatory readiness",
    "pico": "PICO / decision problem",
    "clinical": "Clinical effectiveness",
    "safety": "Safety",
    "economic": "Economic evaluation",
    "budget": "Budget impact",
    "organizational": "Organizational impact",
    "ethical_rwe": "Ethical / social / RWE"
}

WEIGHTS = {
    "regulatory": 0.10,
    "pico": 0.10,
    "clinical": 0.25,
    "safety": 0.15,
    "economic": 0.15,
    "budget": 0.10,
    "organizational": 0.10,
    "ethical_rwe": 0.05
}

def pct(x, max_x=5):
    return max(0, min(100, (float(x)/max_x)*100))

def avg(values):
    vals = [float(v) for v in values]
    return sum(vals)/len(vals) if vals else 0.0

def evaluate_case(case):
    reg = case.get("regulatory", {})
    pico = case.get("pico", {})
    cl = case.get("clinical", {})
    sf = case.get("safety", {})
    ec = case.get("economic", {})
    bi = case.get("budget", {})
    org = case.get("organizational", {})
    eth = case.get("ethical", {})
    rwe = case.get("rwe", {})

    reg_items = ["ce","doc","udi","notified_body","ifu","cer","pms","pmcf","risk"]
    reg_score = 100 * sum(bool(reg.get(k,False)) for k in reg_items) / len(reg_items)

    pico_score = pct(pico.get("fit",0))
    clinical_score = avg([
        pct(cl.get("directness",0)),
        pct(cl.get("consistency",0)),
        pct(cl.get("precision",0)),
        pct(cl.get("effect",0))
    ])
    safety_score = avg([
        pct(sf.get("comparative",0)),
        pct(sf.get("vigilance",0)),
        pct(sf.get("risk_control",0))
    ])
    economic_score = pct(ec.get("model_quality",0))
    budget_score = pct(bi.get("quality",0))
    organizational_score = avg([
        pct(org.get("infrastructure",0)),
        pct(org.get("staff",0)),
        pct(org.get("training",0)),
        pct(org.get("workflow",0)),
        pct(org.get("scalability",0))
    ])
    ethical_rwe_score = avg([
        pct(eth.get("equity",0)),
        pct(eth.get("privacy",0)),
        pct(eth.get("acceptability",0)),
        pct(rwe.get("plan_quality",0))
    ])

    domain_scores = {
        "regulatory": reg_score,
        "pico": pico_score,
        "clinical": clinical_score,
        "safety": safety_score,
        "economic": economic_score,
        "budget": budget_score,
        "organizational": organizational_score,
        "ethical_rwe": ethical_rwe_score
    }
    readiness = sum(domain_scores[k] * WEIGHTS[k] for k in WEIGHTS)

    red_flags = []
    if not reg.get("ce", False):
        red_flags.append("Δεν έχει τεκμηριωθεί CE marking.")
    if not pico.get("comparator","").strip():
        red_flags.append("Δεν έχει οριστεί comparator / current standard of care.")
    if not pico.get("population","").strip():
        red_flags.append("Δεν έχει οριστεί επαρκώς ο πληθυσμός στόχος.")
    if sf.get("serious_signal", False):
        red_flags.append("Υπάρχει δηλωμένο unresolved serious safety signal.")
    if cl.get("certainty","Very low") == "Very low":
        red_flags.append("Η συνολική βεβαιότητα της κλινικής τεκμηρίωσης δηλώνεται ως Very low.")

    certainty = cl.get("certainty","Very low")
    uncertainty = {"High":"Χαμηλή", "Moderate":"Μέτρια", "Low":"Υψηλή", "Very low":"Πολύ υψηλή"}.get(certainty,"Υψηλή")

    life_years = max(1, int(ec.get("life_years",5) or 5))
    annual_cases = max(1, int(ec.get("annual_cases",1) or 1))
    annualized_fixed = (
        float(ec.get("acquisition",0)) +
        float(ec.get("installation",0)) +
        float(ec.get("training",0))
    ) / life_years + float(ec.get("maintenance",0))
    device_cost_per_case = annualized_fixed / annual_cases + float(ec.get("consumable_new",0))
    comparator_variable = float(ec.get("consumable_comp",0))
    delta_cost = device_cost_per_case - comparator_variable + float(ec.get("other_delta_cost",0))
    delta_effect = float(ec.get("delta_effect",0))
    icer = None if delta_effect == 0 else delta_cost/delta_effect

    eligible = int(bi.get("eligible",0) or 0)
    y1 = eligible * float(bi.get("uptake_y1",0))/100 * float(bi.get("net_cost_patient",0))
    y3 = eligible * float(bi.get("uptake_y3",0))/100 * float(bi.get("net_cost_patient",0))

    gaps = []
    if clinical_score < 60: gaps.append("Ενίσχυση comparative clinical evidence και τεκμηρίωση patient-relevant outcomes.")
    if economic_score < 60: gaps.append("Πλήρες cost-effectiveness / cost-utility model με sensitivity analyses.")
    if budget_score < 60: gaps.append("Ελληνικό budget impact model με epidemiology, uptake και scenario analyses.")
    if organizational_score < 60: gaps.append("Χαρτογράφηση υποδομών, staffing, learning curve και capacity ανά κέντρο.")
    if ethical_rwe_score < 60: gaps.append("Σχέδιο RWE/registry και αξιολόγηση equity, privacy/cybersecurity και acceptability.")
    if not gaps: gaps.append("Επικύρωση inputs, ανεξάρτητος έλεγχος πηγών και scenario/sensitivity analysis.")

    if red_flags:
        interpretation = ("Ο φάκελος δεν είναι ακόμη ώριμος για τελική HTA κρίση. "
                          "Υπάρχουν hard-stop ή major uncertainty στοιχεία που πρέπει να επιλυθούν πριν από οποιαδήποτε σύσταση.")
    elif readiness >= 75 and clinical_score >= 65 and safety_score >= 65:
        interpretation = ("Ο φάκελος εμφανίζει υψηλή προετοιμασία για πλήρη HTA αξιολόγηση. "
                          "Η τελική απόφαση πρέπει να βασιστεί στο comparative benefit, στο οικονομικό μοντέλο, "
                          "στο budget impact και στις αβεβαιότητες — όχι μόνο στο συνολικό readiness score.")
    elif readiness >= 55:
        interpretation = ("Ο φάκελος είναι μερικώς ώριμος, αλλά απαιτεί στοχευμένη συμπλήρωση evidence και οικονομικής/οργανωτικής τεκμηρίωσης.")
    else:
        interpretation = ("Ο φάκελος βρίσκεται σε πρώιμο στάδιο και χρειάζεται ουσιαστική συμπλήρωση πριν χρησιμοποιηθεί για HTA deliberation.")

    return {
        "domain_scores": domain_scores,
        "readiness_score": readiness,
        "red_flags": red_flags,
        "uncertainty": uncertainty,
        "gaps": gaps,
        "economics": {
            "annualized_fixed_cost": annualized_fixed,
            "device_cost_per_case": device_cost_per_case,
            "incremental_cost_per_case": delta_cost,
            "icer": icer
        },
        "budget_impact": {"year1": y1, "year3": y3},
        "interpretation": interpretation
    }
