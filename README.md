
# MedTech HTA Evaluator v0.1

Πρωτότυπο web εφαρμογής για δομημένη αξιολόγηση ιατροτεχνολογικών προϊόντων ως HTA.

## Τι κάνει
- Ταυτότητα τεχνολογίας
- Regulatory readiness
- PICO
- Clinical effectiveness
- Safety
- Economic evaluation
- Budget impact
- Organizational impact
- Ethical/social/legal + RWE
- Red flags / evidence gaps
- HTA summary
- HTML report export

## Εκτέλεση
1. Εγκατάσταση Python 3.11+
2. Άνοιξε PowerShell μέσα στον φάκελο
3. Τρέξε:
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run app.py

Στη συνέχεια ανοίγει στον browser.

## Πρόσβαση από tablet στο ίδιο Wi‑Fi
Τρέξε:
streamlit run app.py --server.address 0.0.0.0

και από το tablet άνοιξε:
http://IP_ΤΟΥ_ΥΠΟΛΟΓΙΣΤΗ:8501

## Σημαντική μεθοδολογική αρχή
Το readiness score ΔΕΝ αποτελεί σύσταση αποζημίωσης.
Η εφαρμογή διατηρεί χωριστά:
- evidence
- uncertainty
- red flags
- οικονομικές επιπτώσεις
- αξιολογική κρίση

Στην επόμενη έκδοση πρέπει να προστεθούν:
- βιβλιογραφία και citations ανά claim
- GRADE / risk-of-bias
- SLR module
- sensitivity / scenario analysis
- probabilistic sensitivity analysis
- comparator matrix
- multi-PICO
- versioning / audit log
- user roles
- database
- PDF/DOCX HTA dossier export
- ελληνικό HTA / EU JCA mapping
