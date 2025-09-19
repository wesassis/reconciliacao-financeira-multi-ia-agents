# -*- coding: utf-8 -*-

# agent_orchestrator.py
import os
import json
from dotenv import load_dotenv
# Importações CORRIGIDAS para o SDK nativo do Google
import google.generativeai as genai
from google.generativeai import types # Esta é a linha corrigida
from tools import processar_reconciliacao

# --- Configuração Inicial ---

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Validação e configuração da chave de API para o SDK nativo
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave de API do Google não foi encontrada. Defina a variável de ambiente GEMINI_API_KEY.")

# Configura o cliente do Google GenAI
genai.configure(api_key=api_key)


def extrair_json_da_resposta(text: str):
    """
    Extrai o conteúdo JSON de uma string que pode conter blocos de código markdown.
    """
    if not text:
        return None
    try:
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

        json_string = text[json_block_start:json_block_end].strip()
        return json.loads(json_string)
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Erro ao decodificar JSON: {e}")
        print(f"Texto recebido: {text}")
        return None

def executar_processo_completo(path_contabil: str, path_fiscal: str):
    """
    Orquestra todo o processo: reconciliação e depois análise pela IA usando o SDK nativo.
    """
    print("Iniciando a reconciliação com a ferramenta...")
    report_pendencias = processar_reconciliacao(path_contabil, path_fiscal)
    print("Relatório de pendências gerado:")
    print(report_pendencias)

    if "Nenhuma pendência encontrada" in report_pendencias:
        return []

    # --- Invocação Direta da API do Gemini ---
    
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

    prompt_final = prompt_template.format(report=report_pendencias)
    
    print("\nInvocando a API do Gemini diretamente para análise e geração de lançamentos...")
    
    resposta_llm = ""
    try:
        modelo = genai.GenerativeModel('gemini-2.5-flash')
        resposta = modelo.generate_content(
            contents=prompt_final,
            generation_config=types.GenerationConfig(temperature=0.2)
        )
        resposta_llm = resposta.text
        print("\nResposta bruta do LLM recebida.")
        
    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API do Gemini: {e}")
        return None

    print("\nExtraindo JSON da resposta...")
    resultado_json = extrair_json_da_resposta(resposta_llm)
    
    return resultado_json