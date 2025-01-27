# Agente ScanLit: Análise Automática de Artigos para Revisão Sistemática

## Descrição do Projeto

Este repositório contém o desenvolvimento de um agente de inteligência artificial, denominado **ScanLit**, projetado para auxiliar na análise de artigos científicos como parte de uma revisão sistemática. Este projeto integra as atividades da disciplina de **Ciência de Dados**, sendo realizado como requisito parcial para a obtenção do título de Mestre em **Engenharia Elétrica e de Computação** pela **Universidade Federal do Ceará (UFC)**.

O objetivo principal é construir um sistema automatizado capaz de avaliar e organizar artigos científicos de maneira eficiente, facilitando a condução de revisões sistemáticas em temas específicos.

---

## Temas da Revisão Sistemática

A revisão sistemática será conduzida com base nos seguintes temas:

1. **Bayesian Network-Based Probabilistic Models for Seismic Event Classification: A Systematic Review**  
   Investiga o uso de modelos probabilísticos baseados em redes Bayesianas para a classificação de eventos sísmicos.

2. **Effectiveness of Principal Component Analysis (PCA) in Dimensionality Reduction for Seismic Event Classification**  
   Analisa a eficácia da técnica de Análise de Componentes Principais (PCA) na redução de dimensionalidade para a classificação de eventos sísmicos.

3. **Analysis of the Impact of Tensor-Based vs. Vector-Based Machine Learning Methods for Seismic Event Classification**  
   Compara métodos de aprendizado de máquina baseados em tensores e vetores para a classificação de eventos sísmicos.

---

## Estrutura do Repositório

- `src/` - Código-fonte do agente **ScanLit**.
- `data/` - Base de dados utilizada para a análise dos artigos.
- `notebooks/` - Jupyter Notebooks com experimentos e análises exploratórias.
- `docs/` - Documentação detalhada do projeto.

---

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **Pandas e NumPy**: Manipulação e análise de dados.
- **Scikit-learn**: Aplicação de técnicas de aprendizado de máquina.
- **NLTK e SpaCy**: Processamento de linguagem natural para análise textual.
- **Matplotlib e Seaborn**: Visualização de dados.
- **ChatGpt API**: Automatização da extração de dados dos artigos analisados

---
## arquitetuta do projeto

.
├── dados/                    # PDFs originais
│   ├── artigo1.pdf
│   ├── artigo2.pdf
├── resumos-artigos/          # Resumos gerados pelo BLOOM-560M
│   ├── artigo1.txt
│   ├── artigo2.txt
├── resultados-openai/        # Resultados processados pela API OpenAI
│   ├── artigo1_resultado.txt
│   ├── artigo2_resultado.txt
├── scripts/                  # Scripts principais
│   ├── process_pdf.py        # Processa PDFs e extrai texto
│   ├── gerar_resumo.py       # Gera resumos utilizando BLOOM-560M
│   ├── agente_openai.py      # Gera resultados usando a API OpenAI
├── config.py                 # Configurações de variáveis de ambiente
├── .env                      # Chave da API OpenAI
├── requirements.txt          # Dependências do projeto
└── README.md                 # Documentação do projeto


---
## Fluxo de Uso

1. Coloque os PDFs na pasta dados.
2. Extraia o texto dos PDFs:

````
python scripts/process_pdf.py
````

3. Gere os resumos com o BLOOM-560M:

````
python scripts/gerar_resumo.py
````

4. Analise os resumos com a API OpenAI:

````
python scripts/agente_openai.py
````
5. Os resultados serão salvos na pasta resultados-openai.
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
- **Maria Eline Silva de Farias**  
  E-mail: elinefarias33@gmail.com


  Alterar a Política de Execução para Permitir Scripts:
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
