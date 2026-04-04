import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_sections(title, method, results, code_info="", file_info=""):
    """
    Generate research paper sections using Groq LLM matching Arxiv structure.
    """
    prompt = f"""
    You are an expert academic researcher and writer. Your task is to generate a structured research paper based on the following inputs:

    TITLE: {title}
    METHODOLOGY: {method}
    RESULTS: {results}
    OPTIONAL CODE INFO: {code_info}
    OPTIONAL FILE EXTRACTION: {file_info}

    CRITICAL INSTRUCTION:
    Follow the structure and style of the paper: "Adaptive Financial Sentiment Analysis for NIFTY 50 via Instruction-Tuned LLMs, RAG and Reinforcement Learning Approaches" (Arxiv: 2512.20082).
    
    REQUIRED SECTIONS:
    1. ABSTRACT: A concise summary of the research (approx 150-200 words). Include a 'Keywords' list at the bottom.
    2. INTRODUCTION: Provide background, state the problem, and outline the contribution.
    3. LITERATURE REVIEW: Discuss related work and identify research gaps.
    4. DATASETS: Describe the data sources, preprocessing, and any datasets used.
    5. METHODOLOGY: Detailed technical section covering algorithms, pipelines, or frameworks.
    6. EVALUATION AND METRICS: Description of the experimental setup and performance indicators.
    7. RESULTS: Analysis of findings with technical depth.
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
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096,
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
