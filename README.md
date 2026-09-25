
# Greek MedTech HTA Workspace v0.3

Η v0.3 είναι guided, user-friendly εφαρμογή για structured MedTech HTA assessment.

## UX
- αρχική οθόνη υποδοχής
- sidebar wizard με βήματα
- επεξήγηση κάθε κρίσιμου πεδίου
- score anchors 0–5
- source traceability σε inputs
- step-by-step formulas
- red flags και evidence gaps
- ενσωματωμένος HTA Advisor

## HTA Advisor
### Χωρίς API key
Λειτουργεί τοπικά με ενσωματωμένη methodological knowledge base.

### Με LLM
Ορίστε:
```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="gpt-5.6-luna"
streamlit run app.py
```
Το API key δεν αποθηκεύεται στον φάκελο της εφαρμογής.

## Export
Η τελική οθόνη δημιουργεί:
- Word (.docx)
- PDF

## Εκτέλεση
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Πρόσβαση από tablet στο ίδιο δίκτυο
```powershell
streamlit run app.py --server.address 0.0.0.0
```
και στο tablet:
`http://IP_ΥΠΟΛΟΓΙΣΤΗ:8501`

## Σημαντικό
Η εφαρμογή δεν είναι κρατικό σύστημα και δεν εκδίδει regulatory approval ή reimbursement decision.
Το HTA readiness score είναι δείκτης πληρότητας/ωριμότητας, όχι πιθανότητα έγκρισης.
