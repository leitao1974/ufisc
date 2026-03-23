import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Configuração da Página
st.set_page_config(page_title="Fiscalização Digital v2", layout="wide")

def extrair_texto_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()
    return texto

## --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Painel de Controlo")
    api_key = st.text_input("Google API Key:", type="password")
    
    # Seletor Dinâmico de Modelos
    model_choice = st.selectbox(
        "Escolha o Modelo:",
        ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]
    )
    
    st.info("O modelo 'Pro' é melhor para análise jurídica complexa.")
    st.divider()
    uploaded_file = st.file_uploader("Upload do Auto de Notícia (PDF)", type="pdf")

## --- CORPO DA APP ---
st.header("⚖️ Gerador de Pareceres de Fiscalização")
st.subheader("Selecione os enquadramentos aplicáveis:")

col1, col2 = st.columns(2)
with col1:
    check_ren = st.checkbox("REN - Reserva Ecológica Nacional")
    check_ran = st.checkbox("RAN - Reserva Agrícola Nacional")
    check_rjue = st.checkbox("RJUE / RJIGT (Urbanismo)")
with col2:
    check_natura = st.checkbox("Rede Natura 2000 / Áreas Protegidas")
    check_coimas = st.checkbox("Cálculo de Coimas (Lei 50/2006)")
    check_patrimonio = st.checkbox("Património Cultural (Lei 107/2001)")

if st.button("🚀 Gerar Análise Jurídica"):
    if not api_key or not uploaded_file:
        st.error("Erro: Verifique a API Key e o ficheiro PDF.")
    else:
        with st.spinner(f"A consultar legislação com {model_choice}..."):
            try:
                # 1. Extração de texto
                texto_auto = extrair_texto_pdf(uploaded_file)
                
                # 2. Configuração da IA com Chave Dinâmica
                genai.configure(api_key=api_key)
                
                # Inicialização do modelo selecionado
                model = genai.GenerativeModel(model_name=model_choice)

                # 3. Construção do Prompt com as instruções de legislação do fluxo
                contexto_legal = ""
                if check_ren:
                    contexto_legal += "- REN: DL 166/2008 + DL 123/2024. Analisar Anexo II e Art. 20º.\n"
                if check_ran:
                    contexto_legal += "- RAN: DL 73/2009 + DL 199/2015. Arts. 21º e 22º.\n"
                if check_rjue:
                    contexto_legal += "- Urbanismo: RJUE + DL 10/2024 (Simplex).\n"
                if check_coimas:
                    contexto_legal += "- Coimas: Lei 50/2006 + DL 87/2024.\n"

                prompt_final = f"""
                Age como um Jurista Especialista em Ambiente e Ordenamento em Portugal.
                Analisa o seguinte AUTO DE NOTÍCIA e gera um parecer técnico seguindo a estrutura abaixo.
                
                IMPORTANTE:
                - Consulta a legislação mais recente de 2024 mencionada nas diretrizes.
                - Se a ação NÃO se enquadra num regime, escreve apenas um parágrafo curto.
                - Se se ENQUADRA, fundamenta com artigos e alíneas.
                - Estilo: Jurídico formal (PT-PT), capítulos a **BOLD**.

                TEXTO DO AUTO:
                {texto_auto}

                DIRETRIZES LEGAIS:
                {contexto_legal}
                
                ESTRUTURA OBRIGATÓRIA:
                1. **OBJECTIVO**
                2. **DESCRIÇÃO TÉCNICA E AUDITORIA**
                3. **FUNDAMENTAÇÃO JURÍDICA E TRANSGRESSÕES**
                4. **ANÁLISE JURÍDICA DE VIABILIDADE DE LEGALIZAÇÃO**
                5. **QUADRO SANCIONATÓRIO E NULIDADES**
                6. **PARECER FINAL E MEDIDAS DE REPOSIÇÃO**
                """

                response = model.generate_content(prompt_final)
                
                st.markdown("---")
                st.markdown("### 📄 Parecer Jurídico Gerado")
                st.markdown(response.text)
                
                st.download_button("Baixar Parecer", response.text, file_name="parecer_final.txt")

            except Exception as e:
                st.error(f"Erro na IA: {str(e)}")
                st.info("Dica: Verifique se a sua API Key tem permissões para o modelo selecionado.")
