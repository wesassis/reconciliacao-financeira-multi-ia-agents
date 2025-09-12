    # utils.py
import pandas as pd
import os

def criar_arquivos_exemplo():
    """
    Cria e salva dois arquivos Excel com dados contábeis e fiscais de exemplo,
    contendo divergências deliberadas para teste.
    """
    # Criar diretório se não existir
    if not os.path.exists('sample_data'):
        os.makedirs('sample_data')

    # --- Tabela 1: Razão Contábil ---
    dados_contabeis = {
        'ID_Lancamento': ['L101', 'L102', 'L103', 'L104', 'L105'],
        'Data': pd.to_datetime(['2025-08-05', '2025-08-10', '2025-08-12', '2025-08-20', '2025-08-25']),
        'Conta': ['110101', '620101', '110201', '410101', '620501'],
        'Descricao': [
            'Recebimento cliente A',
            'Pagamento fornecedor B',
            'Transferência entre contas',
            'Venda de produto C',
            'Pagamento conta de luz'
        ],
        'Debito': [1500.00, 250.50, 500.00, 0.00, 120.75],
        'Credito': [0.00, 0.00, 0.00, 3000.00, 0.00],
        'Valor_Absoluto': [1500.00, 250.50, 500.00, 3000.00, 120.75]
    }
    df_contabil = pd.DataFrame(dados_contabeis)
    path_contabil = 'sample_data/razao_contabil_exemplo.xlsx'
    df_contabil.to_excel(path_contabil, index=False)

    # --- Tabela 2: Tabela Fiscal ---
    # Divergências introduzidas:
    # - NF001: Valor diferente (250.50 vs 255.50)
    # - NF003: Lançamento ausente na contabilidade
    # - L104: Data diferente (20/08 vs 21/08)
    dados_fiscais = {
        'ID_Nota_Fiscal': ['NF000', 'NF001', 'NF002', 'NF003'],
        'ID_Lancamento_Ref': ['L101', 'L102', 'L104', ''], # NF003 não tem ref contábil
        'Data_Emissao': pd.to_datetime(['2025-08-05', '2025-08-10', '2025-08-21', '2025-08-28']),
        'Natureza_Operacao': ['Venda', 'Compra de Mercadoria', 'Venda', 'Serviço Contratado'],
        'Emitente_Destinatario': ['Cliente A', 'Fornecedor B', 'Cliente C', 'Fornecedor de TI D'],
        'Valor_Total': [1500.00, 255.50, 3000.00, 450.00]
    }
    df_fiscal = pd.DataFrame(dados_fiscais)
    path_fiscal = 'sample_data/tabela_fiscal_exemplo.xlsx'
    df_fiscal.to_excel(path_fiscal, index=False)
    
    return path_contabil, path_fiscal

if __name__ == '__main__':
    # Permite executar este arquivo diretamente para gerar os dados
    path_c, path_f = criar_arquivos_exemplo()
    print(f"Arquivos de exemplo criados em: {path_c} e {path_f}")