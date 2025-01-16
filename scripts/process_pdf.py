import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

if __name__ == "__main__":
    pdf_dir = "dados"
    output_dir = "resumos-artigos"

    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, pdf_file)
            text = extract_text_from_pdf(pdf_path)

            # Salvar o texto extraído (opcional)
            txt_path = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
