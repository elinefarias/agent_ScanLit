import requests
import json
import os
from PyPDF2 import PdfReader
import tiktoken

OLLAMA_API_URL = "http://localhost:11434/api/chat"
DADOS_DIR = "dados"
EXTRACAO_DIR = "extracao-variaveis"
MAX_TOKENS = 2048  # Defina o limite de tokens/caracteres conforme necessário

def contar_tokens(texto):
    encoding = tiktoken.get_encoding("cl100k_base")  # Use o encoding apropriado para o seu modelo
    tokens = encoding.encode(texto)
    return len(tokens)

def remover_referencias(texto):
    palavra_chave = "References"
    indice = texto.find(palavra_chave)
    if indice != -1:
        texto = texto[:indice]
    return texto

def selecionar_trechos_relevantes(texto):
    palavras_chave = ["abstract", "resumo", "introduction", "introdução", "results", "resultados", "conclusions", "conclusão", "discussion", "discussão"]
    linhas = texto.split("\n")
    texto_filtrado = "\n".join([linha for linha in linhas if any(p in linha.lower() for p in palavras_chave)])
    return texto_filtrado if texto_filtrado else texto

def resumir_texto(texto, nome_artigo):
    texto_relevante = selecionar_trechos_relevantes(texto)
    texto_sem_referencias = remover_referencias(texto_relevante)
    print(f"Texto enviado à LLM: {texto_sem_referencias[:500]}...")
    partes = [texto_sem_referencias[i:i + MAX_TOKENS] for i in range(0, len(texto_sem_referencias), MAX_TOKENS)]
    resumo_completo = ""

    for parte in partes:
        num_tokens = contar_tokens(parte)
        print(f"Enviando {num_tokens} tokens para a LLM")
              
        data = {
    "model": "llama2",
    "messages": [{"role": "user", "content": f"""
You are a scientific text analysis assistant. Your task is to extract detailed and structured quantitative results from the provided scientific text, focusing on sample sizes, statistical measures, numerical results, and comparisons.

Extract the following information:

1. **Sample Size**:
   - Clearly specify the total sample size and any subgroup sizes reported (e.g., "N = 365 students").

2. **Quantitative Metrics**:
   - Summarize all numerical metrics with their descriptions. Include statistics such as means, standard deviations, percentages, p-values, correlations, or other relevant values. For each metric, include:
     - **Metric Description**: A clear explanation of what the metric represents.
     - **Value**: The reported number and its unit (e.g., "Mean = 7.18, SD = 3.85").

3. **Comparisons or Statistical Tests**:
   - Identify comparisons made (e.g., pre- and post-test scores) and the type of statistical tests applied (e.g., t-test, ANOVA).
   - Include p-values or confidence intervals if mentioned.

4. **Additional Quantitative Details**:
   - Include any additional quantitative information or notes that complement the above fields.

### Response Format:
The response must be a JSON file:
```json
{{
    "article_name": "{nome_artigo}",
    "quantitative_results": {{
        "sample_size": "clear description of total and subgroup sizes",
        "metrics": [
            {{
                "description": "what the metric represents",
                "value": "reported value and unit"
            }}
        ],
        "comparisons": [
            {{
                "description": "comparison details",
                "statistical_test": "type of test",
                "p_value": "value if available"
            }}
        ],
        "additional_details": "any complementary quantitative information"
    }}
}}
        Below is the article's text. Focus on extracting quantitative results from the abstract, introduction, and results:
        ---------------------
        {parte}
        """}]
        }
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(OLLAMA_API_URL, json=data, headers=headers, stream=True)
            if response.status_code == 200:
                result_content = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            json_line = json.loads(line)
                            result_content += json_line.get("message", {}).get("content", "")
                            if json_line.get("done", False):
                                break
                        except ValueError:
                            print("Erro ao decodificar uma linha JSON:", line)
                resumo_completo += result_content
            else:
                print(f"Erro ao conectar à API: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Erro ao realizar a solicitação: {e}")
            return None

    return resumo_completo

def processar_arquivos():
    if not os.path.exists(EXTRACAO_DIR):
        os.makedirs(EXTRACAO_DIR)

    for arquivo in os.listdir(DADOS_DIR):
        caminho_arquivo = os.path.join(DADOS_DIR, arquivo)
        if os.path.isfile(caminho_arquivo):
            texto = ""
            try:
                reader = PdfReader(caminho_arquivo)
                for page in reader.pages:
                    texto += page.extract_text()
            except Exception as e:
                print(f"Erro ao ler o arquivo PDF {arquivo}: {e}")
            
            if texto:
                nome_artigo = os.path.splitext(arquivo)[0]
                resumo = resumir_texto(texto, nome_artigo)
                if resumo:
                    caminho_resumo = os.path.join(EXTRACAO_DIR, f"resumo_{arquivo}.txt")
                    with open(caminho_resumo, 'w', encoding='utf-8') as resumo_f:
                        resumo_f.write(resumo)
                    print(f"Resumo salvo em: {caminho_resumo}")
                else:
                    print(f"Falha ao resumir o arquivo: {arquivo}")

if __name__ == "__main__":
    processar_arquivos()
