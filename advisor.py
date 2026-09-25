
import os, json

LOCAL_KB = {
    "cma": """**CMA – Cost-Minimisation Analysis / Ανάλυση ελαχιστοποίησης κόστους** χρησιμοποιείται μόνο όταν έχει τεκμηριωθεί επαρκώς ότι οι συγκρινόμενες τεχνολογίες έχουν ισοδύναμα κλινικά αποτελέσματα για το σχετικό PICO. Αν υπάρχει διαφορά αποτελεσματικότητας ή σημαντική αβεβαιότητα ως προς ισοδυναμία, προτιμάται CEA/CUA/CCA.""",
    "icer": """**ICER – Incremental Cost-Effectiveness Ratio / Οριακός λόγος κόστους-αποτελεσματικότητας** = ΔCost / ΔEffect. Δεν είναι από μόνο του απόφαση αποζημίωσης. Πρέπει να ερμηνεύεται μαζί με clinical benefit, uncertainty, budget impact και το εφαρμοζόμενο decision framework.""",
    "jca": """**JCA – Joint Clinical Assessment / Κοινή Κλινική Αξιολόγηση** είναι ευρωπαϊκή συγκριτική κλινική αξιολόγηση. Δεν είναι CE certificate και δεν είναι εθνική οικονομική αξιολόγηση. Η εθνική HTA appraisal μπορεί να χρησιμοποιεί την JCA ως clinical evidence base.""",
    "pico": """**PICO** = Population, Intervention, Comparator, Outcomes. Είναι η επιχειρησιακή διατύπωση του decision problem και καθορίζει ποια evidence είναι relevant, ποιο effect estimate είναι αποδεκτό και ποιος comparator πρέπει να χρησιμοποιηθεί στο economic model.""",
    "unmet": """Το **unmet health need** είναι contextual factor. Υψηλή unmet need μπορεί να αυξάνει τη σημασία μιας τεχνολογίας, αλλά δεν αυξάνει μηχανικά το clinical benefit και δεν υποκαθιστά comparative evidence.""",
}

def _local_answer(q, case):
    ql=q.lower()
    for key,ans in LOCAL_KB.items():
        if key in ql:
            return ans
    return """Μπορώ να σε καθοδηγήσω με βάση το συγκεκριμένο HTA βήμα. Γράψε την ερώτηση όσο πιο συγκεκριμένα γίνεται, π.χ. **«τι evidence χρειάζεται για PMCF;»**, **«πώς βαθμολογώ directness;»** ή **«πότε δεν επιτρέπεται CMA;»**.

Αν ενεργοποιηθεί εξωτερικό LLM μέσω API key, ο σύμβουλος μπορεί να απαντά και σε πιο σύνθετες ερωτήσεις χρησιμοποιώντας το περιεχόμενο του τρέχοντος φακέλου ως context."""

def answer_question(question, case):
    api_key=os.getenv("OPENAI_API_KEY","").strip()
    if not api_key:
        return _local_answer(question,case)

    try:
        from openai import OpenAI
        client=OpenAI(api_key=api_key)
        context=json.dumps(case,ensure_ascii=False)[:16000]
        instructions="""You are an HTA methodological advisor embedded in a Greek MedTech HTA workspace.
Answer in Greek. Be precise, educational and non-authoritative. Explain acronyms in English + Greek + practical meaning.
Never invent evidence or legal facts. Distinguish regulatory conformity from HTA appraisal.
Use the current case context only as user-provided information and explicitly flag missing evidence."""
        response=client.responses.create(
            model=os.getenv("OPENAI_MODEL","gpt-5.6-luna"),
            instructions=instructions,
            input=f"CURRENT CASE CONTEXT:\n{context}\n\nUSER QUESTION:\n{question}"
        )
        return response.output_text
    except Exception as e:
        return _local_answer(question,case) + f"\n\n*Το εξωτερικό LLM δεν ήταν διαθέσιμο σε αυτή τη συνεδρία ({type(e).__name__}).*"
