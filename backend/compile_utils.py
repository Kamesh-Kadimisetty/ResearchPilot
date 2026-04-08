import os
import subprocess
import tempfile
import shutil

def compile_latex_to_pdf(latex_code: str) -> bytes:
    """
    Compile LaTeX code to PDF using pdflatex.
    Returns the PDF content as bytes.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_filename = "document.tex"
        tex_path = os.path.join(tmpdir, tex_filename)
        pdf_filename = "document.pdf"
        pdf_path = os.path.join(tmpdir, pdf_filename)

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        try:
            # First pass
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60
            )
            # Second pass (resolves cross-references)
            process = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60
            )
            
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    return f.read()
            else:
                error_msg = process.stdout + "\n" + process.stderr
                # Limiting the error output to avoid blowing up the UI
                raise Exception(f"PDF generation failed. Check your LaTeX code. Log snippet:\n{error_msg[-1000:]}")

        except FileNotFoundError:
            raise Exception("pdflatex is not installed. Please add 'texlive-latex-base', 'texlive-fonts-recommended', 'texlive-latex-extra' to packages.txt.")
        except subprocess.TimeoutExpired:
            raise Exception("pdflatex compilation timed out.")
        except Exception as e:
            raise Exception(f"pdflatex Error: {str(e)}")
