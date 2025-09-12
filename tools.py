# tools.py
import pandas as pd

def processar_reconciliacao(arquivo_contabil_path: str, arquivo_fiscal_path: str) -> str:
    """
    Ferramenta completa que carrega, limpa, reconcilia e identifica pendências
    entre dados contábeis e fiscais de arquivos Excel.

    Args:
        arquivo_contabil_path (str): Caminho para o arquivo Excel do razão contábil.
        arquivo_fiscal_path (str): Caminho para o arquivo Excel da tabela fiscal.

    Returns:
        str: Uma string formatada em markdown com o resumo das pendências encontradas,
             pronta para ser usada no prompt do LLM.
    """
    try:
        # --- 1. Carregar e Limpar Dados ---
        df_contabil = pd.read_excel(arquivo_contabil_path)
        df_fiscal = pd.read_excel(arquivo_fiscal_path)

        # Padronização de colunas (exemplo)
        df_contabil.rename(columns={'ID_Lancamento': 'ID_Ref'}, inplace=True)
        df_fiscal.rename(columns={'ID_Lancamento_Ref': 'ID_Ref'}, inplace=True)
        
        # Garantir que a chave de merge não seja nula
        df_contabil['ID_Ref'] = df_contabil['ID_Ref'].astype(str)
        df_fiscal['ID_Ref'] = df_fiscal['ID_Ref'].astype(str)
        
        # --- 2. Reconciliação Inteligente ---
        # Cruzar dados usando o ID de Referência como chave principal
        reconciliacao_df = pd.merge(
            df_contabil,
            df_fiscal,
            on='ID_Ref',
            how='outer',
            suffixes=('_contabil', '_fiscal'),
            indicator=True
        )

        # --- 3. Identificar Pendências ---
        pendencias = []

        # Pendência 1: Lançamento apenas na Contabilidade
        apenas_contabil = reconciliacao_df[reconciliacao_df['_merge'] == 'left_only']
        for _, row in apenas_contabil.iterrows():
            pendencias.append(
                f"- Tipo: Lançamento Apenas na Contabilidade\n"
                f"  ID_Ref: {row['ID_Ref']}\n"
                f"  Data: {row['Data']}\n"
                f"  Valor: {row['Valor_Absoluto']}\n"
                f"  Descrição: {row['Descricao']}\n"
            )

        # Pendência 2: Lançamento apenas Fiscal
        apenas_fiscal = reconciliacao_df[reconciliacao_df['_merge'] == 'right_only']
        for _, row in apenas_fiscal.iterrows():
            pendencias.append(
                f"- Tipo: Lançamento Apenas na Tabela Fiscal\n"
                f"  ID_Nota_Fiscal: {row['ID_Nota_Fiscal']}\n"
                f"  Data: {row['Data_Emissao']}\n"
                f"  Valor: {row['Valor_Total']}\n"
                f"  Descrição: {row['Natureza_Operacao']} - {row['Emitente_Destinatario']}\n"
            )

        # Pendência 3 e 4: Divergência de Valor e Data para lançamentos correspondentes
        correspondentes = reconciliacao_df[reconciliacao_df['_merge'] == 'both']
        for _, row in correspondentes.iterrows():
            # Checar divergência de valor
            if abs(row['Valor_Absoluto'] - row['Valor_Total']) > 0.01: # Tolerância
                pendencias.append(
                    f"- Tipo: Divergência de Valor\n"
                    f"  ID_Ref: {row['ID_Ref']}\n"
                    f"  Valor Contábil: {row['Valor_Absoluto']}\n"
                    f"  Valor Fiscal: {row['Valor_Total']}\n"
                    f"  Descrição: {row['Descricao']}\n"
                )
            
            # Checar divergência de data
            if pd.to_datetime(row['Data']).date() != pd.to_datetime(row['Data_Emissao']).date():
                pendencias.append(
                    f"- Tipo: Divergência de Data\n"
                    f"  ID_Ref: {row['ID_Ref']}\n"
                    f"  Data Contábil: {row['Data'].date()}\n"
                    f"  Data Fiscal: {row['Data_Emissao'].date()}\n"
                    f"  Descrição: {row['Descricao']}\n"
                )

        if not pendencias:
            return "Nenhuma pendência encontrada. A reconciliação foi bem-sucedida."

        # --- 4. Formatar Saída para o LLM ---
        resultado_formatado = "## Relatório de Pendências de Reconciliação\n\n"
        resultado_formatado += "\n\n".join(pendencias)
        return resultado_formatado

    except Exception as e:
        return f"Erro ao processar os arquivos: {str(e)}"