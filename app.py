
import streamlit as st
from hta_engine import evaluate_case, DOMAIN_LABELS
from report_generator import build_html_report
from datetime import datetime

st.set_page_config(page_title="MedTech HTA Evaluator", layout="wide")

if "case" not in st.session_state:
    st.session_state.case = {
        "identity": {},
        "regulatory": {},
        "pico": {},
        "clinical": {},
        "safety": {},
        "economic": {},
        "budget": {},
        "organizational": {},
        "ethical": {},
        "rwe": {},
        "review": {}
    }

case = st.session_state.case

st.title("MedTech HTA Evaluator")
st.caption("Decision-support workspace για αξιολόγηση ιατροτεχνολογικών προϊόντων (ΙΤΧ). Δεν αποτελεί επίσημη απόφαση HTA ή κανονιστική έγκριση.")

tabs = st.tabs([
    "1. Ταυτότητα", "2. Regulatory", "3. PICO", "4. Clinical",
    "5. Safety", "6. Economic", "7. Budget Impact",
    "8. Organizational", "9. Ethics / RWE", "10. HTA Summary"
])

with tabs[0]:
    st.subheader("Ταυτότητα τεχνολογίας")
    c1, c2 = st.columns(2)
    with c1:
        case["identity"]["name"] = st.text_input("Εμπορική ονομασία", value=case["identity"].get("name",""))
        case["identity"]["manufacturer"] = st.text_input("Κατασκευαστής", value=case["identity"].get("manufacturer",""))
        case["identity"]["model"] = st.text_input("Μοντέλο / έκδοση", value=case["identity"].get("model",""))
        case["identity"]["device_type"] = st.selectbox("Τύπος", ["Medical Device", "IVD"], index=0)
    with c2:
        case["identity"]["class"] = st.selectbox("Κλάση", ["I","IIa","IIb","III","A","B","C","D","N/A"], index=0)
        case["identity"]["intended_purpose"] = st.text_area("Intended purpose / προβλεπόμενη χρήση", value=case["identity"].get("intended_purpose",""))
        case["identity"]["indication"] = st.text_area("Κλινική ένδειξη", value=case["identity"].get("indication",""))
        case["identity"]["setting"] = st.multiselect("Setting", ["Νοσοκομείο","Εξωνοσοκομειακά","Κατ’ οίκον","Διαγνωστικό κέντρο","Άλλο"], default=case["identity"].get("setting",[]))

with tabs[1]:
    st.subheader("Regulatory readiness")
    c1, c2, c3 = st.columns(3)
    with c1:
        case["regulatory"]["ce"] = st.checkbox("CE διαθέσιμο", value=case["regulatory"].get("ce", False))
        case["regulatory"]["doc"] = st.checkbox("EU Declaration of Conformity", value=case["regulatory"].get("doc", False))
        case["regulatory"]["udi"] = st.checkbox("UDI / Basic UDI-DI", value=case["regulatory"].get("udi", False))
    with c2:
        case["regulatory"]["notified_body"] = st.checkbox("Notified Body όπου απαιτείται", value=case["regulatory"].get("notified_body", False))
        case["regulatory"]["ifu"] = st.checkbox("IFU / επισήμανση", value=case["regulatory"].get("ifu", False))
        case["regulatory"]["cer"] = st.checkbox("Clinical Evaluation Report / Performance Evaluation", value=case["regulatory"].get("cer", False))
    with c3:
        case["regulatory"]["pms"] = st.checkbox("PMS plan/report", value=case["regulatory"].get("pms", False))
        case["regulatory"]["pmcf"] = st.checkbox("PMCF / PMPF όπου απαιτείται", value=case["regulatory"].get("pmcf", False))
        case["regulatory"]["risk"] = st.checkbox("Risk management file", value=case["regulatory"].get("risk", False))

with tabs[2]:
    st.subheader("PICO")
    case["pico"]["population"] = st.text_area("P — Population", value=case["pico"].get("population",""))
    case["pico"]["intervention"] = st.text_area("I — Intervention", value=case["pico"].get("intervention",""))
    case["pico"]["comparator"] = st.text_area("C — Comparator / current standard of care", value=case["pico"].get("comparator",""))
    case["pico"]["outcomes"] = st.text_area("O — Critical / important outcomes", value=case["pico"].get("outcomes",""))
    case["pico"]["fit"] = st.slider("PICO σαφήνεια και relevance", 0, 5, int(case["pico"].get("fit",0)))

