import os
from dotenv import load_dotenv
import transformers
from PyPDF2 import PdfReader

# Carregar as variáveis de ambiente
load_dotenv()

# Pegar a chave da API do Hugging Face
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

# Configurar o pipeline de resumo de texto
pipeline = transformers.pipeline(
    "summarization",
    model="google/pegasus-xsum",
    tokenizer="google/pegasus-xsum"
)

# Função para extrair texto de um PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Função para dividir o texto em partes menores
def split_text(text, max_length=1024):
    sentences = text.split('. ')
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) + 1 <= max_length:
            chunk += sentence + ". "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + ". "
    if chunk:
        chunks.append(chunk.strip())
    return chunks

# Caminhos das pastas
input_folder = "dados"
output_folder = "resumos-artigos"

# Criar a pasta de saída se não existir
os.makedirs(output_folder, exist_ok=True)

# Processar cada PDF na pasta de entrada
for pdf_file in os.listdir(input_folder):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(input_folder, pdf_file)
        text = extract_text_from_pdf(pdf_path)
        
        # Dividir o texto em partes menores
        text_chunks = split_text(text)
        
        # Gerar resumos para cada parte
        summaries = []
        for chunk in text_chunks:
            prompt = f"As a bibliographic reviewer, summarize the article by focusing on practical implications, key sections, and main results: {chunk}"
            summary = pipeline(prompt, max_length=200, min_length=50, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        
        # Combinar os resumos
        full_summary = "\n".join(summaries)
        
        # Salvar o resumo em um arquivo de texto
        output_path = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}_resumo.txt")
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(full_summary)

print("Resumos gerados com sucesso!")