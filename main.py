import requests
import json
import os
from PyPDF2 import PdfReader
from crewai import Crew  # Corrigido o nome da importação
import tiktoken

OLLAMA_API_URL = "http://localhost:11434/api/chat"
DADOS_DIR = "dados"
RESUMOS_DIR = "resumos-artigos"
MAX_TOKENS = 2048  # Defina o limite de tokens/caracteres conforme necessário

def contar_tokens(texto):
    encoding = tiktoken.get_encoding("cl100k_base")  # Use o encoding apropriado para o seu modelo
    tokens = encoding.encode(texto)
    return len(tokens)

def remover_referencias(texto):
    # Supondo que as referências comecem com "References"
    palavra_chave = "References"
    indice = texto.find(palavra_chave)
    if indice != -1:
        texto = texto[:indice]
    return texto

def resumir_texto(texto):
    texto_sem_referencias = remover_referencias(texto)
    print(f"Texto enviado à LLM: {texto_sem_referencias[:500]}...")  # Adiciona esta linha para imprimir o início do texto
    partes = [texto_sem_referencias[i:i + MAX_TOKENS] for i in range(0, len(texto_sem_referencias), MAX_TOKENS)]
    resumo_completo = ""

    for parte in partes:
        num_tokens = contar_tokens(parte)
        print(f"Enviando {num_tokens} tokens para a LLM")
        
        data = {
            "model": "llama2",
            "messages": [{"role": "user", "content": f"Resuma o seguinte texto: {parte}"}]
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
    if not os.path.exists(RESUMOS_DIR):
        os.makedirs(RESUMOS_DIR)

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
                resumo = resumir_texto(texto)
                if resumo:
                    caminho_resumo = os.path.join(RESUMOS_DIR, f"resumo_{arquivo}.txt")
                    with open(caminho_resumo, 'w', encoding='utf-8') as resumo_f:
                        resumo_f.write(resumo)
                    print(f"Resumo salvo em: {caminho_resumo}")
                else:
                    print(f"Falha ao resumir o arquivo: {arquivo}")

if __name__ == "__main__":
    processar_arquivos()