with tabs[3]:
    st.subheader("Clinical effectiveness")
    case["clinical"]["study_design"] = st.selectbox("Υψηλότερο επίπεδο συγκριτικής τεκμηρίωσης",
        ["Καμία συγκριτική τεκμηρίωση","Single-arm / case series","Observational comparative","RCT","Systematic review / meta-analysis"])
    case["clinical"]["directness"] = st.slider("Directness ως προς το PICO", 0, 5, int(case["clinical"].get("directness",0)))
    case["clinical"]["consistency"] = st.slider("Consistency αποτελεσμάτων", 0, 5, int(case["clinical"].get("consistency",0)))
    case["clinical"]["precision"] = st.slider("Precision / στατιστική ακρίβεια", 0, 5, int(case["clinical"].get("precision",0)))
    case["clinical"]["effect"] = st.slider("Μέγεθος και κλινική σημασία οφέλους", 0, 5, int(case["clinical"].get("effect",0)))
    case["clinical"]["certainty"] = st.selectbox("Συνολική βεβαιότητα evidence", ["Very low","Low","Moderate","High"])
    case["clinical"]["notes"] = st.text_area("Κύρια αποτελέσματα / παραπομπές", value=case["clinical"].get("notes",""))

with tabs[4]:
    st.subheader("Safety")
    case["safety"]["comparative"] = st.slider("Συγκριτικό προφίλ ασφάλειας", 0, 5, int(case["safety"].get("comparative",0)))
    case["safety"]["vigilance"] = st.slider("Πληρότητα vigilance / PMS δεδομένων", 0, 5, int(case["safety"].get("vigilance",0)))
    case["safety"]["risk_control"] = st.slider("Επαρκής έλεγχος κινδύνων", 0, 5, int(case["safety"].get("risk_control",0)))
    case["safety"]["serious_signal"] = st.checkbox("Υπάρχει σοβαρό unresolved safety signal", value=case["safety"].get("serious_signal",False))
    case["safety"]["notes"] = st.text_area("Safety notes", value=case["safety"].get("notes",""))

with tabs[5]:
    st.subheader("Economic evaluation")
    c1, c2 = st.columns(2)
    with c1:
        case["economic"]["acquisition"] = st.number_input("Τιμή αγοράς (€)", min_value=0.0, value=float(case["economic"].get("acquisition",0)))
        case["economic"]["installation"] = st.number_input("Εγκατάσταση (€)", min_value=0.0, value=float(case["economic"].get("installation",0)))
        case["economic"]["maintenance"] = st.number_input("Ετήσιο maintenance (€)", min_value=0.0, value=float(case["economic"].get("maintenance",0)))
        case["economic"]["training"] = st.number_input("Training (€)", min_value=0.0, value=float(case["economic"].get("training",0)))
    with c2:
        case["economic"]["life_years"] = st.number_input("Ωφέλιμη ζωή (έτη)", min_value=1, max_value=30, value=int(case["economic"].get("life_years",5)))
        case["economic"]["annual_cases"] = st.number_input("Πράξεις / ασθενείς ανά έτος", min_value=1, value=int(case["economic"].get("annual_cases",100)))
        case["economic"]["consumable_new"] = st.number_input("Consumables ανά πράξη – νέο (€)", min_value=0.0, value=float(case["economic"].get("consumable_new",0)))
        case["economic"]["consumable_comp"] = st.number_input("Consumables ανά πράξη – comparator (€)", min_value=0.0, value=float(case["economic"].get("consumable_comp",0)))
    case["economic"]["delta_effect"] = st.number_input("Incremental effect (π.χ. QALY/ασθενή)", value=float(case["economic"].get("delta_effect",0.0)), format="%.4f")
    case["economic"]["other_delta_cost"] = st.number_input("Άλλα incremental costs/savings ανά ασθενή (€)", value=float(case["economic"].get("other_delta_cost",0.0)))
    case["economic"]["model_quality"] = st.slider("Ποιότητα/καταλληλότητα economic model", 0, 5, int(case["economic"].get("model_quality",0)))

