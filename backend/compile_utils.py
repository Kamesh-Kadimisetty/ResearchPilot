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
            # Tectonic handles multiple passes and package downloads automatically
            process = subprocess.run(
                ["tectonic", "-o", tmpdir, tex_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300 # Tectonic may need lots of time to download packages on first run
            )
            
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    return f.read()
            else:
                error_msg = process.stdout + "\n" + process.stderr
                raise Exception(f"PDF generation failed with Tectonic. Log:\n{error_msg}")

        except subprocess.TimeoutExpired:
            raise Exception("Tectonic compilation timed out (possible slow network for package downloads).")
        except Exception as e:
            raise Exception(f"Tectonic Error: {str(e)}")
