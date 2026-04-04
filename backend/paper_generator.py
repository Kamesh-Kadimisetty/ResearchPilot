import os
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def generate_sections(title, method, results, code_info="", file_info=""):
    """
    Generate research paper sections using Groq LLM matching Arxiv structure.
    """
    # Truncate file_info to prevent exceeding token limits (approx 12k characters)
    if len(file_info) > 12000:
        file_info = file_info[:12000] + "\n...[TRUNCATED]"
        
    file_instruction = ""
    if file_info.strip() and not file_info.startswith("Error"):
        file_instruction = "IMPORTANT: You MUST actively integrate and synthesize the details from 'FILE EXTRACTION' throughout the paper. Use it to enrich the Introduction, Literature Review, and Data/Methodology sections."

    prompt = f"""
    You are an expert academic researcher and writer. Your task is to generate a structured research paper based on the following inputs:

    TITLE: {title}
    METHODOLOGY: {method}
    RESULTS: {results}
    OPTIONAL CODE INFO: {code_info}
    OPTIONAL FILE EXTRACTION: {file_info}

    CRITICAL INSTRUCTION:
    Follow the structure and style of the paper: "Adaptive Financial Sentiment Analysis for NIFTY 50 via Instruction-Tuned LLMs, RAG and Reinforcement Learning Approaches" (Arxiv: 2512.20082).
    {file_instruction}
    
    REQUIRED SECTIONS:
    1. ABSTRACT: A concise summary of the research (approx 150-200 words). Include a 'Keywords' list at the bottom.
    2. INTRODUCTION: Provide background, state the problem, and outline the contribution.
    3. LITERATURE REVIEW: Provide a COMPREHENSIVE and EXPANSIVE discussion of related work. Compare at least 3-4 different academic approaches, identify specific research gaps, and position this work within the current landscape. (Minimum 500 words).
    4. DATASETS: Provide a DETAILED description of data sources, feature engineering, preprocessing steps, and statistical properties of the data. Explain why these datasets were chosen. (Minimum 400 words).
    5. METHODOLOGY: This is the CORE technical section. Provide an exhaustive explanation of algorithms, system architecture, mathematical formulations (using LaTeX notation where applicable), and specific implementation logic. Be highly technical. (Minimum 800 words).
    6. EVALUATION AND METRICS: Describe a RIGOROUS experimental setup. Define multiple performance indicators (e.g., Accuracy, F1-score, MSE, Latency) and explain the validation strategy (e.g., K-fold cross-validation). (Minimum 400 words).
    7. RESULTS: Analysis of findings with technical depth and data-driven insights.
    8. CONCLUSION: Summary of contributions and future directions.

    Format the output as a dictionary-like structure where each section is clearly labeled:
    [ABSTRACT] ...
    [INTRODUCTION] ...
    [LITERATURE REVIEW] ...
    [DATASETS] ...
    [METHODOLOGY] ...
    [EVALUATION AND METRICS] ...
    [RESULTS] ...
    [CONCLUSION] ...

    IMPORTANT: Aim for a high word count and professional academic tone. Do not be brief; expand on every point to ensure the paper is substantial.
    """

    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=6000,
        )
        response_text = completion.choices[0].message.content
        return parse_sections(response_text)
    except Exception as e:
        return {"error": f"Groq API Error: {str(e)}"}

def parse_sections(text):
    """Parse the LLM response into a dictionary of sections."""
    sections = {}
    current_section = None
    lines = text.split("\n")
    
    section_map = {
        "ABSTRACT": "abstract",
        "INTRODUCTION": "introduction",
        "LITERATURE REVIEW": "literature_review",
        "DATASETS": "datasets",
        "METHODOLOGY": "methodology",
        "EVALUATION AND METRICS": "evaluation",
        "RESULTS": "results",
        "CONCLUSION": "conclusion"
    }

    for line in lines:
        found = False
        for key, val in section_map.items():
            if f"[{key}]" in line.upper():
                current_section = val
                sections[current_section] = ""
                found = True
                break
        
        if not found and current_section:
            sections[current_section] += line + "\n"

    return {k: v.strip() for k, v in sections.items()}

def generate_latex(title, author, sections):
    """Wrap the sections into a professional double-column LaTeX document."""
    latex_template = r"""\documentclass[twocolumn]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{a4paper, margin=0.75in}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}

\title{\textbf{""" + title + r"""}}
\author{""" + author + r"""}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
""" + sections.get('abstract', '') + r"""
\end{abstract}

\section{Introduction}
""" + sections.get('introduction', '') + r"""

\section{Literature Review}
""" + sections.get('literature_review', '') + r"""

\section{Datasets}
""" + sections.get('datasets', '') + r"""

\section{Methodology}
""" + sections.get('methodology', '') + r"""

\section{Evaluation and Metrics}
""" + sections.get('evaluation', '') + r"""

\section{Results}
""" + sections.get('results', '') + r"""

\section{Conclusion}
""" + sections.get('conclusion', '') + r"""

\bibliographystyle{plain}
\end{document}
"""
    return latex_template
