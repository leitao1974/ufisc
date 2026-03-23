import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Configuração da Página
st.set_page_config(page_title="Fiscalização Digital v2", layout="wide", page_icon="⚖️")

def extrair_texto_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()
    return texto

## --- SIDEBAR: CONFIGURAÇÕES DINÂMICAS ---
with st.sidebar:
    st.title("⚙️ Configurações")
    api_key = st.text_input("Introduza a sua Google API Key:", type="password")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Lista modelos disponíveis para esta chave específica
            available_models = [m.name.replace('models/', '') for m in genai.list_models() 
                                if 'generateContent' in m.supported_generation_methods]
            model_choice = st.selectbox("Selecione o Modelo Disponível:", available_models)
        except Exception as e:
            st.error(f"Erro ao validar chave: {e}")
            model_choice = "gemini-1.5-pro" # Fallback
    else:
        st.warning("Insira a API Key para listar os modelos.")
        model_choice = "gemini-1.5-pro"

    st.divider()
    uploaded_file = st.file_uploader("Upload do Auto de Notícia (PDF)", type="pdf")

## --- CORPO DA APP ---
st.header("⚖️ Sistema de Apoio à Fiscalização")
st.info("A IA consultará a legislação mais recente (2024) conforme o seu fluxo de trabalho.")

# Seleção de Regimes conforme o Diagrama
st.subheader("Enquadramentos Jurídicos")
c1, c2, c3 = st.columns(3)
with c1:
    check_ren = st.checkbox("REN (DL 166/2008 + DL 123/2024)")
    check_ran = st.checkbox("RAN (DL 73/2009 + DL 199/2015)")
with c2:
    check_natura = st.checkbox("Rede Natura 2000")
    check_patrimonio = st.checkbox("Património (Lei 107/2001)")
with c3:
    check_rjue = st.checkbox("Ordenamento/Urbanismo (RJUE)")
    check_coimas = st.checkbox("Coimas (Lei 50/2006 + DL 87/2024)")

if st.button("🚀 Gerar Parecer Jurídico"):
    if not api_key or not uploaded_file:
        st.error("⚠️ Falta a API Key ou o ficheiro PDF.")
    else:
        with st.spinner(f"A analisar com {model_choice}..."):
            try:
                texto_auto = extrair_texto_pdf(uploaded_file)
                
                # Configuração do Modelo selecionado dinamicamente
                model = genai.GenerativeModel(model_name=f"models/{model_choice}")

                # Construção das Instruções Legais Dinâmicas
                diretrizes = []
                if check_ren: diretrizes.append("REN: DL 166/2008, DL 124/2019 e a atualização do DL 123/2024. Citar Anexo II e Art. 20º.")
                if check_ran: diretrizes.append("RAN: DL 73/2009 e DL 199/2015. Transcrever alíneas do Art. 21º ou 22º.")
                if check_rjue: diretrizes.append("Urbanismo: RJUE (DL 555/99) e o novo Simplex Urbanístico (DL 10/2024).")
                if check_coimas: diretrizes.append("Contraordenações: Lei 50/2006 com as alterações do DL 87/2024.")

                prompt_final = f"""
                Age como um Jurista Sénior em Portugal (PT-PT).
                Analisa o texto do AUTO DE NOTÍCIA e gera um parecer com base na seguinte legislação:
                {chr(10).join(diretrizes)}

                REGRAS DE OURO:
                1. Se a ação NÃO se enquadra num regime selecionado, faz apenas um pequeno parágrafo enquadrador.
                2. Se se ENQUADRA, faz o enquadramento legal completo e fundamentado.
                3. Conclui explicitamente se a ação é "Legalizável" ou "Insuscetível de Legalização".
                4. Estilo Jurídico Formal. Títulos a **BOLD**.

                TEXTO DO AUTO:
                {texto_auto}

                ESTRUTURA DO DOCUMENTO:
                1. **OBJECTIVO**
                2. **DESCRIÇÃO TÉCNICA E AUDITORIA**
                3. **FUNDAMENTAÇÃO JURÍDICA E TRANSGRESSÕES**
                4. **ANÁLISE JURÍDICA DE VIABILIDADE DE LEGALIZAÇÃO**
                5. **QUADRO SANCIONATÓRIO E NULIDADES**
                6. **PARECER FINAL E MEDIDAS DE REPOSIÇÃO**
                """

                response = model.generate_content(prompt_final)
                
                st.markdown("---")
                st.subheader("📄 Parecer Gerado")
                st.markdown(response.text)
                
                st.download_button("Descarregar Parecer", response.text, file_name="parecer_juridico.md")

            except Exception as e:
                st.error(f"Erro na geração: {e}")
                st.info("Tente mudar o modelo na barra lateral (ex: para gemini-1.5-flash).")
