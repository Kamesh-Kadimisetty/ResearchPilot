document.addEventListener("DOMContentLoaded", () => {
    const paperForm = document.getElementById("paper-form");
    const generateBtn = document.getElementById("generate-btn");
    const outputSection = document.getElementById("output-section");
    const latexOutput = document.getElementById("latex-output");
    const sectionsContent = document.getElementById("sections-content");
    const copyBtn = document.getElementById("copy-btn");
    const downloadBtn = document.getElementById("download-btn");
    const previewPdfBtn = document.getElementById("preview-pdf-btn");
    const pdfLoader = document.getElementById("pdf-loader");
    const pdfPreviewContainer = document.getElementById("pdf-preview-container");
    const pdfViewer = document.getElementById("pdf-viewer");
    const fileInput = document.getElementById("file");
    const fileText = document.getElementById("file-text");

    if (fileInput && fileText) {
        fileInput.addEventListener("change", function() {
            if (this.files && this.files.length > 0) {
                if (this.files.length === 1) {
                    fileText.textContent = this.files[0].name;
                } else {
                    fileText.textContent = `${this.files.length} files selected`;
                }
            } else {
                fileText.textContent = "Upload PDFs/PPTXs (Background Data)";
            }
        });
    }

    const API_URL = "http://localhost:8000/generate-paper";
    const PDF_API_URL = "http://localhost:8000/generate-pdf";

    paperForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        // UI State: Loading
        generateBtn.classList.add("loading");
        generateBtn.disabled = true;
        outputSection.classList.add("hidden");

        const formData = new FormData(paperForm);

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to generate paper");
            }

            const data = await response.json();

            // Display LaTeX
            latexOutput.textContent = data.latex;

            // Display Sections Preview
            sectionsContent.innerHTML = "";
            for (const [key, value] of Object.entries(data.sections)) {
                const sectionDiv = document.createElement("div");
                sectionDiv.className = "section-item";
                sectionDiv.innerHTML = `
                    <h4>${key.replace(/_/g, ' ')}</h4>
                    <p>${value.substring(0, 300)}...</p>
                `;
                sectionsContent.appendChild(sectionDiv);
            }

            // Show output
            outputSection.classList.remove("hidden");
            outputSection.scrollIntoView({ behavior: "smooth" });

        } catch (error) {
            console.error("Error:", error);
            alert("Error: " + error.message);
        } finally {
            generateBtn.classList.remove("loading");
            generateBtn.disabled = false;
        }
    });

    // Copy to Clipboard
    copyBtn.addEventListener("click", () => {
        const text = latexOutput.textContent;
        navigator.clipboard.writeText(text).then(() => {
            copyBtn.textContent = "Copied!";
            setTimeout(() => {
                copyBtn.textContent = "Copy to Clipboard";
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    });

    // Download .tex file
    downloadBtn.addEventListener("click", () => {
        const text = latexOutput.textContent;
        const blob = new Blob([text], { type: "text/plain" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "research_paper.tex";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    });

    // Preview PDF
    previewPdfBtn.addEventListener("click", async () => {
        // UI State
        previewPdfBtn.disabled = true;
        pdfLoader.classList.remove("hidden");
        pdfPreviewContainer.classList.add("hidden");

        const formData = new FormData(paperForm);

        try {
            const response = await fetch(PDF_API_URL, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to compile PDF");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            // Set iframe src to the blob URL
            pdfViewer.src = url;
            pdfPreviewContainer.classList.remove("hidden");
            pdfPreviewContainer.scrollIntoView({ behavior: "smooth" });

        } catch (error) {
            console.error("PDF Error:", error);
            alert("PDF Error: " + error.message);
        } finally {
            previewPdfBtn.disabled = false;
            pdfLoader.classList.add("hidden");
        }
    });
});
