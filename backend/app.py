import streamlit as st
import asyncio
import os
import base64

from paper_generator import generate_sections, generate_latex
from utils import extract_text_from_pdf, extract_text_from_pptx, clean_input, latex_escape
from compile_utils import compile_latex_to_pdf

st.set_page_config(page_title="ResearchPilot | AI Paper Generator", layout="wide")

import pandas as pd
from datetime import datetime

try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    GSheetsConnection = None

def log_analytics(title, author, num_files):
    if GSheetsConnection is None:
        return
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Attempt to read existing analytics, ignore errors if empty or not created
        df = conn.read(worksheet="Analytics", usecols=[0, 1, 2, 3], ttl=5)
        new_row = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "author": author,
            "title": title,
            "files": num_files
        }])
        
        # If it's a new or uninitialized sheet, df might be empty or missing columns
        if df.empty or 'timestamp' not in df.columns:
            updated_df = new_row
        else:
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
        conn.update(worksheet="Analytics", data=updated_df)
    except Exception as e:
        # Silently fail so user generation is not interrupted, but print to console
        print(f"Analytics logging error: {e}")

is_admin = st.query_params.get("admin") == "true"

if is_admin:
    st.header("📊 App Analytics Dashboard")
    st.markdown("Real-time usage analytics logging to Google Sheets.")
    st.divider()
    
    if GSheetsConnection is None:
        st.warning("Please install `st-gsheets-connection` and configure secrets.")
    else:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(worksheet="Analytics", usecols=[0, 1, 2, 3], ttl=5)
            
            if df.empty or 'timestamp' not in df.columns:
                st.info("No analytics data collected yet.")
            else:
                total_generations = len(df)
                unique_users = df['author'].nunique() if 'author' in df.columns else total_generations
                
                col1, col2 = st.columns(2)
                col1.metric("Total Papers Generated", total_generations)
                col2.metric("Total Unique Authors", unique_users)
                
                st.subheader("Recent Activity")
                # Sort by newest first
                st.dataframe(df.iloc[::-1].head(50), use_container_width=True)
                
                st.subheader("Daily Usage")
                if 'timestamp' in df.columns:
                    df['date'] = pd.to_datetime(df['timestamp']).dt.date
                    daily_counts = df.groupby('date').size()
                    st.bar_chart(daily_counts)
                
        except Exception as e:
            st.error(f"Failed to load analytics: {e}. Are your Google Sheets credentials configured in `.streamlit/secrets.toml`?")

