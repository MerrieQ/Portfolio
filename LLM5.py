
import streamlit as st
import pdfplumber
import cohere
import fitz  # PyMuPDF
from io import BytesIO
import tempfile

# Cohere API-configuratie
API_KEY = "9jp4D6PePyb4bSA8C6ZStJb4rPQQh7mehqygg7zs"
co = cohere.Client(API_KEY)

# Volledige TRIPOD-checklist
TRIPOD_CHECKLIST = [
    # Title and Abstract
    ("1", "1.1", "Title and abstract", "Title", "Identify the study as developing and/or validating a multivariable prediction model, the target population, and the outcome to be predicted."),
    ("1", "1.2", "Title and abstract", "Abstract", "Provide a summary of objectives, study design, setting, participants, sample size, predictors, outcome, statistical analysis, results, and conclusions."),
    
    # Introduction
    ("2", "2.1", "Introduction", "Background and objectives", "Explain the medical context (including whether diagnostic or prognostic) and rationale for developing or validating the multivariable prediction model, including references to existing models."),
    ("2", "2.2", "Introduction", "Objectives", "Specify the objectives, including whether the study describes the development or validation of the model or both."),
    
    # Methods
    ("3", "3.1", "Methods", "Source of data", "Describe the study design or source of data (e.g., randomized trial, cohort, or registry data), separately for the development and validation data sets, if applicable."),
    ("3", "3.2", "Methods", "Key study dates", "Specify the key study dates, including start of accrual; end of accrual; and, if applicable, end of follow-up."),
    ("3", "3.3", "Methods", "Study setting", "Specify key elements of the study setting (e.g., primary care, secondary care, general population) including number and location of centres."),
    ("3", "3.4", "Methods", "Eligibility criteria", "Describe eligibility criteria for participants."),
    ("3", "3.5", "Methods", "Treatments received", "Give details of treatments received, if relevant."),
    ("3", "3.6", "Methods", "Outcome definition", "Clearly define the outcome that is predicted by the prediction model, including how and when assessed."),
    ("3", "3.7", "Methods", "Outcome blinding", "Report any actions to blind assessment of the outcome to be predicted."),
    ("3", "3.8", "Methods", "Predictors", "Clearly define all predictors used in developing or validating the multivariable prediction model, including how and when they were measured."),
    ("3", "3.9", "Methods", "Predictors blinding", "Report any actions to blind assessment of predictors for the outcome and other predictors."),
    ("3", "3.10", "Methods", "Sample size", "Explain how the study size was arrived at."),
    ("3", "3.11", "Methods", "Handling missing data", "Describe how missing data were handled (e.g., complete-case analysis, single imputation, multiple imputation) with details of any imputation method."),
    ("3", "3.12", "Methods", "Statistical analysis methods", "Describe how predictors were handled in the analyses."),
    ("3", "3.13", "Methods", "Model type and validation", "Specify type of model, all model-building procedures (including any predictor selection), and method for internal validation."),
    ("3", "3.14", "Methods", "Model performance measures", "Specify all measures used to assess model performance and, if relevant, to compare multiple models."),
    ("3", "3.15", "Methods", "Risk groups", "Provide details on how risk groups were created, if done."),
    
    # Results
    ("4", "4.1", "Results", "Flow of participants", "Describe the flow of participants through the study, including the number of participants with and without the outcome and, if applicable, a summary of the follow-up time. A diagram may be helpful."),
    ("4", "4.2", "Results", "Participant characteristics", "Describe the characteristics of the participants (basic demographics, clinical features, available predictors), including the number of participants with missing data for predictors and outcome."),
    ("4", "4.3", "Results", "Number of participants", "Specify the number of participants and outcome events in each analysis."),
    ("4", "4.4", "Results", "Unadjusted associations", "If done, report the unadjusted association between each candidate predictor and outcome."),
    ("4", "4.5", "Results", "Full prediction model", "Present the full prediction model to allow predictions for individuals (i.e., all regression coefficients, and model intercept or baseline survival at a given time point)."),
    ("4", "4.6", "Results", "Model use", "Explain how to use the prediction model."),
    ("4", "4.7", "Results", "Performance measures", "Report performance measures (with CIs) for the prediction model."),
    
    # Discussion
    ("5", "5.1", "Discussion", "Limitations", "Discuss any limitations of the study (e.g., nonrepresentative sample, few events per predictor, missing data)."),
    ("5", "5.2", "Discussion", "Interpretation", "Give an overall interpretation of the results, considering objectives, limitations, and results from similar studies, and other relevant evidence."),
    ("5", "5.3", "Discussion", "Implications", "Discuss the potential clinical use of the model and implications for future research."),
    
    # Other information
    ("6", "6.1", "Other information", "Supplementary information", "Provide information about the availability of supplementary resources, such as study protocol, Web calculator, and data sets."),
    ("6", "6.2", "Other information", "Funding", "Give the source of funding and the role of the funders for the present study.")
]

