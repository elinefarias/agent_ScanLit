import os
from transformers import AutoTokenizer, AutoModelForCausalLM

def gerar_resumo_bloom(texto, prompt="Resumo do texto:"):
    """
    Gera um resumo usando o modelo Bloom-560M.
    
    Args:
        texto (str): Texto a ser resumido.
        prompt (str): Prompt para orientar o resumo.
        
    Returns:
        str: Resumo gerado.
    """
    # Carregar o tokenizador e o modelo
    tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom-560m")
    model = AutoModelForCausalLM.from_pretrained("bigscience/bloom-560m")

    # Combinar o prompt com o texto
    entrada = f"{prompt}\n\n{texto}"

    # Tokenizar o texto
    inputs = tokenizer(entrada, return_tensors="pt", truncation=True, max_length=1024)

    # Gerar o resumo
    outputs = model.generate(
        inputs["input_ids"],
        max_length=150,  # Limitar o tamanho do resumo
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
    )

    # Decodificar a saída
    resumo = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return resumo

if __name__ == "__main__":
    input_dir = "resumos-artigos"  # Pasta com os textos extraídos
    output_dir = "resumos-artigos"  # Pasta onde os resumos serão salvos

    os.makedirs(output_dir, exist_ok=True)

    for txt_file in os.listdir(input_dir):
        if txt_file.endswith(".txt"):
            txt_path = os.path.join(input_dir, txt_file)
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

    # Preparar entrada com o prompt
    entrada = f"{prompt}\n\n{texto}"
    inputs = tokenizer(entrada, return_tensors="pt", truncation=True, max_length=1024)

    # Gerar o resumo
    outputs = model.generate(
        inputs["input_ids"],
        max_length=150,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
    )

    resumo = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return resumo

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
                # Gerar resumo usando o Bloom
                prompt = "Resuma o texto destacando as principais ideias:"
                resumo = gerar_resumo_bloom(texto, prompt=prompt)

                # Salvar resumo em um arquivo de texto
                resumo_path = os.path.join(output_dir, f"resumo_{os.path.splitext(pdf_file)[0]}.txt")
                with open(resumo_path, "w", encoding="utf-8") as f:
                    f.write(resumo)

                print(f"Resumo gerado e salvo em: {resumo_path}")
            else:
                print(f"Não foi possível extrair texto do PDF: {pdf_file}")

            # Ler o texto do arquivo
            with open(txt_path, "r", encoding="utf-8") as f:
                texto = f.read()

            # Gerar o resumo
            prompt = "Por favor, resuma o texto com ênfase nos pontos mais importantes:"
            resumo = gerar_resumo_bloom(texto, prompt=prompt)

            # Salvar o resumo no arquivo
            resumo_path = os.path.join(output_dir, f"resumo_{txt_file}")
            with open(resumo_path, "w", encoding="utf-8") as f:
                f.write(resumo)

            print(f"Resumo gerado e salvo em: {resumo_path}")
