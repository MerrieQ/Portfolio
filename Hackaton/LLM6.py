import streamlit as st
import pdfplumber
import cohere
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from io import BytesIO

# Cohere API-configuration
API_KEY = "9jp4D6PePyb4bSA8C6ZStJb4rPQQh7mehqygg7zs"
co = cohere.Client(API_KEY)

# Complete TRIPOD-checklist
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

# Function: Extract text from PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function: Search for the correct score in the feedback
def extract_score_from_feedback(feedback):
    for word in feedback.split():
        if word.isdigit() and 1 <= int(word) <= 5:
            return int(word)
    return 1

# Function: Analyse document with the TRIPOD-checklist
def analyze_document_with_llm(document_text):
    results = []
    summary_table = []
    for chapter, item_code, section, item, description in TRIPOD_CHECKLIST:
        prompt = f"""
        Analyseer het volgende academische artikel op het volgende TRIPOD-criterium:

        Criterium:
        Hoofdstuk: {chapter} ({section})
        Item: {item_code} - {item}
        Beschrijving: {description}

        Artikeltekst:
        {document_text[:5000]}

        Geef een beoordeling van 1 tot 5 (waarbij 1 = voldoet niet en 5 = voldoet volledig).  
        Geef daarnaast het specifieke tekstfragment dat je gebruikt voor deze beoordeling.
        """
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=2048,
            temperature=0.7
        )
        feedback = response.generations[0].text.strip()

        # Extract score
        score = extract_score_from_feedback(feedback)

        # Extract relevant fragment
        relevant_fragment = "Geen specifiek fragment gevonden."
        if "Fragment:" in feedback:
            relevant_fragment = feedback.split("Fragment:")[-1].strip()

        # Save results
        results.append({
            "Chapter": chapter,
            "Item": item_code,
            "Section": section,
            "Item Name": item,
            "Feedback": feedback.split("Fragment:")[0].strip(),
            "Score": score,
            "Relevant Fragment": relevant_fragment
        })
        status = "✔" if score >= 4 else "✘"
        summary_table.append([item_code, item, score, status])
    return results, summary_table

# Function: Generate PDF-rapport
def generate_pdf_report(results, summary_table):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Centered', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT, spaceAfter=12))

    elements = []

    # Titelpage
    elements.append(Paragraph("TRIPOD Evaluation Report", styles['Centered']))
    elements.append(Spacer(1, 20))

    # Table of contents
    elements.append(Paragraph("Inhoudsopgave", styles['Heading2']))
    table_data = [["Item Code", "Item", "Score", "Status"]]
    for row in summary_table:
        item_code, item, score, status = row
        table_data.append([item_code, item, str(score), status])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Feedback per item
    for result in results:
        chapter = result["Chapter"]
        item_code = result["Item"]
        section = result["Section"]
        item = result["Item Name"]
        feedback = result["Feedback"]
        score = result["Score"]
        relevant_fragment = result["Relevant Fragment"]

        elements.append(Paragraph(f"Section: {chapter} - {section}", styles["Heading2"]))
        elements.append(Paragraph(f"Item: {item_code} - {item}", styles["Heading3"]))
        elements.append(Paragraph(f"Score: {score}", styles["BodyText"]))
        elements.append(Paragraph(feedback, styles["BodyText"]))
        if relevant_fragment != "Geen specifiek fragment gevonden.":
            elements.append(Paragraph(f"(Tekstfragment: {relevant_fragment})", styles["Italic"]))
        elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Streamlit-interface
def main():
    st.title("TRIPOD Evaluator voor Academische Artikelen")
    st.markdown(
        """
        <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f9f9f9;
        }
        .stButton>button {
            background-color: #004E89;
            color: white;
            border-radius: 10px;
            font-size: 18px;
        }
        .stDownloadButton>button {
            background-color: #008000;
            color: white;
            border-radius: 10px;
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Upload PDF
    uploaded_file = st.file_uploader("Upload een PDF-bestand", type=["pdf"])

    if uploaded_file is not None:
        # Text extraction
        pdf_text = extract_text_from_pdf(uploaded_file)

        st.subheader("Extracted Text")
        st.write(
            pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text
        )  # Show a short preview

        # Start analysis 
        if st.button("Start Analyse"):
            st.write("Analyse bezig... Dit kan enkele minuten duren.")
            results, summary_table = analyze_document_with_llm(pdf_text)

            # Generate PDF
            pdf_buffer = generate_pdf_report(results, summary_table)

            # Show downloadbutton
            st.download_button(
                label="Download Rapport als PDF",
                data=pdf_buffer,
                file_name="TRIPOD_rapport.pdf",
                mime="application/pdf",
            )


# Execute program
if __name__ == "__main__":
    main()
