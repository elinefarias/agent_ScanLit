# Agente ScanLit: Análise Automática de Artigos para Revisão Sistemática

## Descrição do Projeto

Este repositório contém o desenvolvimento de um agente de inteligência artificial, denominado **ScanLit**, projetado para auxiliar na análise de artigos científicos como parte de uma revisão sistemática. Este projeto integra as atividades da disciplina de **Ciência de Dados**, sendo realizado como requisito parcial para a obtenção do título de Mestre em **Engenharia Elétrica e de Computação** pela **Universidade Federal do Ceará (UFC)**.

O objetivo principal é construir um sistema automatizado capaz de avaliar e organizar artigos científicos de maneira eficiente, facilitando a condução de revisões sistemáticas em temas específicos.

---

## Temas da Revisão Sistemática

A revisão sistemática será conduzida com base no seguinte tema:

**Analysis of the Impact of Tensor-Based vs. Vector-Based Machine Learning Methods for Seismic Event Classification**  
   Compara métodos de aprendizado de máquina baseados em tensores e vetores para a classificação de eventos sísmicos.

---

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **Pandas e NumPy**: Manipulação e análise de dados.
- **Scikit-learn**: Aplicação de técnicas de aprendizado de máquina.
- **NLTK e SpaCy**: Processamento de linguagem natural para análise textual.
- **Matplotlib e Seaborn**: Visualização de dados.
- **OpenAI API**: Geração de resumos e análise de textos.
- **Hugging Face API**: Modelos de linguagem para processamento de texto.
- **ollama**: Execução de LLMs (Large Language Models).

---

## Arquitetura do Projeto

.
├── dados/                       # PDFs originais
│   ├── artigo1.pdf
│   ├── artigo2.pdf
├── resumos-artigos/             # Resumos gerados pelo BLOOM-560M
│   ├── artigo1.txt
│   ├── artigo2.txt
├── resultados
│   ├── artigo1_resultado.txt
│   ├── artigo2_resultado.txt
├── scripts/                     # Scripts principais
│   ├── process_pdf.py       
│   ├── gerar_resumo.py       
│   ├── avaliacao-qualitativa-artigos.py
│   ├── classificacao-artigos.py
│   ├── extracao-dados-artigos.py
├── meta-analise/                # notebooks para aplicar uma meta-análise
│   ├── meta_analise.ipynb
|   ├── resultados-meta-analise           
├── config.py                    # Configurações de variáveis de ambiente
├── .env                         # Chave da API OpenAI
├── .gitignore                   # Arquivos ignorados pelo Git
├── LICENSE                      # Licença do projeto
├── main.py                      # Script principal
├── requirements.txt             # Dependências do projeto
└── README.md                    # Documentação do projeto

---

## Fluxo de Uso

1. Coloque os PDFs na pasta dados.
2. Extraia o texto dos PDFs:

````bash
python scripts/process_pdf.py
````

3. Gere os resumos com o BLOOM-560M:

````bash
python scripts/gerar_resumo.py
````

4. Analise os resumos com a API OpenAI:

````bash
python scripts
````

5. Os resultados serão salvos na pasta resultados.

---

## Configuração de Chaves de API

Para testar os scripts do projeto, é necessário adicionar as chaves da API OpenAI e do Hugging Face no arquivo `.env`:

````properties
HUGGINGFACE_API_KEY='sua_chave_huggingface'
OPENAI_API_KEY='sua_chave_openai'
````

---

## Scripts Disponíveis

- **process_pdf.py**: Processa PDFs e extrai texto.
- **gerar_resumo.py**: Gera resumos utilizando BLOOM-560M.
- **avaliacao-qualitativa-artigos.py**: avaliar qualitativamente os artigos a partir de um questionario usando a API OpenAI.
- **classificacao-artigos.py**: classificar artigos baseados em criterios de inclusão e exclusão pré-definidos usando a API OpenAI.
- **extracao-dados-artigos.py** ou **main.py**: extracao de informações para aplicar uma meta-análise usando a API OpenAI.

---

## Como Contribuir

1. Faça um fork deste repositório.
2. Crie uma branch para sua funcionalidade ou correção: `git checkout -b feature/nova-funcionalidade`.
3. Faça commit das alterações: `git commit -m 'Descrição clara do que foi feito'`.
4. Faça push para a branch: `git push origin feature/nova-funcionalidade`.
5. Abra um Pull Request para análise.

---

## Contato

Para dúvidas ou sugestões, entre em contato com:
E-mail: elinefarias33@gmail.com