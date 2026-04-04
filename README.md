# ResearchPilot | AI Paper Generator

**ResearchPilot AI** is an advanced, automated academic research assistant that transforms core research inputs—such as methodologies, results, and background data—into fully structured, publishable research papers automatically drafted in LaTeX.

The application leverages the computing power of Groq's high-speed LLM APIs to synthesize user insights, draft comprehensive literature reviews, expand on provided datasets, and securely compile professional, double-column `.pdf` academic publications natively in real-time.

---

## 🌟 Project Features

- **Automated Academic Drafting:** Inputs including 'Methodology', 'Key Results', and 'Code Snippets' are effortlessly augmented into a fully-realized `Abstract`, `Introduction`, `Literature Review`, `Methodology`, `Results`, and `Conclusion`.
- **Context-Aware Integration:** Upload multiple standard files (`.pdf`, `.pptx`) as "Background Data". The AI intelligently extracts, synthesizes, and incorporates this context straight into the generation of your paper to ensure factual depth.
- **Arxiv Structure Matching:** The final output accurately matches the structural integrity, cadence, and professional tone of standard academic articles.
- **Live LaTeX Compilation:** The app natively compiles standard LaTeX source code into `.pdf` format utilizing a backend engine, making it available for real-time preview and direct download immediately.
- **Single UI Application:** A seamless, unified single-page application built on Streamlit for a fast, elegant, and interactive user experience.

---

## 🛠️ Step-by-Step Installation & Setup Guide

This guide walks you through every single step required to get ResearchPilot AI up and running on your local machine.

### Step 1: System Prerequisites
Before you begin, ensure you have the following installed on your system:
1. **Python 3.9 or higher**: Download from [python.org](https://www.python.org/downloads/).
2. **LaTeX Compiler (pdflatex)**: The app uses `pdflatex` to compile LaTeX source to PDF. 
   - *Mac*: Install via MacTeX (`brew install --cask mactex-no-gui`)
   - *Windows*: Install via [MiKTeX](https://miktex.org/download)
   - *Linux*: Install via TeX Live (`sudo apt install texlive-full`)

### Step 2: Clone the Repository
Open your terminal/command prompt and clone the project (or navigate to the unzipped project folder):
```bash
git clone <repository_url>
cd "Research Pilot"
```

### Step 3: Navigate to the Application Directory
The entire active application is housed within the `backend` directory. Navigate into it:
```bash
cd backend
```

### Step 4: Install Python Dependencies
It is highly recommended to use a virtual environment before installing dependencies to avoid conflicts.
```bash
# Create a virtual environment (optional but recommended)
python3 -m venv venv

# Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt
```

### Step 5: Procure a Groq API Key
The application relies on Groq for extremely fast AI generation. 
1. Go to [Groq Console](https://console.groq.com/keys).
2. Create an account or log in.
3. Navigate to the **API Keys** section and click **Create API Key**.
4. Copy the generated key immediately (you will not be able to see it again).

### Step 6: Configure Environment Variables
The application needs your API key to authenticate with Groq. We've provided a template for you.
1. Duplicate the template file:
   ```bash
   # Mac/Linux:
   cp .env.template .env
   # Windows:
   copy .env.template .env
   ```
2. Open the newly created `.env` file in any text editor.
3. Replace the placeholder text with your actual Groq API Key:
   ```env
   GROQ_API_KEY=gsk_your_actual_long_api_key_sequence_here
   ```
4. Save and close the `.env` file. Do not commit this file to public repositories (it is usually included in `.gitignore`).

### Step 7: Launch the Application
Start the Streamlit server using the following command inside the `backend` directory:
```bash
streamlit run app.py
```
After a few seconds, the terminal will output a local network URL, and your default web browser should automatically open the interface at `http://localhost:8501`.

---

## 📝 Detailed Usage Guide

Once the Streamlit application is running, follow these steps to generate your first research paper:

### 1. Fill in the "Research Inputs"
- **Paper Title**: Enter the desired title of your paper. (e.g., "Adaptive Financial Sentiment Analysis for NIFTY 50 via Instruction-Tuned LLMs").
- **Author Name**: Enter your name or a placeholder (e.g., "John Doe, University of Technology"). This automatically populates the LaTeX `\author{}` tag.
- **Methodology**: Provide a detailed explanation of your research methods, logic, technical architecture, and implementation. The more technical detail you provide here, the better the final methodology section will be.
- **Key Results**: Summarize your quantitative and qualitative findings. E.g., "The model achieved an F1-score of 92%, outperforming the baseline by 14%."
- **Optional Code/Snippet**: Paste core algorithmic logic, pseudo-code, or configuration snippets. 

### 2. Upload Background Data (Optional but Recommended)
- Click on **Upload PDFs/PPTXs**.
- Select files containing previous literature reviews, raw data sheets, or related PowerPoint presentations. 
- *How it works*: The app parses the text from these files and injects it into the AI's prompt. The AI intelligently synthesizes this to build an accurate and well-referenced "Literature Review" and "Introduction" section.

### 3. Generate Paper
- Click the blue **Generate Paper** button.
- The UI will display a spinner indicating:
  1. Extracted text from your uploaded files.
  2. Synthesizing sections using Groq.
- *Note:* Generation takes roughly 30 to 90 seconds depending on the size of the uploaded files.

### 4. Review, Compile, and Export
Once generated, three tabs will appear:
- **PDF Preview**: Click the *Compile & Preview PDF* button. The app will utilize local LaTeX engines to generate the final double-column visual layout. Once compiled, use the Download PDF button for a sharable document.
- **LaTeX Source**: This tab hosts the raw `.tex` output. If you are a power user or prefer Overleaf, simply copy the code or use the **Download .tex** button to export it for external editing.
- **Section Preview**: An easy-to-read web preview of every generated section (Abstract, Methodology, Results, etc.) without needing to read raw LaTeX source.

---

## 🛠️ Project Architecture

```text
Research Pilot/
├── backend/
│   ├── app.py                  # Main Streamlit application entry point (Unified UI + Backend)
│   ├── compile_utils.py        # Subprocess scripts to compile LaTeX strings to PDF using pdflatex
│   ├── paper_generator.py      # Core LLM prompt engineering, API calling, and Arxiv structuring
│   ├── utils.py                # PyPDF and python-pptx extraction utilities; input sanitizers
│   ├── requirements.txt        # Full project python dependencies 
│   ├── main.py                 # (Legacy) FastAPI Backend endpoints
│   └── .env.template           # Template for defining environment variables
└── frontend/                   
    ├── index.html              # (Legacy) HTML/JS Frontend UI Framework
    ├── script.js               # (Legacy) Javascript implementation calling FastAPI
    └── style.css               # (Legacy) Stylesheet
```

## ⚠️ Troubleshooting

- **"Command 'pdflatex' not found"**: Your system is missing a LaTeX compiler. Ensure you installed MacTeX/MiKTeX as outlined in Step 1.
- **"Groq API Error / Unauthorized"**: Double-check that your `.env` file exists and `GROQ_API_KEY` is spelled correctly and contains a valid key from your Groq console.
- **Failed File Uploads**: If a specific PDF or PPTX is causing an error, it may be corrupted or contain non-extractable flattened images. Provide files with raw text where possible.
