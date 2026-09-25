
import os
import streamlit as st
from datetime import datetime
from hta_engine import evaluate_case, DOMAIN_LABELS
from report_generator import build_docx_bytes, build_pdf_bytes
from advisor import answer_question

st.set_page_config(
    page_title="Greek MedTech HTA Workspace",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- STYLE ----------
st.markdown("""
<style>
.block-container{padding-top:1.25rem;padding-bottom:3rem;}
.hta-card{background:#ffffff;border:1px solid #e5e7eb;border-radius:14px;padding:18px;margin:8px 0 14px 0;box-shadow:0 1px 4px rgba(0,0,0,.04)}
.hta-help{background:#f7fafc;border-left:4px solid #2563eb;padding:12px 14px;border-radius:8px;margin:6px 0 12px 0}
.hta-warn{background:#fff7ed;border-left:4px solid #ea580c;padding:12px 14px;border-radius:8px}
.smallmuted{color:#667085;font-size:.9rem}
.stepok{color:#15803d;font-weight:700}.stepmiss{color:#b45309;font-weight:700}
</style>
""", unsafe_allow_html=True)

STEPS = [
    ("welcome","Αρχική"),
    ("eligibility","Eligibility / JCA"),
    ("identity","Ταυτότητα ΙΤΧ"),
    ("regulatory","Regulatory"),
    ("pico","PICO"),
    ("clinical","Κλινικό όφελος"),
    ("safety","Κλινική ασφάλεια"),
    ("organization","Οργανωτικός αντίκτυπος"),
    ("economic","Οικονομική αξιολόγηση"),
    ("budget","Budget impact"),
    ("social","Κοινωνικός αντίκτυπος"),
    ("legal","Νομικές / ηθικές"),
    ("use_safety","Safety in use"),
    ("unmet","Unmet need"),
    ("uncertainty","Αβεβαιότητα / RWE"),
    ("summary","HTA σύνοψη & αναφορά"),
]

def initial_case():
    return {
        "eligibility": {}, "identity": {}, "regulatory": {}, "pico": {},
        "clinical": {}, "safety": {}, "organizational": {}, "economic": {},
        "budget": {}, "social": {}, "legal_ethical": {}, "use_safety": {},
        "unmet_need": {}, "uncertainty": {}, "rwe": {}, "sources": {}
    }

if "case" not in st.session_state:
    st.session_state.case = initial_case()
if "step" not in st.session_state:
    st.session_state.step = "welcome"
if "advisor_history" not in st.session_state:
    st.session_state.advisor_history = []

case = st.session_state.case

def explainer(title, what, why, input_hint, evidence, effect, example="", error=""):
    with st.expander("💡 Βοήθεια: " + title):
        st.markdown(f"""
**Τι σημαίνει**  
{what}

**Γιατί το ζητάμε**  
{why}

**Τι πρέπει να συμπληρώσεις**  
{input_hint}

**Τεκμηρίωση που πρέπει να υπάρχει**  
{evidence}

**Πώς επηρεάζει την αξιολόγηση**  
{effect}
""")
        if example:
            st.markdown(f"**Παράδειγμα**  \n{example}")
        if error:
            st.markdown(f"**Συχνό λάθος**  \n{error}")

def score_help(title, anchors):
    with st.expander("📏 Πώς βαθμολογείται: " + title):
        for n,txt in anchors:
            st.markdown(f"**{n}** — {txt}")

def source_box(key):
    st.markdown("<div class='smallmuted'>Πηγή / παραπομπή του συγκεκριμένου input</div>", unsafe_allow_html=True)
    case["sources"][key] = st.text_input(
        "Source", value=case["sources"].get(key,""),
        key="src_"+key, label_visibility="collapsed",
        placeholder="π.χ. JCA report p. 42 / DOI / CER §7.3 / manufacturer submission"
    )

def metric_input(key, label, help_title, help_text):
    case.setdefault("metrics",{})
    val = st.number_input(label, value=float(case["metrics"].get(key,0.0)), key="m_"+key)
    case["metrics"][key] = val
    with st.expander("ℹ️ "+help_title):
        st.markdown(help_text)
    return val

def nav_buttons(prev_key=None,next_key=None):
    c1,c2,c3 = st.columns([1,4,1])
    with c1:
        if prev_key and st.button("← Πίσω", use_container_width=True):
            st.session_state.step=prev_key
            st.rerun()
    with c3:
        if next_key and st.button("Συνέχεια →", type="primary", use_container_width=True):
            st.session_state.step=next_key
            st.rerun()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🩺 Greek MedTech HTA")
    st.caption("Guided Regulatory & HTA Workspace")
    result_sidebar = evaluate_case(case)
    st.progress(min(100,max(0,int(result_sidebar["readiness_score"])))/100)
    st.caption(f"Ετοιμότητα φακέλου: {result_sidebar['readiness_score']:.0f}%")
    st.markdown("---")
    step_labels = {k:v for k,v in STEPS}
    selected = st.radio(
        "Βήματα αξιολόγησης",
        options=[k for k,_ in STEPS],
        format_func=lambda x: step_labels[x],
        index=[k for k,_ in STEPS].index(st.session_state.step)
    )
    if selected != st.session_state.step:
        st.session_state.step = selected
        st.rerun()
    st.markdown("---")
    st.markdown("### 🤖 HTA Advisor")
    st.caption("Ρώτησε τι σημαίνει ένα πεδίο, ποια στοιχεία χρειάζονται ή πώς ερμηνεύεται ένας δείκτης.")
    q = st.text_input("Ερώτηση", placeholder="π.χ. Πότε επιτρέπεται CMA;", key="advisor_q")
    if st.button("Ρώτησε τον σύμβουλο", use_container_width=True) and q.strip():
        ans = answer_question(q, case)
        st.session_state.advisor_history.append((q,ans))
    if st.session_state.advisor_history:
        q0,a0 = st.session_state.advisor_history[-1]
        with st.expander("Τελευταία απάντηση", expanded=True):
            st.markdown(a0)
    st.caption("Ο σύμβουλος υποστηρίζει την αξιολόγηση· δεν αντικαθιστά reviewer ή επίσημη κανονιστική κρίση.")

step = st.session_state.step

# ---------- WELCOME ----------
if step == "welcome":
    st.title("Greek MedTech HTA Workspace")
    st.subheader("Από τον φάκελο του ΙΤΧ έως την τεκμηριωμένη HTA αναφορά")
    st.markdown("""
Η εφαρμογή σε καθοδηγεί βήμα-βήμα. Δεν χρειάζεται να γνωρίζεις εξαρχής όλη τη μεθοδολογία:
κάθε επιλογή έχει ενσωματωμένη βοήθεια, παραδείγματα, απαιτούμενη τεκμηρίωση και επεξήγηση
του τρόπου με τον οποίο επηρεάζει το assessment.
""")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("<div class='hta-card'><h4>1. Καταχώριση</h4><p>Ταυτότητα, CE, JCA, PICO και πηγές.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='hta-card'><h4>2. Αξιολόγηση</h4><p>Κλινικά, οικονομικά, οργανωτικά, κοινωνικά και safety domains.</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='hta-card'><h4>3. Αναφορά</h4><p>QC, red flags, τεκμηριωμένη σύνοψη και export σε Word/PDF.</p></div>", unsafe_allow_html=True)
    st.info("Στόχος: κάθε συμπέρασμα να είναι αναπαραγώγιμο από δεύτερο αξιολογητή.")
    nav_buttons(None,"eligibility")

# ---------- ELIGIBILITY ----------
elif step == "eligibility":
    st.title("0. Eligibility / JCA")
    st.write("Πρώτα ελέγχουμε αν και πώς εντάσσεται το ΙΤΧ στην ευρωπαϊκή/εθνική διαδρομή HTA.")
    case["eligibility"]["jca_available"] = st.checkbox(
        "Υπάρχει δημοσιευμένη Joint Clinical Assessment (JCA);",
        value=case["eligibility"].get("jca_available",False)
    )
    explainer(
        "Joint Clinical Assessment (JCA)",
        "Κοινή ευρωπαϊκή κλινική αξιολόγηση σχετικής αποτελεσματικότητας και ασφάλειας.",
        "Η εθνική αξιολόγηση μπορεί να αξιοποιεί την JCA αντί να επαναλαμβάνει το ίδιο κλινικό έργο.",
        "Επίλεξε ΝΑΙ μόνο αν έχεις ταυτοποιήσει δημοσιευμένη JCA για το συγκεκριμένο device/indication.",
        "JCA report, scope, publication date, identifier.",
        "Επηρεάζει το eligibility και το clinical evidence mapping.",
        "JCA report με ίδιο ακριβώς device και indication.",
        "CE certificate ή opinion expert panel δεν είναι JCA."
    )
    case["eligibility"]["jca_ref"] = st.text_input("JCA reference / URL / identifier", value=case["eligibility"].get("jca_ref",""))
    source_box("jca")
    case["eligibility"]["national_pathway"] = st.selectbox(
        "Στόχος φακέλου",
        ["Προετοιμασία HTA φακέλου","Αποζημίωση","Νοσοκομειακή προμήθεια","Εσωτερική αξιολόγηση","Άλλο"],
        index=0
    )
    explainer(
        "Στόχος φακέλου",
        "Το decision context για το οποίο αξιολογείται η τεχνολογία.",
        "Ο comparator, το perspective και το budget model εξαρτώνται από το ποιος αποφασίζει και για ποιο σκοπό.",
        "Επίλεξε τον πραγματικό σκοπό του φακέλου.",
        "Αίτημα/εντολή αξιολόγησης ή documented use case.",
        "Καθορίζει τα επόμενα modules και την τελική αναφορά."
    )
    nav_buttons("welcome","identity")

# ---------- IDENTITY ----------
elif step == "identity":
    st.title("1. Ταυτότητα Ιατροτεχνολογικού")
    c1,c2 = st.columns(2)
    with c1:
        case["identity"]["name"]=st.text_input("Εμπορική ονομασία", value=case["identity"].get("name",""))
        case["identity"]["manufacturer"]=st.text_input("Κατασκευαστής", value=case["identity"].get("manufacturer",""))
        case["identity"]["model"]=st.text_input("Μοντέλο / έκδοση", value=case["identity"].get("model",""))
        case["identity"]["device_type"]=st.selectbox("Τύπος",["Medical Device","IVD"],index=0)
    with c2:
        case["identity"]["class"]=st.selectbox("Κλάση",["I","IIa","IIb","III","A","B","C","D","N/A"],index=0)
        case["identity"]["intended_purpose"]=st.text_area("Intended purpose", value=case["identity"].get("intended_purpose",""))
        case["identity"]["indication"]=st.text_area("Ένδειξη", value=case["identity"].get("indication",""))
        case["identity"]["setting"]=st.multiselect("Setting",["Νοσοκομείο","Εξωνοσοκομειακά","Κατ’ οίκον","Διαγνωστικό κέντρο","Άλλο"],default=case["identity"].get("setting",[]))
    explainer(
        "Intended purpose",
        "Η χρήση που ορίζει ο κατασκευαστής για τη συγκεκριμένη έκδοση του ΙΤΧ.",
        "Είναι ο πυρήνας για classification, CE scope και μεταφερσιμότητα evidence.",
        "Αντέγραψε την ακριβή διατύπωση από IFU/DoC και πρόσθεσε πηγή.",
        "IFU, Declaration of Conformity, CER/PER.",
        "Ασυμφωνία intended purpose και HTA indication δημιουργεί red flag."
    )
    source_box("identity")
    nav_buttons("eligibility","regulatory")

# ---------- REGULATORY ----------
elif step == "regulatory":
    st.title("2. Regulatory Readiness")
    items = [
        ("ce","CE marking","Τεκμηριώνει ότι το προϊόν φέρει σήμανση CE στο σχετικό regulatory πλαίσιο."),
        ("doc","EU Declaration of Conformity","Δήλωση συμμόρφωσης του κατασκευαστή για το συγκεκριμένο προϊόν/έκδοση."),
        ("udi","UDI / Basic UDI-DI","Μοναδική ταυτοποίηση για traceability."),
        ("notified_body","Notified Body documentation","Πιστοποιητικό κοινοποιημένου οργανισμού όπου απαιτείται."),
        ("ifu","IFU / Labeling","Επίσημες οδηγίες χρήσης, warnings, contraindications."),
        ("cer","CER / Performance Evaluation","Κλινική ή performance αξιολόγηση regulatory dossier."),
        ("pms","PMS / PSUR","Post-market surveillance και περιοδικά safety δεδομένα."),
        ("pmcf","PMCF / PMPF","Μετεμπορική κλινική/performance παρακολούθηση."),
        ("risk","Risk Management File","Hazards, controls και residual risks.")
    ]
    for key,label,desc in items:
        c1,c2 = st.columns([1,2])
        with c1:
            case["regulatory"][key]=st.checkbox(label,value=case["regulatory"].get(key,False))
        with c2:
            st.caption(desc)
            source_box("reg_"+key)
    explainer(
        "Regulatory completeness",
        "Έλεγχος πληρότητας των βασικών regulatory τεκμηρίων.",
        "Το HTA δεν αντικαθιστά το CE conformity assessment, αλλά πρέπει να ξέρει ακριβώς ποιο προϊόν και ποια έκδοση αξιολογεί.",
        "Σημείωσε μόνο όσα έχεις πραγματικά επαληθεύσει.",
        "Έγγραφα manufacturer/Notified Body/EUDAMED όπου εφαρμόζεται.",
        "Μη επαληθευμένα ή ληγμένα στοιχεία παραμένουν gap και μπορεί να μπλοκάρουν την αξιολόγηση.",
        error="Το 'έχει CE' δεν αρκεί χωρίς αντιστοίχιση σε model/version/indication."
    )
    nav_buttons("identity","pico")

# ---------- PICO ----------
elif step == "pico":
    st.title("3. PICO / Decision Problem")
    for key,label,what in [
        ("population","P — Population","Ποιοι ακριβώς ασθενείς ή χρήστες αφορά η αξιολόγηση."),
        ("intervention","I — Intervention","Το ακριβές device, version, procedure και συνοδευτική χρήση."),
        ("comparator","C — Comparator","Το πραγματικό standard of care ή εναλλακτική στο ελληνικό setting."),
        ("outcomes","O — Outcomes","Patient-relevant και resource outcomes που κρίνουν την αξία.")
    ]:
        case["pico"][key]=st.text_area(label,value=case["pico"].get(key,""))
        explainer(label,what,"Χωρίς σαφές PICO δεν υπάρχει συγκρίσιμη HTA ερώτηση.",
                  "Γράψε συγκεκριμένα inclusion/exclusion, version, comparator και outcome hierarchy.",
                  "JCA scope, guidelines, Greek practice, clinical studies.",
                  "Το PICO οδηγεί evidence selection, effect estimates και economic model.")
        source_box("pico_"+key)
    case["pico"]["fit"]=st.slider("Σαφήνεια / relevance PICO",0,5,int(case["pico"].get("fit",0)))
    score_help("PICO",[(0,"Δεν υπάρχει λειτουργικό PICO."),(1,"Πολύ ασαφές."),
                       (2,"Υπάρχουν βασικά στοιχεία αλλά σοβαρά κενά."),
                       (3,"Επαρκές για αρχική αξιολόγηση."),
                       (4,"Σαφές, τεκμηριωμένο και συμβατό με το decision problem."),
                       (5,"Πλήρως operationalized με υποομάδες, comparator justification και outcome hierarchy.")])
    nav_buttons("regulatory","clinical")

# ---------- CLINICAL ----------
elif step == "clinical":
    st.title("4. Κλινικό όφελος")
    case["clinical"]["study_design"]=st.selectbox(
        "Υψηλότερο διαθέσιμο συγκριτικό design",
        ["Καμία συγκριτική τεκμηρίωση","Single-arm / case series","Observational comparative","RCT","Systematic review / meta-analysis"]
    )
    explainer("Study design","Τύπος μελέτης που στηρίζει το comparative effect.",
              "Η ιεραρχία design βοηθά, αλλά η ποιότητα και directness είναι εξίσου κρίσιμες.",
              "Επίλεξε το υψηλότερο πραγματικά σχετικό evidence για το συγκεκριμένο PICO.",
              "Publications, protocols, registries, JCA evidence tables.",
              "Επηρεάζει certainty, όχι μηχανικά την τελική κρίση.")
    dims=[("directness","Directness"),("consistency","Consistency"),
          ("precision","Precision"),("effect","Κλινική σημασία αποτελέσματος")]
    for key,label in dims:
        case["clinical"][key]=st.slider(label,0,5,int(case["clinical"].get(key,0)),key="cl_"+key)
        source_box("cl_"+key)
    score_help("Clinical evidence",[
        (0,"Απουσία ή μη αξιολογήσιμη τεκμηρίωση."),
        (1,"Πολύ αδύναμη, έμμεση ή σοβαρά προβληματική."),
        (2,"Χαμηλή, με σημαντικές αβεβαιότητες."),
        (3,"Επαρκής για βασικό συμπέρασμα, αλλά όχι χωρίς σημαντικούς περιορισμούς."),
        (4,"Ισχυρή και άμεσα σχετική, με μικρές αβεβαιότητες."),
        (5,"Πολύ ισχυρή, συνεπής, ακριβής και κλινικά ουσιαστική.")
    ])
    case["clinical"]["certainty"]=st.selectbox("Συνολική certainty of evidence",["Very low","Low","Moderate","High"])
    case["clinical"]["notes"]=st.text_area("Κλινική αιτιολόγηση / κύρια αποτελέσματα",value=case["clinical"].get("notes",""))
    nav_buttons("pico","safety")

# ---------- SAFETY ----------
elif step == "safety":
    st.title("5. Κλινική ασφάλεια")
    for key,label in [("comparative","Comparative safety"),("vigilance","Vigilance / PMS completeness"),("risk_control","Residual risk control")]:
        case["safety"][key]=st.slider(label,0,5,int(case["safety"].get(key,0)))
        source_box("saf_"+key)
    case["safety"]["serious_signal"]=st.checkbox("Υπάρχει unresolved serious safety signal",value=case["safety"].get("serious_signal",False))
    explainer("Clinical Safety","Ανεπιθύμητες κλινικές εκβάσεις και device/procedure-related harm.",
              "Η ασφάλεια πρέπει να συγκρίνεται με τον comparator και να λαμβάνει υπόψη vigilance.",
              "Κατέγραψε frequency, severity, causality και unresolved signals.",
              "Trials, registries, PMS/PSUR, recalls, FSCA.",
              "Σοβαρό unresolved signal μπορεί να λειτουργήσει ως hard stop.",
              error="Μην συγχέεις clinical adverse events με human-factor/operator-error risk.")
    case["safety"]["notes"]=st.text_area("Safety rationale",value=case["safety"].get("notes",""))
    nav_buttons("clinical","organization")

# ---------- ORGANIZATION ----------
elif step == "organization":
    st.title("6. Οργανωτικός αντίκτυπος")
    fields=[("infrastructure","Υποδομές"),("staff","Staffing"),("training","Training / learning curve"),
            ("workflow","Workflow / care pathway"),("scalability","Scalability")]
    for key,label in fields:
        case["organizational"][key]=st.slider(label,0,5,int(case["organizational"].get(key,0)))
        source_box("org_"+key)
    score_help("Organizational impact",[
        (0,"Μη εφαρμόσιμο ή δεν υπάρχει τεκμηρίωση."),
        (1,"Πολύ μεγάλες απαιτήσεις/εμπόδια."),
        (2,"Σημαντικές απαιτήσεις με χαμηλή ετοιμότητα."),
        (3,"Διαχειρίσιμες απαιτήσεις."),
        (4,"Καλή συμβατότητα με υπάρχουσα υποδομή και workflow."),
        (5,"Σαφής οργανωτική βελτίωση/υψηλή δυνατότητα εφαρμογής.")
    ])
    case["organizational"]["notes"]=st.text_area("Organizational rationale",value=case["organizational"].get("notes",""))
    nav_buttons("safety","economic")

# ---------- ECONOMIC ----------
elif step == "economic":
    st.title("7. Οικονομική αξιολόγηση")
    case["economic"]["analysis_type"]=st.selectbox(
        "Μέθοδος",
        ["CEA – Cost-Effectiveness Analysis","CUA – Cost-Utility Analysis","CMA – Cost-Minimisation Analysis","CCA – Cost-Consequence Analysis"]
    )
    explainer(
        "CEA / CUA / CMA / CCA",
        "CEA: κόστος ανά φυσική μονάδα αποτελέσματος. CUA: κόστος ανά QALY. CMA: μόνο με τεκμηριωμένη ισοδυναμία. CCA: κόστη και outcomes χωριστά.",
        "Η μέθοδος πρέπει να ταιριάζει στο clinical evidence και στο decision problem.",
        "Επίλεξε μέθοδο και τεκμηρίωσε γιατί είναι η κατάλληλη.",
        "Clinical equivalence/superiority evidence, utilities, cost inputs, modelling plan.",
        "Καθορίζει ποιο economic output είναι έγκυρο.",
        error="CMA χωρίς αποδεδειγμένη clinical equivalence είναι μεθοδολογικά ακατάλληλη."
    )
    c1,c2=st.columns(2)
    with c1:
        case["economic"]["acquisition"]=st.number_input("Acquisition (€)",min_value=0.0,value=float(case["economic"].get("acquisition",0)))
        source_box("eco_acq")
        case["economic"]["installation"]=st.number_input("Installation (€)",min_value=0.0,value=float(case["economic"].get("installation",0)))
        source_box("eco_inst")
        case["economic"]["training"]=st.number_input("Training (€)",min_value=0.0,value=float(case["economic"].get("training",0)))
        source_box("eco_train")
        case["economic"]["maintenance"]=st.number_input("Annual maintenance (€)",min_value=0.0,value=float(case["economic"].get("maintenance",0)))
        source_box("eco_maint")
    with c2:
        case["economic"]["life_years"]=st.number_input("Useful life (years)",min_value=1,max_value=30,value=int(case["economic"].get("life_years",5)))
        source_box("eco_life")
        case["economic"]["annual_cases"]=st.number_input("Annual cases",min_value=1,value=int(case["economic"].get("annual_cases",100)))
        source_box("eco_cases")
        case["economic"]["consumable_new"]=st.number_input("Consumables / case – new (€)",min_value=0.0,value=float(case["economic"].get("consumable_new",0)))
        source_box("eco_con_new")
        case["economic"]["consumable_comp"]=st.number_input("Consumables / case – comparator (€)",min_value=0.0,value=float(case["economic"].get("consumable_comp",0)))
        source_box("eco_con_comp")
    case["economic"]["other_delta_cost"]=st.number_input("Other incremental costs/savings per patient (€)",value=float(case["economic"].get("other_delta_cost",0.0)))
    source_box("eco_delta_cost")
    case["economic"]["delta_effect"]=st.number_input("Incremental effect (e.g. QALY/patient)",value=float(case["economic"].get("delta_effect",0.0)),format="%.4f")
    source_box("eco_delta_effect")
    case["economic"]["model_quality"]=st.slider("Economic model quality",0,5,int(case["economic"].get("model_quality",0)))

    r=evaluate_case(case)
    e=r["economics"]
    st.markdown("### 🧮 Υπολογισμός βήμα-βήμα")
    st.code(
f"""Upfront fixed cost = Acquisition + Installation + Training
= {case["economic"]["acquisition"]:.2f} + {case["economic"]["installation"]:.2f} + {case["economic"]["training"]:.2f}
= {e["upfront_fixed"]:.2f} €

Annualized fixed cost = Upfront fixed cost / Useful life + Maintenance
= {e["upfront_fixed"]:.2f} / {case["economic"]["life_years"]} + {case["economic"]["maintenance"]:.2f}
= {e["annualized_fixed"]:.2f} € / year

Device cost per case = Annualized fixed cost / Annual cases + Consumables
= {e["annualized_fixed"]:.2f} / {case["economic"]["annual_cases"]} + {case["economic"]["consumable_new"]:.2f}
= {e["device_cost_per_case"]:.2f} € / case

Incremental cost = Device cost/case - Comparator variable cost + Other Δcost
= {e["device_cost_per_case"]:.2f} - {case["economic"]["consumable_comp"]:.2f} + {case["economic"]["other_delta_cost"]:.2f}
= {e["incremental_cost_per_case"]:.2f} € / case"""
    )
    if e["icer"] is None:
        st.warning("ICER δεν ορίζεται επειδή ΔEffect = 0. Ελέγξτε αν λείπει effect estimate ή αν η κατάλληλη μέθοδος είναι CMA/CCA.")
    else:
        st.code(f"ICER = ΔCost / ΔEffect = {e['incremental_cost_per_case']:.2f} / {case['economic']['delta_effect']:.4f} = {e['icer']:.2f} € ανά μονάδα αποτελέσματος")
    nav_buttons("organization","budget")

# ---------- BUDGET ----------
elif step == "budget":
    st.title("8. Budget Impact")
    case["budget"]["eligible"]=st.number_input("Eligible population / year",min_value=0,value=int(case["budget"].get("eligible",0)))
    source_box("bia_eligible")
    case["budget"]["uptake_y1"]=st.slider("Uptake Year 1 (%)",0,100,int(case["budget"].get("uptake_y1",10)))
    case["budget"]["uptake_y3"]=st.slider("Uptake Year 3 (%)",0,100,int(case["budget"].get("uptake_y3",30)))
    case["budget"]["net_cost_patient"]=st.number_input("Net incremental cost / patient (€)",value=float(case["budget"].get("net_cost_patient",0.0)))
    source_box("bia_net")
    case["budget"]["quality"]=st.slider("Greek BIA model quality",0,5,int(case["budget"].get("quality",0)))
    r=evaluate_case(case); b=r["budget_impact"]
    st.markdown("### 🧮 Υπολογισμός")
    st.code(f"""Treated Y1 = Eligible × Uptake Y1
= {case["budget"]["eligible"]} × {case["budget"]["uptake_y1"]}% = {b["y1_users"]:.1f}

Budget Impact Y1 = Treated Y1 × Net incremental cost
= {b["y1_users"]:.1f} × {case["budget"]["net_cost_patient"]:.2f}
= {b["year1"]:.2f} €

Treated Y3 = {case["budget"]["eligible"]} × {case["budget"]["uptake_y3"]}% = {b["y3_users"]:.1f}
Budget Impact Y3 = {b["year3"]:.2f} €""")
    explainer("Net incremental cost","Το καθαρό επιπλέον κόστος ανά ασθενή μετά από αποφεύγόμενα κόστη/savings.",
              "Το budget impact δεν είναι απλώς τιμή συσκευής × ασθενείς.",
              "Συμπερίλαβε relevant downstream costs και savings.",
              "Greek tariffs, procurement, DRGs, resource-use studies.",
              "Ορίζει την πραγματική πίεση στον προϋπολογισμό.")
    nav_buttons("economic","social")

# ---------- SOCIAL ----------
elif step == "social":
    st.title("9. Κοινωνικός αντίκτυπος")
    for key,label in [("equity","Ισότητα πρόσβασης"),("patient_burden","Burden ασθενούς/φροντιστή"),
                      ("geographic","Γεωγραφικές ανισότητες"),("acceptability","Αποδοχή από ασθενείς/χρήστες")]:
        case["social"][key]=st.slider(label,0,5,int(case["social"].get(key,0)))
        source_box("soc_"+key)
    explainer("Social impact","Επίδραση στην πρόσβαση, μετακίνηση, caregiver burden, κοινωνικές/γεωγραφικές ανισότητες.",
              "Η αξία μιας τεχνολογίας δεν εξαντλείται σε clinical endpoints και κόστος.",
              "Χρησιμοποίησε patient-reported evidence, access data ή τεκμηριωμένη qualitative analysis.",
              "PROs, surveys, Greek access data, patient organisations, service data.",
              "Μπορεί να αναδείξει σημαντικό όφελος ή εμπόδιο εφαρμογής.")
    case["social"]["notes"]=st.text_area("Social rationale",value=case["social"].get("notes",""))
    nav_buttons("budget","legal")

# ---------- LEGAL ----------
elif step == "legal":
    st.title("10. Νομικές & ηθικές πτυχές")
    for key,label in [("privacy","GDPR / privacy"),("cybersecurity","Cybersecurity governance"),
                      ("consent","Informed consent"),("liability","Liability / accountability"),
                      ("fairness","Fairness / non-discrimination")]:
        case["legal_ethical"][key]=st.slider(label,0,5,int(case["legal_ethical"].get(key,0)))
        source_box("leg_"+key)
    explainer("Legal / Ethical","Νομιμότητα, προστασία δεδομένων, accountability, fairness και consent.",
              "Ιδίως software/AI devices μπορεί να έχουν risks που δεν αποτυπώνονται σε clinical trials.",
              "Κατέγραψε συγκεκριμένες νομικές/ηθικές απαιτήσεις και mitigation.",
              "DPIA, cybersecurity file, contracts, consent forms, governance policies.",
              "Unresolved legal/ethical issues μπορεί να απαιτούν conditions ή να εμποδίζουν εφαρμογή.")
    case["legal_ethical"]["notes"]=st.text_area("Legal / ethical rationale",value=case["legal_ethical"].get("notes",""))
    nav_buttons("social","use_safety")

# ---------- USE SAFETY ----------
elif step == "use_safety":
    st.title("11. Safety in Use / Human Factors")
    for key,label in [("usability","Usability"),("operator_error","Prevention of operator error"),
                      ("training","Training adequacy"),("alarms","Alarms / fail-safe"),
                      ("maintenance","Maintenance / calibration safety")]:
        case["use_safety"][key]=st.slider(label,0,5,int(case["use_safety"].get(key,0)))
        source_box("use_"+key)
    case["use_safety"]["critical_use_risk"]=st.checkbox(
        "Κρίσιμος κίνδυνος λανθασμένης χρήσης χωρίς επαρκές mitigation",
        value=case["use_safety"].get("critical_use_risk",False)
    )
    explainer("Safety in use","Κίνδυνος που προκύπτει από interface, χειρισμό, workflow, training ή maintenance.",
              "Μια τεχνολογία μπορεί να έχει καλό clinical safety profile αλλά κακή operational safety.",
              "Αξιολόγησε human factors/usability evidence και πραγματικές απαιτήσεις εκπαίδευσης.",
              "Usability engineering, simulated-use studies, complaint/CAPA data.",
              "Κρίσιμο unresolved use-risk είναι major red flag.")
    nav_buttons("legal","unmet")

# ---------- UNMET ----------
elif step == "unmet":
    st.title("12. Unmet Health Need")
    for key,label in [("alternatives","Έλλειψη αποτελεσματικών εναλλακτικών"),("severity","Severity"),
                      ("burden","Disease / system burden"),("subgroup","Unmet need συγκεκριμένης υποομάδας")]:
        case["unmet_need"][key]=st.slider(label,0,5,int(case["unmet_need"].get(key,0)))
        source_box("unmet_"+key)
    st.info("Υψηλό unmet need δεν αποδεικνύει αποτελεσματικότητα. Είναι contextual factor, όχι υποκατάστατο comparative evidence.")
    case["unmet_need"]["notes"]=st.text_area("Unmet-need rationale",value=case["unmet_need"].get("notes",""))
    nav_buttons("use_safety","uncertainty")

# ---------- UNCERTAINTY ----------
elif step == "uncertainty":
    st.title("13. Αβεβαιότητα & RWE")
    for key,label in [("clinical","Clinical uncertainty"),("economic","Economic uncertainty"),
                      ("implementation","Implementation uncertainty"),("long_term","Long-term uncertainty")]:
        case["uncertainty"][key]=st.slider(label,0,5,int(case["uncertainty"].get(key,0)))
        source_box("unc_"+key)
    st.warning("Στο uncertainty domain: 5 = πολύ υψηλή αβεβαιότητα.")
    case["rwe"]["registry"]=st.checkbox("Υπάρχει/προτείνεται registry",value=case["rwe"].get("registry",False))
    case["rwe"]["conditional"]=st.checkbox("Κατάλληλο για conditional coverage / managed entry",value=case["rwe"].get("conditional",False))
    case["rwe"]["plan_quality"]=st.slider("RWE plan quality",0,5,int(case["rwe"].get("plan_quality",0)))
    explainer("Conditional coverage","Πρόσβαση υπό όρους με δεσμευτική συλλογή πρόσθετων δεδομένων.",
              "Χρησιμοποιείται όταν μια κρίσιμη αβεβαιότητα μπορεί ρεαλιστικά να μειωθεί μετά την εφαρμογή.",
              "Όρισε research question, endpoints, registry, timeline και reassessment rule.",
              "Protocol, registry plan, governance, data-quality plan.",
              "Δεν πρέπει να λειτουργεί ως τρόπος παράκαμψης ανεπαρκούς πιθανότητας κλινικού οφέλους.")
    nav_buttons("unmet","summary")

# ---------- SUMMARY ----------
elif step == "summary":
    st.title("14. HTA Σύνοψη & Αναφορά")
    result=evaluate_case(case)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Readiness",f"{result['readiness_score']:.0f}/100")
    c2.metric("Clinical",f"{result['domain_scores']['clinical']:.0f}/100")
    c3.metric("Economic",f"{result['domain_scores']['economic']:.0f}/100")
    c4.metric("Uncertainty",result["uncertainty_label"])

    st.markdown("### Έλεγχος domains")
    for k,v in result["domain_scores"].items():
        st.write(f"**{DOMAIN_LABELS[k]}** — {v:.0f}/100")

    if result["red_flags"]:
        st.error("Red flags / hard stops")
        for x in result["red_flags"]:
            st.write("• "+x)
    else:
        st.success("Δεν εντοπίστηκαν hard-stop red flags με τα τρέχοντα inputs.")

    st.markdown("### Evidence gaps / επόμενες ενέργειες")
    for x in result["gaps"]:
        st.write("• "+x)

    st.markdown("### HTA interpretation")
    st.info(result["interpretation"])

    st.markdown("### 📄 Τελική αναφορά")
    st.caption("Η αναφορά περιλαμβάνει τα δεδομένα, τις πηγές, τους υπολογισμούς, τα red flags, τις αβεβαιότητες και το rationale.")
    docx_bytes = build_docx_bytes(case,result)
    pdf_bytes = build_pdf_bytes(case,result)
    c1,c2=st.columns(2)
    with c1:
        st.download_button(
            "⬇️ Εξαγωγή σε Word (.docx)",
            data=docx_bytes,
            file_name=f"MedTech_HTA_{case['identity'].get('name','device')}_{datetime.now().strftime('%Y%m%d')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    with c2:
        st.download_button(
            "⬇️ Εξαγωγή σε PDF",
            data=pdf_bytes,
            file_name=f"MedTech_HTA_{case['identity'].get('name','device')}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    nav_buttons("uncertainty",None)
