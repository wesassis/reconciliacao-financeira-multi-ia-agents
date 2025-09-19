# Reconciliação Financeira com Agentes de IA

## Visão Geral

Este projeto apresenta um sistema de reconciliação contábil-fiscal automatizado, desenvolvido com Streamlit e agentes de Inteligência Artificial. O objetivo principal é simplificar e agilizar o processo de identificação de divergências entre dados contábeis e fiscais, oferecendo sugestões de ajustes e explicações lógicas para as pendências encontradas. A aplicação é projetada para ser intuitiva e eficiente, permitindo que usuários façam o upload de seus arquivos e obtenham uma análise detalhada com o suporte de IA.

## Estrutura do Projeto

O repositório está organizado da seguinte forma:

- `sample_data/`: Contém arquivos de exemplo para demonstração das funcionalidades.
- `agent_orchestrator.py`: Módulo responsável pela orquestração dos agentes de IA no processo de reconciliação.
- `app.py`: O arquivo principal da aplicação Streamlit, que define a interface do usuário e integra as funcionalidades.
- `requirements.txt`: Lista as dependências necessárias para executar o projeto.
- `tools.py`: Define as ferramentas que os agentes de IA podem utilizar.
- `utils.py`: Contém funções utilitárias para o projeto, como a criação de arquivos de exemplo.

## Instalação

Para configurar e executar o projeto localmente, siga os passos abaixo:

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/wesassis/reconciliacao-financeira-multi-ia-agents.git
    cd reconciliacao-financeira-multi-ia-agents
    ```

2.  **Crie um ambiente virtual (recomendado):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

    As dependências incluem:
    - `streamlit`: Para a construção da interface web.
    - `pandas`: Para manipulação e análise de dados.
    - `openpyxl`: Para leitura e escrita de arquivos Excel.
    - `python-dotenv`: Para gerenciar variáveis de ambiente.
    - `google-generativeai`: Para integração com modelos de IA da Google.
    - `langchain`: Framework para desenvolvimento de aplicações com LLMs.
    - `langchain-google-genai`: Integração do LangChain com a API Generative AI da Google.

4.  **Configure as variáveis de ambiente:**

    Crie um arquivo `.env` na raiz do projeto e adicione sua chave de API da Google Generative AI:

    ```
    GEMENI_API_KEY="SUA_CHAVE_API_AQUI"
    ```

## Uso

Para iniciar a aplicação Streamlit, execute o seguinte comando no terminal:

```bash
streamlit run app.py
```

Após a execução, a aplicação será aberta em seu navegador padrão. Você poderá:

- Gerar e baixar arquivos de exemplo para testar a funcionalidade.
- Fazer o upload de seus próprios arquivos Excel (Razão Contábil e Tabela Fiscal).
- Iniciar o processo de reconciliação inteligente, que utilizará a IA para analisar os dados.
- Visualizar as pendências identificadas, as explicações lógicas e os lançamentos de ajuste sugeridos.
- Editar os lançamentos sugeridos e exportá-los para um arquivo CSV.

## Tecnologias Utilizadas

- **Streamlit**: Framework para criação rápida de aplicações web interativas em Python.
- **Pandas**: Biblioteca para manipulação e análise de dados.
- **Google Generative AI**: Modelos de inteligência artificial para análise e geração de insights.
- **LangChain**: Framework para construir aplicações baseadas em modelos de linguagem.
- **Python-dotenv**: Para carregamento de variáveis de ambiente.



