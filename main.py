import requests
import json
import os
from PyPDF2 import PdfReader
import tiktoken
import re

OLLAMA_API_URL = "http://localhost:11434/api/chat"
DADOS_DIR = "dados"
EXTRACAO_DIR = "extracao-variaveis"
MAX_TOKENS = 2048  # Defina o limite de tokens/caracteres conforme necessário

def contar_tokens(texto):
    encoding = tiktoken.get_encoding("cl100k_base")  # Use o encoding apropriado para o seu modelo
    tokens = encoding.encode(texto)
    return len(tokens)

def selecionar_secoes_relevantes(texto):
    secoes_alvo = ["Abstract", "Introduction", "Results", "Discussion", "Conclusions"]
    
    # Criar um padrão regex para capturar títulos de seções
    padrao_secoes = re.compile(rf"(?i)^({'|'.join(secoes_alvo)})\b", re.MULTILINE)
    
    secoes_encontradas = {}
    matches = list(padrao_secoes.finditer(texto))
    
    for i, match in enumerate(matches):
        titulo = match.group(1)  # Nome da seção encontrada
        inicio = match.start()   # Posição inicial da seção
        
        # Definir onde essa seção termina (antes da próxima seção)
        if i + 1 < len(matches):
            fim = matches[i + 1].start()
        else:
            fim = len(texto)
        
        secoes_encontradas[titulo] = texto[inicio:fim].strip()
    
    # Retornar o texto filtrado apenas com as seções encontradas
    return "\n\n".join(secoes_encontradas.values())

def extracao_variavel_primaria(texto, nome_artigo):
    texto_relevante = selecionar_secoes_relevantes(texto)
    num_tokens = contar_tokens(texto_relevante)

    if num_tokens > MAX_TOKENS:
        print(f"Texto excede o limite de {MAX_TOKENS} tokens e pode ser truncado!")

    print(f"Texto enviado à LLM: {texto_relevante}...")

    # Dividir o texto em blocos
    blocos = []
    inicio = 0
    while inicio < len(texto_relevante):
        fim = min(inicio + MAX_TOKENS, len(texto_relevante))
        blocos.append(texto_relevante[inicio:fim])
        inicio = fim

    # Enviar os blocos para a LLM
    resultado_content = ""
    headers = {"Content-Type": "application/json"}

    for bloco in blocos:
        data = {
            "model": "llama2",
            "messages": [{
                "role": "user",
                "content": f"""
You are an assistant specialized in scientific text analysis. Your task is to extract detailed and structured information from the provided text, based on the abstract, introduction, and results/conclusion.

        Extract the following information:

        1. **Primary Variable Evaluated**:
           - Clearly identify the primary variable analyzed in the study. Use an objective and precise description.

        2. **Results Related to the Primary Variable**:
           - Organize the information into the following fields:
             - **Sample**: Include the sample size, always with clear numbers and units (e.g., "200 participants").
             - **Qualitative**: Summarize subjective or general conclusions.
             - **Quantitative**: Include relevant metrics, statistics, or numbers, always with units (e.g., "15%", "SMD 1.107, p < 0.05").
             - **Other Details**: Provide additional relevant information that complements the above data.
Extract the following information:

1. **Sample Size**:
   - Clearly specify the total sample size and any subgroup sizes reported (e.g., 'N = 365 students').

2. **Quantitative Metrics**:
   - Summarize all numerical metrics with their descriptions. Include statistics such as means, standard deviations, percentages, p-values, correlations, or other relevant values. For each metric, include:
     - **Metric Description**: A clear explanation of what the metric represents.
     - **Value**: The reported number.
     - **Unit**: The measurement unit if applicable (e.g., 'points', '%').
     - **Standard Deviation** (if available): The SD value.

3. **Comparisons or Statistical Tests**:
   - Identify comparisons made (e.g., pre- and post-test scores) and the type of statistical tests applied (e.g., t-test, ANOVA).
   - Include p-values or confidence intervals if mentioned.

4. **Additional Quantitative Details**:
   - Include any additional quantitative information or notes that complement the above fields.

### Response Format:
The response must be in JSON format:
{{
    "article_name": "Title of the Article",
    "quantitative_results": {{
        "sample_size": {{
            "total": "Total sample size",
            "subgroups": {{
                "group_1": "Size of group 1",
                "group_2": "Size of group 2"
            }}
        }},
        "metrics": [
            {{
                "description": "What the metric represents",
                "value": "Reported numerical value",
                "unit": "Measurement unit",
                "std_dev": "Standard deviation (if available)"
            }}
        ],
        "comparisons": [
            {{
                "description": "Comparison details",
                "statistical_test": "Type of statistical test",
                "p_value": "Value if available"
            }}
        ],
        "additional_details": "Any complementary quantitative information"
    }}
}}

Below is the article's text. Focus on extracting quantitative results from the abstract, introduction, and results:
---------------------
{bloco}
"""
        }]
        }

        # Enviar solicitação para a API
        try:
            response = requests.post(OLLAMA_API_URL, json=data, headers=headers, stream=True)
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            json_line = json.loads(line)
                            resultado_content += json_line.get("message", {}).get("content", "")
                            if json_line.get("done", False):
                                break
                        except ValueError:
                            print("Erro ao decodificar uma linha JSON:", line)
            else:
                print(f"Erro ao conectar à API: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao realizar a solicitação: {e}")

    # Retornar o conteúdo final com os resultados
    return resultado_content

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
                        page_text = page.extract_text()
                        if page_text:
                            texto += page_text
            except Exception as e:
                print(f"Erro ao ler o arquivo PDF {arquivo}: {e}")

            if texto:
                nome_artigo = os.path.splitext(arquivo)[0]
                resultado_extracao = extracao_variavel_primaria(texto, nome_artigo)
                if resultado_extracao:
                    caminho_resultado_extracao = os.path.join(EXTRACAO_DIR, f"extracao_variaveis_{arquivo}.json")
                    with open(caminho_resultado_extracao, 'w', encoding='utf-8') as resultado_extracao_f:
                        json.dump(json.loads(resultado_extracao), resultado_extracao_f, ensure_ascii=False, indent=4)
                    print(f"Arquivo salvo em: {caminho_resultado_extracao}")
                else:
                    print(f"Falha ao processar arquivo: {arquivo}")

if __name__ == "__main__":
    processar_arquivos()
