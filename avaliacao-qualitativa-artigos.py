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
    output_base_dir = "resultados-analise-qualidade"
    subdirs = ["IEEE", "WebOfScience"]

    for subdir in subdirs:
        articles_dir = os.path.join(base_dir, subdir)
        output_dir = os.path.join(output_base_dir, f"resultados-analise-qualidade-{subdir}")
        os.makedirs(output_dir, exist_ok=True)

        if not os.path.exists(articles_dir):
            print(f"Erro: O diretório '{articles_dir}' não foi encontrado.")
            continue

        # Prompt para direcionar a análise
        prompt = (
            "Objetivo: Ler os documentos, cruzar os dados e aplicar um questionário de qualidade de acordo com as informações específicas definidas nas solicitações contidas em <solicitacoes>"
            "Descrição: Esta revisão sistemática examina o impacto dos métodos de aprendizado de máquina baseados em tensores na classificação de eventos sísmicos, comparando-os com abordagens tradicionais baseadas em vetores. "
            "Dada a complexidade e a natureza multidimensional dos dados sísmicos, os métodos baseados em tensores oferecem o potencial para capturar relações intrincadas de forma mais eficaz, levando potencialmente a uma melhor precisão de classificação e a uma compreensão mais profunda dos fenômenos sísmicos."
            "<Pergunta de pesquisa>"
            " Como os métodos de aprendizado de máquina baseados em tensores se comparam aos métodos baseados em vetores na classificação de eventos sísmicos em termos de precisão e eficiência?"
            "</Pergunta de pesquisa>"
            "Gere um JSON com os campos especificados. "
            "<solicitacoes>"
            "1 - TÍTULO: Extraia o título do artigo."
            "2 - ANO: Extraia o ano de publicação do artigo."
            "3 -  PERGUNTAS:"
            "   - Analise os arquivos contendo os artigo."
            "   - Responda às perguntas de qualidade conforme descritas em <perguntas>"
            "   - Em caso de dúvida, considere os objetivos da pesquisa descritos em <objetivos>"
            "</solicitacoes>"
            "<template>"
            "{" 
                " 'artigo': 'nome do arquivo.pdf',"
                " 'TÍTULO': 'Título do artigo',"
                " 'ano': 'Ano de publicação do artigo',"
                " 'O estudo possui uma descrição clara dos objetivos e da pergunta de pesquisa?': 'Sim/Parcialmente/Não',"
                " 'Os dados sísmicos utilizados são descritos detalhadamente (ex.: origem, características, pré-processamento)?': 'Sim/Parcialmente/Não',"
                " 'Os métodos de aprendizado de máquina (baseados em tensores e/ou vetores) são bem explicados e justificam sua escolha?': 'Sim/Parcialmente/Não',"
                " 'O estudo compara diretamente métodos baseados em tensores e métodos baseados em vetores?': 'Sim/Parcialmente/Não',"
                " 'As métricas de desempenho são bem definidas e apropriadas para a avaliação da classificação sísmica?': 'Sim/Parcialmente/Não',"
                " 'O estudo inclui análise estatística ou técnicas de validação adequadas para avaliar a robustez dos resultados?': 'Sim/Parcialmente/Não',"
                " 'As limitações do estudo são discutidas de forma clara e transparente?': 'Sim/Parcialmente/Não',"
                " 'O estudo apresenta reprodutibilidade, fornecendo detalhes suficientes sobre os métodos e os dados utilizados?': 'Sim/Parcialmente/Não',"
                " 'O artigo foi publicado em uma fonte confiável (periódico ou conferência revisado por pares)?': 'Sim/Parcialmente/Não',"
                " 'As conclusões do estudo são coerentes com os resultados apresentados?': 'Sim/Parcialmente/Não',"
            "}"
            "</template>"
            "<perguntas>"
            "Quality Assessment Checklist:"
            "1. O estudo possui uma descrição clara dos objetivos e da <Pergunta de pesquisa>"
            "2. Os dados sísmicos utilizados são descritos detalhadamente (ex.: origem, características, pré-processamento)?"
            "3. Os métodos de aprendizado de máquina (baseados em tensores e/ou vetores) são bem explicados e justificam sua escolha?"
            "4. O estudo compara diretamente métodos baseados em tensores e métodos baseados em vetores?"
            "5. As métricas de desempenho são bem definidas e apropriadas para a avaliação da classificação sísmica?"
            "6. O estudo inclui análise estatística ou técnicas de validação adequadas para avaliar a robustez dos resultados?"
            "7. As limitações do estudo são discutidas de forma clara e transparente?"
            "8. O estudo apresenta reprodutibilidade, fornecendo detalhes suficientes sobre os métodos e os dados utilizados?"
            "9. O artigo foi publicado em uma fonte confiável (periódico ou conferência revisado por pares)?"
            "10. As conclusões do estudo são coerentes com os resultados apresentados?"
            "Opções de resposta:"
            "1. Sim"
            "2. Parcialmente"
            "3. Não"
            "</perguntas>"
            "<objetivos>"
            "Objetivos da Revisão Sistemática:"
            "1. Investigar o impacto dos métodos de aprendizado de máquina baseados em tensores na classificação de eventos sísmicos, em comparação com abordagens baseadas em vetores."
            "2. Analisar a precisão e a eficiência dos métodos baseados em tensores na captura de relações multidimensionais em dados sísmicos."
            "3. Identificar as principais aplicações, desafios e avanços recentes no uso de técnicas baseadas em tensores para análise de eventos sísmicos."
            "4. Avaliar a robustez e a escalabilidade dos modelos baseados em tensores em diferentes contextos de dados sísmicos."
            "5. Sintetizar as evidências disponíveis na literatura para orientar futuras pesquisas sobre a utilização de aprendizado de máquina na classificação de eventos sísmicos."
            "</objetivos>"
            "Backstory"
            "Você é um especialista em leitura e análise de artigos científicos. Sua missão é extrair informações cruciais, compreendendo o contexto semântico completo dos artigos. Sua função é fundamental para avaliar a relevância dos artigos analisados. Ao responder as solicitações delimitadas por <solicitacoes>, você deve levar em consideração as definições de controle em <controle> e as restrições em <restricoes>."
            "<controle>"
            "NÍVEIS DE CONTROLE:"
            "1. Entonação: Formal Científico."
            "2. Foco de Tópico: Sempre com alto foco no texto do artigo científico."
            "3. Língua: Responda sempre em Português do Brasil, aderindo aos padrões de redação científica do país, exceto quando especificado para não traduzir."
            "4. Controle de Sentimento: Neutro e científico. Evite superlativos como: inovador, revolucionário, etc."
            "5. Nível de Originalidade: 10, onde 1 é pouco original e 10 é muito original. Em hipótese alguma copie frases do texto original."
            "6. Nível de Abstração: 1, onde 1 é muito concreto e real e 10 é muito abstrato e irreal."
            "7. Tempo Verbal: Escreva no passado."
            "</controle>"
            "<restricoes>"
            "O que não deve ser traduzido do inglês para o português brasileiro:"
            "1. Termos técnicos em inglês amplamente aceitos e usados nos textos em português."
            "2. Nome de algoritmos de machine learning."
            "3. Métricas usadas no trabalho."
            "</restricoes>"
            "Tarefa = Leia os artigos e responda em JSON às solicitações definidas em <solicitacoes>, usando o modelo definido em <template>."
        )

        print(f"Iniciando processamento dos artigos na pasta '{articles_dir}'...")

        for article_file in os.listdir(articles_dir):
            if article_file.endswith(".pdf"):
                article_path = os.path.join(articles_dir, article_file)

                # Extrair texto do PDF
                article_content = extract_text_from_pdf(article_path)

                # Dividir o conteúdo do artigo em partes menores
                article_chunks = split_text(article_content)

                # Processar cada parte do artigo com a API OpenAI
                final_result = None

                for chunk in article_chunks:
                    result = process_article_with_openai(chunk, prompt)
                    if result:
                        # Adiciona um print para exibir o resultado antes de tentar decodificar o JSON
                        print(f"Resultado bruto para {article_file}: {result}")
                        # Remove as marcações de bloco de código Markdown
                        result = result.strip("```json").strip("```").strip()
                        try:
                            result_json = json.loads(result)
                            final_result = result_json
                            break
                        except json.JSONDecodeError as e:
                            print(f"Erro ao decodificar o JSON: {e}")
                            continue
                    else:
                        print(f"Erro ao processar o arquivo: {article_file}")
                        break

                if final_result:
                    #print(f"Resultado para {article_file}: {final_result}")

                    # Salvar o resultado em JSON
                    output_data = {
                        "artigo": article_file,
                        "titulo": final_result.get("TÍTULO"),	
                        "ano": final_result.get("ano"),
                        "O estudo possui uma descrição clara dos objetivos e da pergunta de pesquisa?": final_result.get("O estudo possui uma descrição clara dos objetivos e da pergunta de pesquisa?"),
                        "Os dados sísmicos utilizados são descritos detalhadamente (ex.: origem, características, pré-processamento)?": final_result.get("Os dados sísmicos utilizados são descritos detalhadamente (ex.: origem, características, pré-processamento)?"),
                        "Os métodos de aprendizado de máquina (baseados em tensores e/ou vetores) são bem explicados e justificam sua escolha?": final_result.get("Os métodos de aprendizado de máquina (baseados em tensores e/ou vetores) são bem explicados e justificam sua escolha?"),
                        "O estudo compara diretamente métodos baseados em tensores e métodos baseados em vetores?": final_result.get("O estudo compara diretamente métodos baseados em tensores e métodos baseados em vetores?"),
                        "As métricas de desempenho são bem definidas e apropriadas para a avaliação da classificação sísmica?": final_result.get("As métricas de desempenho são bem definidas e apropriadas para a avaliação da classificação sísmica?"),
                        "O estudo inclui análise estatística ou técnicas de validação adequadas para avaliar a robustez dos resultados?": final_result.get("O estudo inclui análise estatística ou técnicas de validação adequadas para avaliar a robustez dos resultados?"),
                        "As limitações do estudo são discutidas de forma clara e transparente?": final_result.get("As limitações do estudo são discutidas de forma clara e transparente?"),
                        "O estudo apresenta reprodutibilidade, fornecendo detalhes suficientes sobre os métodos e os dados utilizados?": final_result.get("O estudo apresenta reprodutibilidade, fornecendo detalhes suficientes sobre os métodos e os dados utilizados?"),
                        "O artigo foi publicado em uma fonte confiável (periódico ou conferência revisado por pares)?": final_result.get("O artigo foi publicado em uma fonte confiável (periódico ou conferência revisado por pares)?"),
                        "As conclusões do estudo são coerentes com os resultados apresentados?": final_result.get("As conclusões do estudo são coerentes com os resultados apresentados?")
                    }
    
                    # Adiciona o print para exibir a saída gerada pelo agente
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% saida agente %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                    print(f"Saída gerada pelo agente para {article_file}: {json.dumps(output_data, ensure_ascii=False, indent=4)}")
                    
                     # Simplificar o nome do arquivo de saída
                    output_filename = article_file.replace(".pdf", "_resultado.json")
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # Garantir que o diretório de saída exista
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, ensure_ascii=False, indent=4)
                    print(f"Resultado salvo em: {output_path}")

        print(f"Processamento concluído na pasta '{articles_dir}'.")