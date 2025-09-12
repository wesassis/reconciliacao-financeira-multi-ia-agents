# agent_orchestrator.py
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from tools import processar_reconciliacao

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Validação da chave de API
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("A chave de API do Google não foi encontrada. Defina a variável de ambiente GOOGLE_API_KEY.")

def criar_cadeia_de_reconciliacao():
    """
    Cria e configura a cadeia LangChain para análise e geração de lançamentos.
    """
    # 1. Configurar o Modelo de Linguagem (LLM)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.2)

    # 2. Definir o Prompt Template CORRIGIDO
    prompt_template = """
    Você é um assistente contábil especialista em reconciliação fiscal e contábil.
    Sua tarefa é analisar uma lista de pendências e, para cada uma, gerar um lançamento contábil de ajuste para o mês seguinte,
    junto com uma explicação clara e profissional.

    **Contexto:**
    O mês atual da análise é Agosto de 2025. Os lançamentos de ajuste devem ser datados no primeiro dia do mês seguinte (01/09/2025).
    Use as seguintes contas contábeis como padrão para os ajustes:
    - 110101 (Bancos Conta Movimento)
    - 410101 (Receita de Vendas)
    - 620101 (Despesas com Fornecedores)
    - 210101 (Fornecedores a Pagar)
    - 110201 (Clientes a Receber)
    - 999999 (Conta de Ajuste de Reconciliação) - Use esta conta para contrapartidas de ajustes de valor ou data.

    **Relatório de Pendências Recebido:**
    {report}

    **Sua Tarefa:**
    Analise cada pendência no relatório e gere uma lista de objetos JSON. Cada objeto deve conter:
    1.  `tipo_pendencia`: O tipo de pendência identificado (ex: "Divergência de Valor").
    2.  `descricao_pendencia`: Um resumo da pendência encontrada.
    3.  `lancamento_sugerido`: Um objeto JSON com a sugestão de lançamento (data, conta_debito, conta_credito, valor, historico).
    4.  `explicacao_logica`: A justificativa detalhada para o lançamento sugerido, explicando o porquê da correção.

    **Formato de Saída OBRIGATÓRIO:**
    Retorne APENAS uma lista de objetos JSON válida, dentro de um bloco de código JSON. Exemplo:
    ```json
    [
      {{
        "tipo_pendencia": "Exemplo",
        "descricao_pendencia": "Descrição do problema encontrado.",
        "lancamento_sugerido": {{
          "data": "2025-09-01",
          "conta_debito": "XXXXXX - Nome da Conta",
          "conta_credito": "YYYYYY - Nome da Conta",
          "valor": 123.45,
          "historico": "Ajuste ref. [motivo da pendência] do mês 08/2025."
        }},
        "explicacao_logica": "Esta é a explicação detalhada do motivo pelo qual este lançamento é necessário para corrigir a pendência."
      }}
    ]
    ```
    """
    
    prompt = PromptTemplate(
        input_variables=["report"],
        template=prompt_template,
    )

    # 3. Criar a Cadeia (Chain)
    chain = prompt | llm | StrOutputParser()
    
    return chain

def extrair_json_da_resposta(text: str):
    """
    Extrai o conteúdo JSON de uma string que pode conter blocos de código markdown.
    """
    try:
        # Encontra o início e o fim do bloco de código JSON
        json_block_start = text.find('```json')
        if json_block_start == -1:
             json_block_start = text.find('[')
             if json_block_start == -1: return None
        else:
             json_block_start += len('```json')
        
        json_block_end = text.rfind('```')
        if json_block_end == -1:
             json_block_end = text.rfind(']') + 1
             if json_block_end == 0: return None

        # Extrai e limpa a string JSON
        json_string = text[json_block_start:json_block_end].strip()

        # Carrega a string JSON para um objeto Python
        return json.loads(json_string)
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Erro ao decodificar JSON: {e}")
        print(f"Texto recebido: {text}")
        return None

def executar_processo_completo(path_contabil, path_fiscal):
    """
    Orquestra todo o processo: reconciliação e depois análise pela IA.
    """
    print("Iniciando a reconciliação com a ferramenta...")
    report_pendencias = processar_reconciliacao(path_contabil, path_fiscal)
    print("Relatório de pendências gerado:")
    print(report_pendencias)

    if "Nenhuma pendência encontrada" in report_pendencias:
        return []

    print("\nInvocando a cadeia de IA para análise e geração de lançamentos...")
    cadeia = criar_cadeia_de_reconciliacao()
    resposta_llm = cadeia.invoke({"report": report_pendencias})
    print("\nResposta bruta do LLM recebida.")
    
    print("\nExtraindo JSON da resposta...")
    resultado_json = extrair_json_da_resposta(resposta_llm)
    
    return resultado_json