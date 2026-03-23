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
    st.info("A IA consultará as versões mais recentes do DR (ex: DL 123/2024).")
    
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
        with st.spinner("A processar legislação e a redigir..."):
            texto_auto = extrair_texto_pdf(uploaded_file)
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')

            # Construção da base de conhecimento do Prompt
            contexto_legal = ""
            if check_ren:
                contexto_legal += "- REN: Analisar sob o DL 166/2008, com a redação atualíssima do DL 123/2024. Verificar Tipologias do Anexo II e critérios de exceção do Art. 20º.\n"
            if check_ran:
                contexto_legal += "- RAN: Analisar sob o DL 73/2009 (redação DL 199/2015). Focar nos Arts. 21º e 22º (utilizações não agrícolas).\n"
            if check_rjue:
                contexto_legal += "- Urbanismo: Considerar o novo 'Simplex Urbanístico' (DL 10/2024) que alterou o RJUE.\n"
            if check_coimas:
                contexto_legal += "- Coimas: Aplicar a Lei 50/2006 (Lei Quadro das Contraordenações Ambientais) com a redação do DL 87/2024.\n"

            prompt_final = f"""
            ESTRUTURA DE PARECER TÉCNICO-JURÍDICO (PT-PT)
            
            És um jurista sénior da administração pública. Com base no texto do AUTO DE NOTÍCIA abaixo, gera um parecer.
            
            REGRAS CRÍTICAS:
            1. Se a ação descrita NÃO se enquadra num regime selecionado, escreve apenas um parágrafo curto justificando a exclusão.
            2. Se se ENQUADRA, faz uma análise exaustiva com citações de artigos.
            3. Estilo: Formal, técnico, capítulos a **BOLD**.
            4. Se houver dúvidas sobre a legalização, aplica os critérios cumulativos (ex: interesse público, inexistência de alternativa).

            CONTEÚDO DO AUTO:
            {texto_auto}

            DIRETRIZES DE ATUALIZAÇÃO LEGISLATIVA:
            {contexto_legal}
            
            ESTRUTURA DO OUTPUT:
            1. **OBJECTIVO**
            2. **DESCRIÇÃO TÉCNICA E AUDITORIA** (Cruzamento com Portarias 419/2012 ou 162/2011 se aplicável)
            3. **FUNDAMENTAÇÃO JURÍDICA E TRANSGRESSÕES**
            4. **ANÁLISE JURÍDICA DE VIABILIDADE DE LEGALIZAÇÃO** (Concluir taxativamente)
            5. **QUADRO SANCIONATÓRIO E NULIDADES**
            6. **PARECER FINAL E MEDIDAS DE REPOSIÇÃO**
            """

            try:
                response = model.generate_content(prompt_final)
                st.markdown("### 📄 Parecer Gerado")
                st.markdown(response.text)
                
                # Botão para copiar texto
                st.download_button("Baixar Parecer (TXT)", response.text, file_name="parecer_fiscalizacao.txt")
            except Exception as e:
                st.error(f"Erro na IA: {e}")