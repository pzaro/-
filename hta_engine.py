
DOMAIN_LABELS = {
    "eligibility":"Eligibility / JCA",
    "regulatory":"Regulatory readiness",
    "pico":"PICO / decision problem",
    "clinical":"Clinical benefit",
    "safety":"Clinical safety",
    "organizational":"Organizational impact",
    "economic":"Economic evaluation",
    "budget":"Budget impact",
    "social":"Social impact",
    "legal_ethical":"Legal & ethical",
    "use_safety":"Safety in use",
    "unmet_need":"Unmet health need",
    "rwe":"RWE readiness"
}

WEIGHTS = {
    "eligibility":0.05, "regulatory":0.08, "pico":0.08, "clinical":0.18,
    "safety":0.10, "organizational":0.08, "economic":0.12, "budget":0.08,
    "social":0.05, "legal_ethical":0.05, "use_safety":0.06,
    "unmet_need":0.04, "rwe":0.03
}

def pct(x,max_x=5):
    return max(0,min(100,float(x)/max_x*100))

def avg(vals):
    vals=[float(x) for x in vals]
    return sum(vals)/len(vals) if vals else 0.0

def evaluate_case(case):
    elig=case.get("eligibility",{})
    reg=case.get("regulatory",{})
    pico=case.get("pico",{})
    cl=case.get("clinical",{})
    sf=case.get("safety",{})
    org=case.get("organizational",{})
    ec=case.get("economic",{})
    bi=case.get("budget",{})
    social=case.get("social",{})
    le=case.get("legal_ethical",{})
    us=case.get("use_safety",{})
    un=case.get("unmet_need",{})
    unc=case.get("uncertainty",{})
    rwe=case.get("rwe",{})

    eligibility_score = 100 if elig.get("jca_available") else 0
    reg_keys=["ce","doc","udi","notified_body","ifu","cer","pms","pmcf","risk"]
    regulatory_score=100*sum(bool(reg.get(k,False)) for k in reg_keys)/len(reg_keys)
    pico_score=pct(pico.get("fit",0))
    clinical_score=avg([pct(cl.get("directness",0)),pct(cl.get("consistency",0)),
                        pct(cl.get("precision",0)),pct(cl.get("effect",0))])
    safety_score=avg([pct(sf.get("comparative",0)),pct(sf.get("vigilance",0)),pct(sf.get("risk_control",0))])
    organizational_score=avg([pct(org.get(k,0)) for k in ["infrastructure","staff","training","workflow","scalability"]])
    economic_score=pct(ec.get("model_quality",0))
    budget_score=pct(bi.get("quality",0))
    social_score=avg([pct(social.get(k,0)) for k in ["equity","patient_burden","geographic","acceptability"]])
    legal_ethical_score=avg([pct(le.get(k,0)) for k in ["privacy","cybersecurity","consent","liability","fairness"]])
    use_safety_score=avg([pct(us.get(k,0)) for k in ["usability","operator_error","training","alarms","maintenance"]])
    unmet_need_score=avg([pct(un.get(k,0)) for k in ["alternatives","severity","burden","subgroup"]])
    rwe_score=avg([100 if rwe.get("registry") else 0, pct(rwe.get("plan_quality",0))])

    domain_scores={
        "eligibility":eligibility_score,"regulatory":regulatory_score,"pico":pico_score,
        "clinical":clinical_score,"safety":safety_score,"organizational":organizational_score,
        "economic":economic_score,"budget":budget_score,"social":social_score,
        "legal_ethical":legal_ethical_score,"use_safety":use_safety_score,
        "unmet_need":unmet_need_score,"rwe":rwe_score
    }
    readiness=sum(domain_scores[k]*WEIGHTS[k] for k in WEIGHTS)

    uncertainty_raw=avg([pct(unc.get(k,0)) for k in ["clinical","economic","implementation","long_term"]])
    if uncertainty_raw>=80: uncertainty_label="Πολύ υψηλή"
    elif uncertainty_raw>=60: uncertainty_label="Υψηλή"
    elif uncertainty_raw>=40: uncertainty_label="Μέτρια"
    elif uncertainty_raw>=20: uncertainty_label="Χαμηλή"
    else: uncertainty_label="Πολύ χαμηλή"

    red_flags=[]
    if not elig.get("jca_available",False):
        red_flags.append("Δεν έχει δηλωθεί δημοσιευμένη JCA για τη συγκεκριμένη διαδρομή αξιολόγησης.")
    if not reg.get("ce",False):
        red_flags.append("Δεν έχει τεκμηριωθεί CE marking.")
    if not pico.get("comparator","").strip():
        red_flags.append("Δεν έχει οριστεί comparator/current standard of care.")
    if sf.get("serious_signal",False):
        red_flags.append("Υπάρχει unresolved serious clinical safety signal.")
    if us.get("critical_use_risk",False):
        red_flags.append("Υπάρχει κρίσιμος unresolved κίνδυνος safety-in-use.")
    if cl.get("certainty","Very low")=="Very low":
        red_flags.append("Η συνολική clinical evidence certainty δηλώνεται Very low.")

    life=max(1,int(ec.get("life_years",5) or 5))
    cases=max(1,int(ec.get("annual_cases",1) or 1))
    upfront=float(ec.get("acquisition",0))+float(ec.get("installation",0))+float(ec.get("training",0))
    annualized=upfront/life+float(ec.get("maintenance",0))
    device_cost_case=annualized/cases+float(ec.get("consumable_new",0))
    delta_cost=device_cost_case-float(ec.get("consumable_comp",0))+float(ec.get("other_delta_cost",0))
    de=float(ec.get("delta_effect",0))
    icer=None if de==0 else delta_cost/de

    eligible=int(bi.get("eligible",0) or 0)
    y1_users=eligible*float(bi.get("uptake_y1",0))/100
    y3_users=eligible*float(bi.get("uptake_y3",0))/100
    y1=y1_users*float(bi.get("net_cost_patient",0))
    y3=y3_users*float(bi.get("net_cost_patient",0))

    gaps=[]
    if clinical_score<60: gaps.append("Ενίσχυση comparative clinical evidence και patient-relevant outcomes.")
    if safety_score<60: gaps.append("Ενίσχυση comparative safety/vigilance evidence.")
    if organizational_score<60: gaps.append("Λεπτομερής organizational/capacity analysis.")
    if economic_score<60: gaps.append("Πλήρες economic model με sensitivity/scenario analyses.")
    if budget_score<60: gaps.append("Ελληνικό budget impact model με epidemiology και uptake scenarios.")
    if social_score<60: gaps.append("Τεκμηρίωση social impact και equity.")
    if legal_ethical_score<60: gaps.append("Πλήρης legal/ethical/cybersecurity assessment.")
    if use_safety_score<60: gaps.append("Human factors/usability και safety-in-use evidence.")
    if unmet_need_score<40: gaps.append("Καλύτερη τεκμηρίωση unmet health need.")
    if rwe_score<50: gaps.append("Σχέδιο RWE/registry για unresolved uncertainties.")

    if red_flags:
        interpretation=("Ο φάκελος δεν είναι ώριμος για τελική HTA κρίση. Υπάρχουν major red flags/hard stops "
                        "που πρέπει να επιλυθούν πριν από deliberation.")
    elif readiness>=75 and uncertainty_raw<60:
        interpretation=("Υψηλή ωριμότητα φακέλου για πλήρη HTA deliberation. Η τελική κρίση δεν πρέπει να προκύπτει "
                        "μηχανικά από το score, αλλά από comparative benefit, safety, οικονομική επίπτωση, unmet need "
                        "και residual uncertainty.")
    elif readiness>=55:
        interpretation=("Μερικώς ώριμος φάκελος. Απαιτούνται στοχευμένες συμπληρώσεις πριν από τελική κρίση.")
    else:
        interpretation=("Πρώιμο στάδιο HTA readiness με ουσιώδη evidence gaps.")

    return {
        "domain_scores":domain_scores,
        "readiness_score":readiness,
        "uncertainty_raw":uncertainty_raw,
        "uncertainty_label":uncertainty_label,
        "red_flags":red_flags,
        "gaps":gaps,
        "economics":{
            "upfront_fixed":upfront,"annualized_fixed":annualized,
            "device_cost_per_case":device_cost_case,
            "incremental_cost_per_case":delta_cost,"icer":icer
        },
        "budget_impact":{"y1_users":y1_users,"y3_users":y3_users,"year1":y1,"year3":y3},
        "interpretation":interpretation
    }
