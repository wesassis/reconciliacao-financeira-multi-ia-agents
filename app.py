# app.py
import streamlit as st
import pandas as pd
from utils import criar_arquivos_exemplo
from agent_orchestrator import executar_processo_completo
import os
import tempfile

st.set_page_config(layout="wide", page_title="Reconciliação Contábil com IA")

st.title("🤖 Sistema de Reconciliação Contábil-Fiscal com IA Multiagente")
st.markdown("""
Esta aplicação utiliza um sistema de IA para automatizar a reconciliação entre dados contábeis e fiscais.
Faça o upload dos seus arquivos ou use os dados de exemplo para ver a mágica acontecer.
""")

# --- Sidebar para Upload e Controles ---
with st.sidebar:
    st.header("⚙️ Controles")
    
    st.subheader("1. Obtenha os Arquivos de Exemplo")
    if st.button("Gerar e Baixar Arquivos de Exemplo"):
        path_c, path_f = criar_arquivos_exemplo()
        st.success("Arquivos gerados na pasta `sample_data/`!")
        
        with open(path_c, "rb") as file:
            st.download_button(
                label="Baixar Razão Contábil Exemplo",
                data=file,
                file_name="razao_contabil_exemplo.xlsx"
            )
        with open(path_f, "rb") as file:
            st.download_button(
                label="Baixar Tabela Fiscal Exemplo",
                data=file,
                file_name="tabela_fiscal_exemplo.xlsx"
            )

    st.divider()

    st.subheader("2. Faça o Upload dos Seus Arquivos")
    uploaded_contabil = st.file_uploader("Razão Contábil (.xlsx)", type="xlsx")
    uploaded_fiscal = st.file_uploader("Tabela Fiscal (.xlsx)", type="xlsx")

# --- Área Principal para Exibição dos Resultados ---
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

if uploaded_contabil and uploaded_fiscal:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pré-visualização: Razão Contábil")
        df_contabil_preview = pd.read_excel(uploaded_contabil)
        st.dataframe(df_contabil_preview.head())
    with col2:
        st.subheader("Pré-visualização: Tabela Fiscal")
        df_fiscal_preview = pd.read_excel(uploaded_fiscal)
        st.dataframe(df_fiscal_preview.head())

    if st.button("🚀 Iniciar Reconciliação Inteligente", type="primary", use_container_width=True):
        # Salvar arquivos temporários para passar os caminhos para as ferramentas
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_c:
            tmp_c.write(uploaded_contabil.getvalue())
            path_contabil = tmp_c.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_f:
            tmp_f.write(uploaded_fiscal.getvalue())
            path_fiscal = tmp_f.name
        
        with st.spinner("A IA está analisando os dados, identificando pendências e gerando sugestões... Por favor, aguarde."):
            try:
                resultados_json = executar_processo_completo(path_contabil, path_fiscal)
                st.session_state.resultados = resultados_json
            except Exception as e:
                st.error(f"Ocorreu um erro durante o processo: {e}")
            finally:
                # Limpar arquivos temporários
                os.remove(path_contabil)
                os.remove(path_fiscal)

if st.session_state.resultados is not None:
    st.divider()
    st.header("✅ Resultados da Reconciliação")

    if not st.session_state.resultados:
        st.success("🎉 Nenhuma pendência encontrada! Seus dados estão reconciliados.")
    else:
        # Métricas
        total_pendencias = len(st.session_state.resultados)
        st.metric(label="Total de Pendências Identificadas", value=total_pendencias)
        
        st.info("Abaixo estão as pendências e os lançamentos de ajuste sugeridos pela IA. Você pode editar os dados antes de exportar.")

        # Converter resultados para um DataFrame para edição
        lancamentos_sugeridos = [res.get('lancamento_sugerido', {}) for res in st.session_state.resultados]
        df_lancamentos = pd.DataFrame(lancamentos_sugeridos)

        # Usar st.data_editor para permitir edições
        st.subheader("📝 Lançamentos de Ajuste Sugeridos (Editável)")
        df_editado = st.data_editor(df_lancamentos, num_rows="dynamic", key="editor_lancamentos")

        # Mostrar explicações para cada pendência
        st.subheader("🧠 Lógica da IA (Explicações)")
        for i, res in enumerate(st.session_state.resultados):
            with st.expander(f"**Pendência {i+1}: {res.get('tipo_pendencia')}** - {res.get('descricao_pendencia')}"):
                st.write("**Explicação:**")
                st.markdown(f"> {res.get('explicacao_logica')}")

        # Botão para exportar
        csv = df_editado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Exportar Lançamentos Aprovados para CSV",
            data=csv,
            file_name="lancamentos_de_ajuste.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    st.info("Aguardando o upload dos arquivos para iniciar a análise.")