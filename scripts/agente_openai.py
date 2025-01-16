import os
import openai
from config import OPENAI_API_KEY

# Configurar a API
openai.api_key = OPENAI_API_KEY

def process_resumo_with_openai(resumo, prompt):
    """
    Processa um resumo usando a API OpenAI com um prompt personalizado.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{prompt}\n\n{resumo}",
        max_tokens=500,
        temperature=0.7,
    )
    return response["choices"][0]["text"].strip()

if __name__ == "__main__":
    resumo_dir = "resumos-artigos"
    output_dir = "resultados-openai"
    os.makedirs(output_dir, exist_ok=True)

    # Prompt para direcionar a análise
    prompt = (
        "Baseando-se no resumo fornecido, identifique as contribuições mais relevantes "
        "do artigo e sugira possíveis aplicações práticas."
    )

    for resumo_file in os.listdir(resumo_dir):
        if resumo_file.endswith(".txt"):
            resumo_path = os.path.join(resumo_dir, resumo_file)

            with open(resumo_path, "r", encoding="utf-8") as f:
                resumo = f.read()

            # Processar resumo com a API OpenAI
            resultado = process_resumo_with_openai(resumo, prompt)

            # Salvar o resultado
            output_path = os.path.join(output_dir, resumo_file.replace(".txt", "_resultado.txt"))
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(resultado)