with tabs[6]:
    st.subheader("Budget impact")
    case["budget"]["eligible"] = st.number_input("Επιλέξιμος πληθυσμός / έτος", min_value=0, value=int(case["budget"].get("eligible",0)))
    case["budget"]["uptake_y1"] = st.slider("Uptake Year 1 (%)", 0, 100, int(case["budget"].get("uptake_y1",10)))
    case["budget"]["uptake_y3"] = st.slider("Uptake Year 3 (%)", 0, 100, int(case["budget"].get("uptake_y3",30)))
    case["budget"]["net_cost_patient"] = st.number_input("Καθαρή μεταβολή κόστους ανά ασθενή (€)", value=float(case["budget"].get("net_cost_patient",0.0)))
    case["budget"]["quality"] = st.slider("Ποιότητα ελληνικού budget impact model", 0, 5, int(case["budget"].get("quality",0)))

with tabs[7]:
    st.subheader("Organizational impact")
    case["organizational"]["infrastructure"] = st.slider("Εφικτότητα υποδομών", 0, 5, int(case["organizational"].get("infrastructure",0)))
    case["organizational"]["staff"] = st.slider("Εφικτότητα staffing", 0, 5, int(case["organizational"].get("staff",0)))
    case["organizational"]["training"] = st.slider("Εφικτότητα training / learning curve", 0, 5, int(case["organizational"].get("training",0)))
    case["organizational"]["workflow"] = st.slider("Επίδραση στο workflow / care pathway", 0, 5, int(case["organizational"].get("workflow",0)))
    case["organizational"]["scalability"] = st.slider("Scalability / δυνατότητα υιοθέτησης", 0, 5, int(case["organizational"].get("scalability",0)))
    case["organizational"]["notes"] = st.text_area("Organizational notes", value=case["organizational"].get("notes",""))

with tabs[8]:
    st.subheader("Ethical / social / legal + RWE")
    case["ethical"]["equity"] = st.slider("Equity / ισότιμη πρόσβαση", 0, 5, int(case["ethical"].get("equity",0)))
    case["ethical"]["privacy"] = st.slider("Privacy / cybersecurity / GDPR readiness", 0, 5, int(case["ethical"].get("privacy",0)))
    case["ethical"]["acceptability"] = st.slider("Patient / clinician acceptability", 0, 5, int(case["ethical"].get("acceptability",0)))
    case["rwe"]["registry"] = st.checkbox("Υπάρχει/προτείνεται registry", value=case["rwe"].get("registry",False))
    case["rwe"]["conditional"] = st.checkbox("Κατάλληλο για conditional coverage / managed entry", value=case["rwe"].get("conditional",False))
    case["rwe"]["plan_quality"] = st.slider("Ποιότητα RWE plan", 0, 5, int(case["rwe"].get("plan_quality",0)))
    case["rwe"]["notes"] = st.text_area("RWE / managed-entry plan", value=case["rwe"].get("notes",""))

with tabs[9]:
    st.subheader("HTA Summary")
    result = evaluate_case(case)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Evidence readiness", f"{result['readiness_score']:.0f}/100")
    c2.metric("Clinical domain", f"{result['domain_scores']['clinical']:.0f}/100")
    c3.metric("Economic domain", f"{result['domain_scores']['economic']:.0f}/100")
    c4.metric("Uncertainty", result["uncertainty"])

    st.markdown("### Domain profile")
    for k, v in result["domain_scores"].items():
        st.write(f"**{DOMAIN_LABELS[k]}:** {v:.0f}/100")

    if result["red_flags"]:
        st.error("Red flags")
        for x in result["red_flags"]:
            st.write("• " + x)
    else:
        st.success("Δεν εντοπίστηκαν hard-stop red flags με τα τρέχοντα δεδομένα.")

    st.markdown("### Decision-support interpretation")
    st.info(result["interpretation"])

    st.markdown("### Evidence gaps / επόμενες ενέργειες")
    for x in result["gaps"]:
        st.write("• " + x)

    html = build_html_report(case, result)
    st.download_button(
        "Εξαγωγή HTA report σε HTML",
        data=html,
        file_name=f"HTA_{case['identity'].get('name','device')}_{datetime.now().strftime('%Y%m%d')}.html",
        mime="text/html"
    )
