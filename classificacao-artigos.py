import os
import openai
import json
import PyPDF2
from config import OPENAI_API_KEY

# Configurar a API
openai.api_key = OPENAI_API_KEY

def extract_text_from_pdf(pdf_path):
    """
    Extrai o texto de um arquivo PDF.
    """
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def process_article_with_openai(article_content, prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em leitura e análise de artigos científicos."},
                {"role": "user", "content": f"{prompt}\n\n{article_content}"}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except openai.error.OpenAIError as e:
        print(f"Erro ao chamar a API OpenAI: {e}")
        return None

def split_text(text, max_tokens=1000):
    """
    Divide o texto em partes menores com base no número máximo de tokens.
    """
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(current_chunk)
            current_chunk = sentence + ". "
            current_tokens = sentence_tokens
        else:
            current_chunk += sentence + ". "
            current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

if __name__ == "__main__":
    base_dir = "artigos"
    output_base_dir = "resultados"
    subdirs = ["IEEE", "WEBOFScience"]

    for subdir in subdirs:
        articles_dir = os.path.join(base_dir, subdir)
        output_dir = os.path.join(output_base_dir, f"resultados-{subdir}")
        os.makedirs(output_dir, exist_ok=True)

        # Verificar se o diretório de artigos existe
        if not os.path.exists(articles_dir):
            print(f"Erro: O diretório '{articles_dir}' não foi encontrado.")
            continue

        # Prompt para direcionar a análise
        prompt = (
            "Objetivo: Classificar resumos de artigos de acordo com as informações especificas definidas nas solicitações contidas em <solicitacoes>. "
            "Assim que reconhecer que o artigo obedece a um critério de inclusão ou exclusão, pare a avaliação e gere um JSON com os campos especificados. "
            "<solicitacoes>"
            "1 - STATUS: Analise o resumo do artigo e verifique se atende aos objetivos da pesquisa em <objetivos> e aos critérios descritos em <criterios>. "
            "Se atender a qualquer critério de inclusão (CI), retorne o status 'Accepted'. "
            "Se atender a qualquer critério de exclusão (CE), retorne o status 'Rejected'. "
            "Caso exista algum artigo duplicado, retorne 'Duplicated'. "
            "2 – CRITERIO: Informe qual o nome do principal critério de inclusão ou exclusão conforme resultado da avaliação conforme descritos em <criterios>."
            "8 - TÍTULO - Extraia o título do artigo."
            "10 - COMMENTS - Justifique o porquê do artigo ter sido classificado com aquele status."
            "</solicitacoes>"
            "<template>"
            "{"
            "  'artigo': 'nome do arquivo.pdf',"
            "  'TÍTULO': 'Título do artigo',"
            "  'STATUS': 'Status do artigo',"
            "  'CRITERIO': 'Resultado do critério de inclusão ou exclusão',"
            "  'COMMENTS': 'Justificativa para a classificação do artigo.'"
            "}"
            "</template>"
            "<criterios>"
            "#Critérios de Inclusão"
            "CI - Tipo de Estudo: Estudos utilizando aprendizado de máquina para classificação de eventos sísmicos."
            "CI - População: Estudos que analisam dados sísmicos reais ou simulados para a classificação de eventos sísmicos."
            "CI - Intervenção: Aplicação de métodos baseados em tensores e/ou métodos baseados em vetores para análise sísmica."
            "CI - Resultados: Estudos que reportam métricas quantitativas de desempenho, como acurácia, precisão, recall e F1-score."
            "CI - Idioma: Estudos publicados em inglês ou português."
            "#Critérios de Exclusão"
            "CE - Tipo de Estudo: Revisões de literatura, artigos de opinião, resumos de conferências sem texto completo disponível."
            "CE - População: Estudos que não envolvem dados sísmicos ou utilizam apenas modelos teóricos sem validação empírica."
            "CE - Intervenção: Estudos que não comparam ou não aplicam métodos baseados em tensores ou vetores."
            "CE - Resultados: Estudos que não apresentam métricas quantitativas para avaliação de desempenho."
            "CE - Idioma: Estudos pagos."
            "</criterios>"
            "<objetivos>"
            "1. Investigar o impacto dos métodos de aprendizado de máquina baseados em tensores na classificação de eventos sísmicos, em comparação com abordagens baseadas em vetores."
            "2. Analisar a precisão e a eficiência dos métodos baseados em tensores na captura de relações multidimensionais em dados sísmicos."
            "3. Identificar as principais aplicações, desafios e avanços recentes no uso de técnicas baseadas em tensores para análise de eventos sísmicos."
            "4. Avaliar a robustez e a escalabilidade dos modelos baseados em tensores em diferentes contextos de dados sísmicos."
            "5. Sintetizar as evidências disponíveis na literatura para orientar futuras pesquisas sobre a utilização de aprendizado de máquina na classificação de eventos sísmicos."
            "</objetivos>"
            "Backstory = Você é um especialista em leitura e análise de artigos científicos. Sua missão é extrair informações cruciais, compreendendo o contexto semântico completo dos artigos. Sua função é fundamental para avaliar a relevância dos artigos analisados. Ao responder as solicitações delimitadas por <solicitacoes>, você deve levar em consideração as definições de controles em <controle> e as restrições em <restricoes>."
            "<controle>"
            "NÍVEIS DE CONTROLE:"
            "1. Entonação: Formal Científico."
            "2. Foco de Tópico: Você deve responder sempre com alto foco no texto do artigo científico."
            "3. Língua: Responda sempre em Português do Brasil como os Brasileiros costumam escrever textos científicos aderindo aos padrões de redação científica do país a não ser o que será especificado para não traduzir."
            "4. Controle de Sentimento: Neutro e científico. Evite superlativos como: inovador, revolucionário e etc."
            "5. Nível Originalidade: 10, onde 1 é pouco original e 10 é muito original. Em hipótese alguma copie frases do texto original."
            "6. Nível de Abstração: 1, onde 1 é muito concreto e real e 10 é muito abstrato e irreal."
            "7. Tempo Verbal: Escreva no passado."
            "</controle>"
            "<restricoes>"
            "O que não deve ser traduzido do inglês para o português brasileiro:"
            "1. Termos técnicos em inglês amplamente aceitos e usado nos textos em português."
            "2. Nome de algoritmos de machine learning."
            "3. Métricas usadas no trabalho."
            "</restricoes>"
            "Tarefa = Leia o arquivo de resumo de artigos e responda em JSON às solicitações definidas em <solicitacoes> usando o modelo definido em <template>. Saída esperada = JSON com as respostas às solicitações definidas em <solicitacoes>, usando o modelo definido em <template>."
        )

        print(f"Iniciando processamento dos artigos na pasta '{articles_dir}'...")

        for article_file in os.listdir(articles_dir):
            if article_file.endswith(".pdf"):
                article_path = os.path.join(articles_dir, article_file)
                print(f"Processando arquivo: {article_path}")

                # Extrair texto do PDF
                article_content = extract_text_from_pdf(article_path)

                # Dividir o conteúdo do artigo em partes menores
                article_chunks = split_text(article_content)

                # Processar cada parte do artigo com a API OpenAI
                final_result = None
                for chunk in article_chunks:
                    result = process_article_with_openai(chunk, prompt)
                    if result:
                        # Parse the result to check for status and criteria
                        try:
                            result_json = json.loads(result)
                            if result_json.get("STATUS") in ["Accepted", "Rejected", "Duplicated"]:
                                final_result = result_json
                                break
                        except json.JSONDecodeError:
                            print(f"Erro ao decodificar o JSON: {result}")
                            continue
                    else:
                        print(f"Erro ao processar o arquivo: {article_file}")
                        break

                if final_result:
                    print(f"Resultado para {article_file}: {final_result}")

                    # Salvar o resultado em JSON
                    output_data = {
                        "artigo": article_file,
                        "STATUS": final_result.get("STATUS"),
                        "CRITERIO": final_result.get("CRITERIO"),
                        "COMMENTS": final_result.get("COMMENTS")
                    }
                    output_path = os.path.join(output_dir, article_file.replace(".pdf", "_resultado.json"))
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, ensure_ascii=False, indent=4)
                    print(f"Resultado salvo em: {output_path}")

        print(f"Processamento concluído na pasta '{articles_dir}'.")