else:
    st.title("ResearchPilot | AI Paper Generator")
    st.markdown("### Automated Academic Research Paper Generator")
    st.markdown("Provide the core details of your research, and our AI will generate a structured academic paper for you in double-column LaTeX format.")
    st.divider()
    
    with st.container():
        st.markdown("#### Research Inputs")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Paper Title", placeholder="e.g., The Impact of Quantum Computing on Cryptography")
        with col2:
            author = st.text_input("Author Name", placeholder="e.g., Jane Doe", value="")
            
        method = st.text_area("Methodology", height=150, placeholder="Describe your research methods, logic, and techniques...")
        results = st.text_area("Key Results", height=150, placeholder="Summarize your data and findings...")
        code = st.text_area("Optional Code/Snippet", height=100, placeholder="Paste your core algorithm or GitHub repository link...")
        files = st.file_uploader("Upload PDFs/PPTXs (Background Data)", accept_multiple_files=True, type=['pdf', 'pptx'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            generate_btn = st.button("Generate Paper", type="primary", use_container_width=True)
    st.divider()
    
    if generate_btn:
        if not title or not author or not method or not results:
            st.error("Please fill in all required fields: Title, Author, Methodology, and Key Results.")
        else:
            with st.spinner("Analyzing inputs and processing files..."):
                file_content = ""
                file_count = 0
                if files:
                    file_count = len(files)
                    for f in files:
                        content = f.read()
                        filename = f.name.lower()
                        extracted = ""
                        if filename.endswith(".pdf"):
                            extracted = extract_text_from_pdf(content)
                        elif filename.endswith(".pptx") or filename.endswith(".ppt"):
                            extracted = extract_text_from_pptx(content)
                        else:
                            try:
                                extracted = content.decode("utf-8")
                            except:
                                extracted = "Filename: " + filename
                        
                        if extracted and not extracted.startswith("Error"):
                            file_content += f"\n--- {f.name} ---\n{extracted}\n"
                
                clean_t = clean_input(title)
                clean_m = clean_input(method)
                clean_r = clean_input(results)
                clean_c = clean_input(code or "")
                
                # Log analytics tracking
                log_analytics(clean_t, author, file_count)
    
            with st.spinner("Generating research paper sections using AI... (This may take a minute or two)"):
                sections = asyncio.run(generate_sections(
                    title=clean_t,
                    method=clean_m,
                    results=clean_r,
                    code_info=clean_c,
                    file_info=file_content
                ))
                
                if "error" in sections:
                    st.error(f"Error: {sections['error']}")
                else:
                    escaped_sections = {k: latex_escape(v) for k, v in sections.items()}
                    latex_code = generate_latex(latex_escape(clean_t), author, escaped_sections)
                    
                    st.session_state['sections'] = sections
                    st.session_state['latex_code'] = latex_code
                    st.success("Paper generated successfully!")
    
    if 'sections' in st.session_state and 'latex_code' in st.session_state:
        st.header("Generated Paper Preview")
        
        tab1, tab2, tab3 = st.tabs(["PDF Preview", "LaTeX Source", "Section Preview"])
        
        with tab1:
            col_a, col_b = st.columns(2)
            with col_a:
                compile_clicked = st.button("Compile & Preview PDF", use_container_width=True)
            with col_b:
                import html
                safe_latex = html.escape(st.session_state['latex_code'])
                overleaf_form_tab1 = f'''
                <form action="https://www.overleaf.com/docs" method="post" target="_blank">
                    <textarea name="snip" style="display:none;">{safe_latex}</textarea>
                    <button type="submit" style="
                        width: 100%;
                        background-color: #279B61;
                        color: white;
                        border: none;
                        padding: 0.35rem 1rem;
                        border-radius: 0.45rem;
                        cursor: pointer;
                        font-size: 1rem;
                        font-weight: 400;
                        line-height: 1.6;
                        text-align: center;
                    ">Edit in overleaf</button>
                </form>'''
                st.markdown(overleaf_form_tab1, unsafe_allow_html=True)

            if compile_clicked:
                with st.spinner("Compiling LaTeX to PDF... (If this fails, please click Edit in Overleaf instead)"):
                    try:
                        pdf_bytes = compile_latex_to_pdf(st.session_state['latex_code'])
                        st.session_state['pdf_bytes'] = pdf_bytes
                    except Exception as e:
                        st.error(f"PDF Compilation Error: {e} \n\nStreamlit Cloud may not have enough memory to run pdflatex. Click 'Edit in overleaf' to see the PDF!")
            
            if 'pdf_bytes' in st.session_state:
                b64_pdf = base64.b64encode(st.session_state['pdf_bytes']).decode('utf-8')
                pdf_display = f'<object data="data:application/pdf;base64,{b64_pdf}" type="application/pdf" width="100%" height="800px"><iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="800px">This browser does not support PDFs. Please download the PDF to view it.</iframe></object>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                st.download_button("Download PDF", data=st.session_state['pdf_bytes'], file_name="research_paper.pdf", mime="application/pdf")
                
        with tab2:
            st.code(st.session_state['latex_code'], language='latex')
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("Download .tex", data=st.session_state['latex_code'], file_name="research_paper.tex", mime="text/plain", use_container_width=True)
                
            with col2:
                import html
                safe_latex = html.escape(st.session_state['latex_code'])
                overleaf_form = f'''
                <form action="https://www.overleaf.com/docs" method="post" target="_blank">
                    <textarea name="snip" style="display:none;">{safe_latex}</textarea>
                    <button type="submit" style="
                        width: 100%;
                        background-color: #279B61;
                        color: white;
                        border: none;
                        padding: 0.35rem 1rem;
                        border-radius: 0.45rem;
                        cursor: pointer;
                        font-size: 1rem;
                        font-weight: 400;
                        line-height: 1.6;
                        text-align: center;
                    ">Edit in overleaf</button>
                </form>'''
                st.markdown(overleaf_form, unsafe_allow_html=True)
            
        with tab3:
            for key, value in st.session_state['sections'].items():
                if key != 'error':
                    st.subheader(key.replace('_', ' ').title())
                    st.write(value)
