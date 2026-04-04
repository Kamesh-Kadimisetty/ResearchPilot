import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
from io import BytesIO

from paper_generator import generate_sections, generate_latex
from utils import extract_text_from_pdf, extract_text_from_pptx, clean_input
from compile_utils import compile_latex_to_pdf

app = FastAPI(title="ResearchPilot API")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-paper")
async def generate_paper(
    title: str = Form(...),
    method: str = Form(...),
    results: str = Form(...),
    code: Optional[str] = Form(None),
    author: str = Form("ResearchPilot AI Assistant"),
    file: Optional[UploadFile] = File(None)
):
    """
    Endpoint to generate a research paper from inputs and optional file.
    """
    file_content = ""
    # Explicitly check if a file was actually uploaded (has a filename)
    if file and file.filename:
        print(f"DEBUG: Receiving file '{file.filename}'...")
        content = await file.read()
        filename = file.filename.lower()
        if filename.endswith(".pdf"):
            file_content = extract_text_from_pdf(content)
        elif filename.endswith(".pptx") or filename.endswith(".ppt"):
            file_content = extract_text_from_pptx(content)
        else:
            # Fallback for other text-based files
            try:
                file_content = content.decode("utf-8")
            except:
                file_content = "Filename: " + filename
        
        print(f"DEBUG: Extracted {len(file_content)} characters from document.")
        if file_content.startswith("Error"):
            print(f"DEBUG: Extraction failed with error: {file_content}")
    else:
        print("DEBUG: No document uploaded or empty filename.")

    # Clean the primary inputs
    clean_title = clean_input(title)
    clean_method = clean_input(method)
    clean_results = clean_input(results)
    clean_code = clean_input(code or "")

    # Generate the research sections
    sections = generate_sections(
        title=clean_title,
        method=clean_method,
        results=clean_results,
        code_info=clean_code,
        file_info=file_content
    )

    if "error" in sections:
        raise HTTPException(status_code=500, detail=sections["error"])

    # Generate the final LaTeX document
    # Escape all content for LaTeX
    from utils import latex_escape
    escaped_sections = {k: latex_escape(v) for k, v in sections.items()}
    latex_code = generate_latex(latex_escape(clean_title), author, escaped_sections)

    return {
        "latex": latex_code,
        "sections": sections
    }

@app.post("/generate-pdf")
async def generate_pdf(
    title: str = Form(...),
    method: str = Form(...),
    results: str = Form(...),
    code: Optional[str] = Form(None),
    author: str = Form("ResearchPilot AI Assistant"),
    file: Optional[UploadFile] = File(None)
):
    """
    Endpoint to generate a research paper and return it as a compiled PDF.
    """
    file_content = ""
    if file and file.filename:
        content = await file.read()
        filename = file.filename.lower()
        if filename.endswith(".pdf"):
            file_content = extract_text_from_pdf(content)
        elif filename.endswith(".pptx") or filename.endswith(".ppt"):
            file_content = extract_text_from_pptx(content)
        else:
            try:
                file_content = content.decode("utf-8")
            except:
                file_content = ""

    # Clean the primary inputs
    clean_title = clean_input(title)
    clean_method = clean_input(method)
    clean_results = clean_input(results)
    clean_code = clean_input(code or "")

    # Generate the research sections
    sections = generate_sections(
        title=clean_title,
        method=clean_method,
        results=clean_results,
        code_info=clean_code,
        file_info=file_content
    )

    if "error" in sections:
        raise HTTPException(status_code=500, detail=sections["error"])

    # Generate LaTeX
    from utils import latex_escape
    escaped_sections = {k: latex_escape(v) for k, v in sections.items()}
    latex_code = generate_latex(latex_escape(clean_title), author, escaped_sections)

    # Compile to PDF
    try:
        pdf_bytes = compile_latex_to_pdf(latex_code)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=research_paper.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Compilation Error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to ResearchPilot API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
