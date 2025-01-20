import os
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModelForCausalLM

def extract_text_from_pdf(pdf_path):
    """
    Extrai o texto de um arquivo PDF.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def gerar_resumo_bloom(texto, prompt="Resuma o texto a seguir:"):
    """
    Gera um resumo usando o modelo Bloom-560M.
    """
    tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom-560m")
    model = AutoModelForCausalLM.from_pretrained("bigscience/bloom-560m")

    # Dividir o texto em partes menores se for muito longo
    max_length = 1024
    chunks = [texto[i:i + max_length] for i in range(0, len(texto), max_length)]

    resumos = []
    for chunk in chunks:
        entrada = f"{prompt}\n\n{chunk}"
        inputs = tokenizer(entrada, return_tensors="pt", truncation=True, max_length=max_length)

        # Gerar o resumo
        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=500,  # Use max_new_tokens instead of max_length
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,  # Use nucleus sampling
            top_k=50,   # Use top-k sampling
        )

        resumo = tokenizer.decode(outputs[0], skip_special_tokens=True)
        resumos.append(resumo)

    # Concatenar todos os resumos
    resumo_final = " ".join(resumos)
    return resumo_final

if __name__ == "__main__":
    pdf_dir = "dados"  # Pasta com os PDFs
    output_dir = "resumos-artigos"  # Pasta para salvar resumos

    os.makedirs(output_dir, exist_ok=True)

    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, pdf_file)

            # Extrair texto do PDF
            texto = extract_text_from_pdf(pdf_path)

            if texto.strip():
                prompt = """
                Summarize the following scientific article by highlighting the most important parts, such as methodology, results, and conclusions. Make sure to include key metrics like accuracy, precision, recall, and any other relevant performance indicators. Focus on the classification methods and their effectiveness:
                """
                resumo = gerar_resumo_bloom(texto, prompt=prompt)

                # Salvar resumo em um arquivo de texto
                resumo_path = os.path.join(output_dir, f"resumo_{os.path.splitext(pdf_file)[0]}.txt")
                with open(resumo_path, "w", encoding="utf-8") as f:
                    f.write(resumo)

                print(f"Resumo gerado e salvo em: {resumo_path}")
            else:
                print(f"Não foi possível extrair texto do PDF: {pdf_file}")