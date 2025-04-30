import streamlit as st
import pdfplumber
import cohere
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO

# Cohere API-configuratie
API_KEY = "9jp4D6PePyb4bSA8C6ZStJb4rPQQh7mehqygg7zs"
co = cohere.Client(API_KEY)

# TRIPOD Checklist (volledige lijst)
TRIPOD_CHECKLIST = [
    # Title and Abstract
    ("Title and abstract", "Title", "Identify the study as developing and/or validating a multivariable prediction model, the target population, and the outcome to be predicted."),
    ("Title and abstract", "Abstract", "Provide a summary of objectives, study design, setting, participants, sample size, predictors, outcome, statistical analysis, results, and conclusions."),
    
    # Introduction
    ("Introduction", "Background and objectives", "Explain the medical context (including whether diagnostic or prognostic) and rationale for developing or validating the multivariable prediction model, including references to existing models."),
    ("Introduction", "Objectives", "Specify the objectives, including whether the study describes the development or validation of the model or both."),
    
    # Methods
    ("Methods", "Source of data", "Describe the study design or source of data (e.g., randomized trial, cohort, or registry data), separately for the development and validation data sets, if applicable."),
    ("Methods", "Key study dates", "Specify the key study dates, including start of accrual; end of accrual; and, if applicable, end of follow-up."),
    ("Methods", "Study setting", "Specify key elements of the study setting (e.g., primary care, secondary care, general population) including number and location of centres."),
    ("Methods", "Eligibility criteria", "Describe eligibility criteria for participants."),
    ("Methods", "Treatments received", "Give details of treatments received, if relevant."),
    ("Methods", "Outcome definition", "Clearly define the outcome that is predicted by the prediction model, including how and when assessed."),
    ("Methods", "Outcome blinding", "Report any actions to blind assessment of the outcome to be predicted."),
    ("Methods", "Predictors", "Clearly define all predictors used in developing or validating the multivariable prediction model, including how and when they were measured."),
    ("Methods", "Predictors blinding", "Report any actions to blind assessment of predictors for the outcome and other predictors."),
    ("Methods", "Sample size", "Explain how the study size was arrived at."),
    ("Methods", "Handling missing data", "Describe how missing data were handled (e.g., complete-case analysis, single imputation, multiple imputation) with details of any imputation method."),
    ("Methods", "Statistical analysis methods", "Describe how predictors were handled in the analyses."),
    ("Methods", "Model type and validation", "Specify type of model, all model-building procedures (including any predictor selection), and method for internal validation."),
    ("Methods", "Model performance measures", "Specify all measures used to assess model performance and, if relevant, to compare multiple models."),
    ("Methods", "Risk groups", "Provide details on how risk groups were created, if done."),
    
    # Results
    ("Results", "Flow of participants", "Describe the flow of participants through the study, including the number of participants with and without the outcome and, if applicable, a summary of the follow-up time. A diagram may be helpful."),
    ("Results", "Participant characteristics", "Describe the characteristics of the participants (basic demographics, clinical features, available predictors), including the number of participants with missing data for predictors and outcome."),
    ("Results", "Number of participants", "Specify the number of participants and outcome events in each analysis."),
    ("Results", "Unadjusted associations", "If done, report the unadjusted association between each candidate predictor and outcome."),
    ("Results", "Full prediction model", "Present the full prediction model to allow predictions for individuals (i.e., all regression coefficients, and model intercept or baseline survival at a given time point)."),
    ("Results", "Model use", "Explain how to use the prediction model."),
    ("Results", "Performance measures", "Report performance measures (with CIs) for the prediction model."),
    
    # Discussion
    ("Discussion", "Limitations", "Discuss any limitations of the study (e.g., nonrepresentative sample, few events per predictor, missing data)."),
    ("Discussion", "Interpretation", "Give an overall interpretation of the results, considering objectives, limitations, and results from similar studies, and other relevant evidence."),
    ("Discussion", "Implications", "Discuss the potential clinical use of the model and implications for future research."),
    
    # Other information
    ("Other information", "Supplementary information", "Provide information about the availability of supplementary resources, such as study protocol, Web calculator, and data sets."),
    ("Other information", "Funding", "Give the source of funding and the role of the funders for the present study.")
]

# Functie: Extract tekst uit PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Functie: Analyseer document volgens TRIPOD-checklist
def analyze_document_with_llm(document_text):
    results = []
    marked_text = document_text
    for section, item, description in TRIPOD_CHECKLIST:
        prompt = f"""
        Analyseer het volgende academische artikel op het volgende TRIPOD-criterium:

        Criterium:
        Sectie: {section}
        Item: {item}
        Beschrijving: {description}

        Artikeltekst:
        {document_text[:5000]}  # Beperk de lengte indien nodig

        Geef een beoordeling: wat is goed, wat ontbreekt, en hoe kan het verbeterd worden?
        """
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=500
        )
        feedback = response.generations[0].text
        results.append({"Section": section, "Item": item, "Feedback": feedback})

        # Markeer relevante tekst
        marked_text = marked_text.replace(
            document_text[:5000], f"***[{section} - {item}]*** {document_text[:5000]}"
        )
    return results, marked_text

# Functie: Genereer PDF-rapport
def generate_pdf_report(results, marked_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Centered', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT, spaceAfter=12))

    elements = []

    # Titelpagina
    elements.append(Paragraph("TRIPOD Evaluation Report", styles['Centered']))
    elements.append(Spacer(1, 20))

    # Feedback per item
    for result in results:
        section = result['Section']
        item = result['Item']
        feedback = result['Feedback']
        elements.append(Paragraph(f"Section: {section}", styles['Heading2']))
        elements.append(Paragraph(f"Item: {item}", styles['Heading3']))
        elements.append(Paragraph(feedback, styles['BodyText']))
        elements.append(Spacer(1, 12))

    # Gemarkeerde tekst
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Marked Article Text", styles['Heading2']))
    elements.append(Paragraph(marked_text, styles['BodyText']))

    # Bouw PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Streamlit-interface
def main():
    st.title("TRIPOD Evaluator voor Academische Artikelen")
    st.write("Upload een academisch artikel (PDF) en ontvang een gedetailleerd rapport volgens de TRIPOD-richtlijnen.")

    # Upload PDF
    uploaded_file = st.file_uploader("Upload een PDF-bestand", type=["pdf"])
    
    if uploaded_file is not None:
        # Tekst extracten
        pdf_text = extract_text_from_pdf(uploaded_file)
        
        st.subheader("Extracted Text")
        st.write(pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text)  # Toon een korte preview
        
        # Analyse starten
        if st.button("Start Analyse"):
            st.write("Analyse bezig... Dit kan enkele minuten duren.")
            results, marked_text = analyze_document_with_llm(pdf_text)

            # Genereer PDF
            pdf_buffer = generate_pdf_report(results, marked_text)

            # Toon downloadknop
            st.download_button(
                label="Download Rapport als PDF",
                data=pdf_buffer,
                file_name="TRIPOD_rapport.pdf",
                mime="application/pdf"
            )

# Voer programma uit
if __name__ == "__main__":
    main()