# Functie: Extract tekst en posities uit PDF
def extract_text_with_positions(pdf_file):
    extracted_text = []
    with pdfplumber.open(pdf_file) as pdf:
        for page_number, page in enumerate(pdf.pages):
            for word in page.extract_words():
                extracted_text.append({
                    "text": word["text"],
                    "x0": word["x0"],
                    "x1": word["x1"],
                    "top": word["top"],
                    "bottom": word["bottom"],
                    "page_number": page_number
                })
    return extracted_text

# Functie: Highlight relevante tekst in originele PDF
def highlight_text_in_pdf(input_pdf, highlights):
    # Maak tijdelijk bestand voor het geüploade PDF-bestand
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(input_pdf.read())
        temp_file_path = temp_file.name

    # Open PDF met PyMuPDF
    pdf_document = fitz.open(temp_file_path)
    total_pages = pdf_document.page_count  # Haal totaal aantal pagina's op

    for highlight in highlights:
        # Controleer of de pagina bestaat in het document
        if highlight["page_number"] < total_pages:
            page = pdf_document[highlight["page_number"]]
            rect = fitz.Rect(highlight["x0"], highlight["top"], highlight["x1"], highlight["bottom"])
            page.add_highlight_annot(rect)
        else:
            st.error(f"Highlight verwijst naar een niet-bestaande pagina: {highlight['page_number'] + 1}")

    # Sla gemarkeerde PDF op in een buffer
    output_pdf = BytesIO()
    pdf_document.save(output_pdf)
    pdf_document.close()
    output_pdf.seek(0)
    return output_pdf

# Functie: Analyseren en highlights genereren
def analyze_and_highlight(pdf_file, extracted_text):
    highlights = []
    document_text = " ".join([char["text"] for char in extracted_text])
    for chapter, item_code, section, item, description in TRIPOD_CHECKLIST:
        prompt = f"""
        Criterion:
        {item} - {description}

        Article Text:
        {document_text[:5000]}

        Which text is relevant to this evaluation?
        """
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=300
        )
        relevant_text = response.generations[0].text.strip()

        # Match relevant text in extracted data
        for char_data in extracted_text:
            if relevant_text in char_data["text"]:
                highlights.append({
                    "page_number": char_data["page_number"],
                    "x0": char_data["x0"],
                    "x1": char_data["x1"],
                    "top": char_data["top"],
                    "bottom": char_data["bottom"]
                })
    return highlights

# Streamlit-interface
def main():
    st.title("TRIPOD Evaluator met Highlights")
    st.write("Upload een PDF en ontvang een geëvalueerd en gemarkeerd document volgens TRIPOD-criteria.")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        extracted_text = extract_text_with_positions(uploaded_file)
        highlights = analyze_and_highlight(uploaded_file, extracted_text)
        highlighted_pdf = highlight_text_in_pdf(uploaded_file, highlights)

        st.download_button(
            label="Download Highlighted PDF",
            data=highlighted_pdf,
            file_name="highlighted_tripod_report.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
