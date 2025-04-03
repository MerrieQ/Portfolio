**TRIPOD Evaluator – HACKATON**
Code: LLM6.py

This application was built during a one-week hackathon for UMC Utrecht. The goal was to automate the assessment of academic articles using the TRIPOD criteria (Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis – Gary S. Collins, 2015). The app allows users to upload a PDF of an academic article and generates a detailed feedback report using a large language model via the Cohere API.

Instead of training our own LLM (which proved infeasible due to time and quality constraints), we used the Cohere API to analyze the article against the TRIPOD checklist.

The file TRIPOD_rapport (14) is the result of the final program. TRIPOD_rapport (11-13) are files to show the improvements made, so those are relatively irrelevant.

**Getting Started**
This guide will help you run the project locally.

**Prerequisites**
To run this software, install the following dependencies:
- Python 3.10+
- streamlit
- pdfplumber
- cohere
- reportlab

You can install all required packages using:
pip install streamlit pdfplumber cohere reportlab

**Installation**
1. Clone the repository:
git clone https://github.com/MerrieQ/Portfolio.git
cd Portfolio/Hackaton

2. Get a free API key from Cohere:
Visit https://dashboard.cohere.com/api-keys and sign in or register.
Create an API key (you may need approval if usage is restricted).

3. Open the file LLM6.py and replace the line:
API_KEY = "APIKEY"
with your own API key.

**Usage**
Run the Streamlit application with the command:
streamlit run LLM6.py

- Upload an academic article in PDF format.
- The app will extract the text, analyze it against the TRIPOD criteria, and score it using Cohere's LLM.
- A downloadable PDF report will be generated with per-item feedback and scores.

**Output**
The generated PDF report is structured with:
- A table of contents summarizing each TRIPOD item and its score
- Per-section feedback, including cited fragments from the paper
- A clean and styled layout using ReportLab

**Contact**
Created by Merlijn Marquering and Robbie van Dijk
Email: merlijn.marquering@gmail.com
Email: robbie.vandijk@student.hu.nl
GitHub: https://github.com/MerrieQ  
Project File: https://github.com/MerrieQ/Portfolio/blob/main/Hackaton/LLM6.py




**Acknowledgments**
- Cohere (https://cohere.ai) – for the LLM API
- TRIPOD Checklist by Gary S. Collins (BMJ, 2015)
- Streamlit – for the fast and interactive UI framework
- ReportLab – for professional PDF generation
- pdfplumber – for extracting structured text from academic PDFs
