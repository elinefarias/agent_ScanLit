import os
import openai
import pdfplumber
import time
from config import OPENAI_API_KEY

# Configurar a API OpenAI
openai.api_key = OPENAI_API_KEY

def extract_text_from_pdf(pdf_path):
    """
    Extrai o texto de um arquivo PDF usando pdfplumber.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def process_article_with_openai(article_content, prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em leitura e análise de artigos científicos."},
                {"role": "user", "content": f"{prompt}\n\n{article_content}"}
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except openai.error.OpenAIError as e:
        print(f"Erro ao chamar a API OpenAI: {e}")
        return None

def split_text(text, max_tokens=9000):
    """
    Divide o texto em partes menores respeitando o limite de tokens.
    """
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
            current_tokens = sentence_tokens
        else:
            current_chunk += sentence + ". "
            current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

if __name__ == "__main__":
    base_dir = "artigos"
    output_base_dir = "resultados-extracao"
    subdirs = ["IEEE", "WebOfScience"]

    for subdir in subdirs:
        articles_dir = os.path.join(base_dir, subdir)
        output_dir = os.path.join(output_base_dir, f"resultados-analise-extracao-{subdir}")
        os.makedirs(output_dir, exist_ok=True)

        if not os.path.exists(articles_dir):
            print(f"Erro: O diretório '{articles_dir}' não foi encontrado.")
            continue

        # Prompt para direcionar a análise
        prompt = (
            "Objetivo: Classificar resumos de artigos de acordo com as informações especificas definidas nas solicitações contidas em <solicitacoes>. "
            "<solicitacoes>"
            "1 - OBJETIVOS - Identificação dos Objetivos: Realize uma análise cuidadosa do conteúdo do trabalho para extrair os objetivos principais. Resuma esses objetivos em um parágrafo claro e conciso, capturando a essência das metas e intenções do estudo. Número de palavras até 60 ou maior do que 39."
            "2 - GAP - Identificação do GAP: Analise o conteúdo do trabalho para identificar o GAP científico que ele aborda, mesmo que não esteja explicitamente mencionado. Formule um parágrafo conciso, focando em destacar a questão central que o estudo procura resolver ou elucidar. Número de palavras até 60 ou maior do que 39."
            "3 - METODOLOGIA - Extração Detalhada da Metodologia do Trabalho: Identificação e Descrição da Metodologia: Proceda com uma análise minuciosa do trabalho para identificar a metodologia utilizada. Detalhe cada aspecto da metodologia, incluindo o desenho do estudo, as técnicas e ferramentas empregadas. Número de palavras até 60 ou maior do que 39."
            "4 - RESULTADOS - Escreva em um parágrafo os resultados obtidos estudo dando ênfase a dados quantitativos, quero dados numéricos explicitamente. Nesse parágrafo também de ênfase a comparação ao melhor trabalho anterior em relação ao trabalho proposto. Não use superlativos. Deixe o tom neutro e científico. Número de palavras até 60 ou maior do que 39."
            "5 - CONCLUSÃO - Resuma as conclusões dos autores em relação ao trabalho. Número de palavras até 60 ou maior do que 30."
            "6 - AVALIAÇÃO - Faça uma avalição crítica ao trabalho. Não seja generalista faça uma crítica aprofundada. Número de palavras até 60 ou maior do que 39."
            "7 - AUTORES - Extraia o nome dos autores."
            "8 - TÍTULO - Extraia o título do artigo."
            "9 - ANO - Extraia o ano de publicação do artigo."
            "10 - REVISTA OU PERIÓDICO - Extraia o nome da revista ou periódico onde o artigo foi publicado."
            "11 - PAÍS - Extraia o nome do país de origem do artigo."
            "12 - VARIÁVEL PRIMÁRIA 1 - Extraia o valor da variável primária antes da intervenção do estudo de acordo com as orientações em <variavel>, tentar extrair informações relacionadas ao conjunto de dados utilizado e métricas analisadas para verificar se há alguma inferência possível, se não encontrar, ler novamente o documento até encontrar. De preferência em números."
            "13 - VARIÁVEL PRIMÁRIA 2 - Extraia o valor da variável primária após a intervenção do estudo de acordo com as orientações em <variavel>, tentar extrair informações relacionadas ao conjunto de dados utilizado e métricas analisadas para verificar se há alguma inferência possível, se não encontrar, ler novamente o documento até encontrar. De preferência em números."
            "14 - TAMANHO DA AMOSTRA - Extraia o tamanho em números, se possível, da amostra do estudo, tentar extrair informações relacionadas ao conjunto de dados utilizado e métricas analisadas para verificar se há alguma inferência possível, se não encontrar, ler novamente o documento até encontrar. De preferência em números."
            "</solicitacoes>"

            "<variavel>"
            "Variável primária"
           "A variável primária (ou desfecho primário) é o principal parâmetro que um estudo ou análise busca medir ou avaliar para responder à sua pergunta de pesquisa. É a variável mais importante para determinar se a intervenção ou condição investigada teve o efeito esperado."
            "Características da Variável Primária"
            "1. Centralidade: É a métrica central do estudo, usada para avaliar o sucesso ou a falha da intervenção."
            "2. Objetiva: Deve ser mensurável e bem definida para evitar ambiguidades."
            "3. Relevância: Relaciona-se diretamente com o objetivo principal do estudo."
            "4. Planejamento Prévio: É definida antes do início da coleta de dados para evitar vieses."

            "Exemplo Prático de variável primária:"  
            "No estudo comparativo sobre métodos de aprendizado de máquina para classificação de eventos sísmicos, a variável primária foi:"  
            "Acurácia da classificação de eventos sísmicos utilizando modelos baseados em tensores e vetores."  
            "Por quê? Porque a acurácia é uma métrica fundamental para avaliar a eficácia de diferentes abordagens de aprendizado de máquina na identificação de eventos sísmicos. O desempenho dos métodos baseados em tensores foi comparado com os métodos tradicionais baseados em vetores para determinar qual técnica proporciona uma classificação mais precisa e eficiente."  

            "Importância"
            "Definir a variável primária é crucial, pois:"
            "Se houver mais de um objetivo no estudo, podem ser definidas variáveis secundárias, que fornecem informações adicionais, mas não são o foco principal."

            "importante"
            "Caso a variável primária não esteja claramente especificada no artigo: Tente identificar qualquer informação relacionada ao impacto ou à métrica central do estudo. "
            "Se não conseguir encontrar o valor da variável tente novamente até encontrar."
            "Se não existir realmente, prossiga para os próximos passos."

            "</variavel>"

            "<template>"
            " 'artigo': 'nome do arquivo.pdf',"
            " 'TÍTULO': 'Título do artigo',"
            " 'AUTORES': 'Nome dos autores',"
            " 'ANO:' 'Ano de publicação do artigo',"
            " 'REVISTA OU PERIÓDICO:' 'Nome da revista ou periódico',"
            " 'PAÍS:' 'País de origem do artigo',"
            " 'OBJETIVOS:' 'Objetivo geral e específicos',"
            " 'GAP:' 'Gap científico',"
            " 'METODOLOGIA:' 'Metodologia',"
            " 'RESULTADOS:' 'Resultados do artigo',"
            " 'CONCLUSÃO:' 'Conclusões',"
            " 'AVALIAÇÃO:' 'Análise do artigo',"
            " 'AMOSTRA:' 'Tamano da amostra',"
            " 'VARIAVEL PRIMARIA 1:' 'Valor da variável primária antes da intervenção do estudo',"
            " 'VARIAVEL PRIMARIA 2:' 'Valor da variável primária após a da intervenção do estudo',"
            "</template>"
            "Backstory = Você é um especialista em leitura e análise de artigos científicos. Sua missão é extrair informações cruciais, compreendendo o contexto semântico completo dos artigos. Sua função é fundamental para avaliar a relevância dos artigos analisados. Ao responder as solicitações delimitadas por <solicitacoes>, você deve levar em consideração as definições de controles em <controle> e as restrições em <restricoes>."
            "<controle>"
            "NÍVEIS DE CONTROLE:"
            "1. Entonação: Formal Científico."
            "2. Foco de Tópico: Você deve responder sempre com alto foco no texto do artigo científico."
            "3. Língua: Responda sempre em Português do Brasil como os Brasileiros costumam escrever textos científicos aderindo aos padrões de redação científica do país a não ser o que será especificado para não traduzir."
            "4. Controle de Sentimento: Neutro e científico. Evite superlativos como: inovador, revolucionário e etc. 5. Nível Originalidade: 10, onde 1 é pouco original e 10 é muito original. Em hipótese alguma copie frases do texto original."
            "6. Nível de Abstração: 1, onde 1 é muito concreto e real e 10 é muito abstrato e irreal."
            "7. Tempo Verbal: Escreva no passado."
            "</controle>"
            "<restricoes>"
            "O que não deve ser traduzido do inglês para o português brasileiro:"
            "1. Termos técnicos em inglês amplamente aceitos e usado nos textos em português."
            "2. Nome de algoritmos de machine learning."
            "3. Métricas usadas no trabalho."
            "</restricoes>"
            "Tarefa = Leia os PDFs que contém os artigos e responda em JSON às solicitações definidas em <solicitacoes> usando o modelo definido em <template>. Saída esperada = JSON com as respostas às solicitações definidas em <solicitacoes>, usando o modelo definido em <template>."
        )

        print(f"Iniciando processamento dos artigos na pasta '{articles_dir}'...")

        for article_file in os.listdir(articles_dir):
            if article_file.endswith(".pdf"):
                article_path = os.path.join(articles_dir, article_file)

                # Extrair texto do PDF
                article_content = extract_text_from_pdf(article_path)

                if not article_content:
                    print(f"Erro: Não foi possível extrair texto do PDF {article_file}. Verifique o formato do arquivo.")
                    continue

                # Dividir o conteúdo do artigo em partes menores
                article_chunks = split_text(article_content)

                # Processar cada parte do artigo com a API OpenAI
                final_result = ""

                for chunk in article_chunks:
                    result = process_article_with_openai(chunk, prompt)
                    time.sleep(1)  # Adiciona uma pausa para evitar rate limit

                    if result:
                        final_result += result + "\n"
                    else:
                        print(f"Erro ao processar o arquivo: {article_file}")
                        break

                if final_result:
                    print(f"Resultado bruto para {article_file}: {final_result}")

                    # Salvar o resultado em um arquivo .txt
                    output_filename = article_file.replace(".pdf", "_resultado.txt")
                    output_path = os.path.join(output_dir, output_filename)

                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(final_result)
                    print(f"Resultado salvo em: {output_path}")

        print(f"Processamento concluído na pasta '{articles_dir}'.")