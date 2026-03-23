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
st.info("IA configurada para o regime jurídico atualizado (Simplex 2024 e Contraordenações Ambientais).")

# Seleção de Regimes conforme o Diagrama
st.subheader("Enquadramentos Jurídicos")
c1, c2, c3 = st.columns(3)

with c1:
    check_ren = st.checkbox("REN (DL 166/2008 + DL 123/2024)")
    # CAIXA DE TEXTO DINÂMICA PARA REN
    tipologia_ren = ""
    if check_ren:
        tipologia_ren = st.text_input("Indique a Tipologia REN (ex: Arribas, Cabeceiras, Infiltração Máxima):")
        
    check_ran = st.checkbox("RAN (DL 73/2009 + DL 199/2015)")

with c2:
    check_natura = st.checkbox("Rede Natura 2000 (DL 140/99)")
    check_patrimonio = st.checkbox("Património (Lei 107/2001)")

with c3:
    check_rjue = st.checkbox("Ordenamento/Urbanismo (RJUE + DL 10/2024)")
    check_coimas = st.checkbox("Coimas (Lei 50/2006 + DL 87/2024)")

if st.button("🚀 Gerar Parecer Jurídico"):
    if not api_key or not uploaded_file:
        st.error("⚠️ Falta a API Key ou o ficheiro PDF.")
    elif check_ren and not tipologia_ren:
        st.warning("⚠️ Por favor, indique a tipologia da REN para uma análise precisa.")
    else:
        with st.spinner(f"A analisar com {model_choice}..."):
            try:
                texto_auto = extrair_texto_pdf(uploaded_file)
                
                # Configuração do Modelo selecionado dinamicamente
                model = genai.GenerativeModel(model_name=f"models/{model_choice}")

                # Construção das Instruções Legais Dinâmicas
                diretrizes = []
                if check_ren: 
                    diretrizes.append(f"- REN: DL 166/2008 atualizado pelo DL 123/2024. O utilizador indicou a TIPOLOGIA: '{tipologia_ren}'. "
                                      "Cruzar obrigatoriamente com o ANEXO II (Usos e ações compatíveis) e fundamentar com o Art. 20º.")
                
                if check_ran: diretrizes.append("- RAN: DL 73/2009 e DL 199/2015. Transcrever alíneas do Art. 21º ou 22º.")
                if check_rjue: diretrizes.append("- Urbanismo: RJUE (DL 555/99) e Simplex Urbanístico (DL 10/2024). Focar na Nulidade do Art. 68º se faltarem pareceres.")
                if check_natura: diretrizes.append("- Rede Natura 2000: DL 140/99 (versão atualizada). Aplicar o teste de exceção do Art. 9º.")
                if check_coimas: diretrizes.append("- Contraordenações: Lei 50/2006 com as alterações do DL 87/2024.")

                prompt_final = f"""
                Age como um Jurista Sénior de uma CCDR em Portugal (PT-PT).
                Analisa o texto do AUTO DE NOTÍCIA com base na seguinte legislação e diretrizes:
                {chr(10).join(diretrizes)}

                REGRAS CRÍTICAS DE ANÁLISE:
                1. NULIDADES (Art. 68.º RJUE): Identifica se a operação é nula por falta de pareceres vinculativos (ex: ICNF, APA, CCDR) em áreas protegidas ou REN.
                2. VIABILIDADE DE LEGALIZAÇÃO:
                   - Equaciona se a pretensão tem parâmetros urbanísticos para legalização (Art. 102º RJUE).
                   - Analisa especificamente a viabilidade face ao Artigo 9.º do DL 140/99 (se em Rede Natura) e Artigo 20.º e 21.º do RJREN (DL 166/2008).
                   - Verificar se a ação é compatível com a proteção ecológica e prevenção de riscos da tipologia REN indicada.
                3. ENQUADRAMENTO: Se a ação NÃO se enquadra num regime, faz apenas um pequeno parágrafo justificativo. Se se ENQUADRA, fundamenta exaustivamente.
                4. ESTILO: Jurídico formal, capítulos a **BOLD**.

                TEXTO DO AUTO:
                {texto_auto}

                ESTRUTURA OBRIGATÓRIA:
                1. **OBJECTIVO**
                2. **DESCRIÇÃO TÉCNICA E AUDITORIA**
                3. **FUNDAMENTAÇÃO JURÍDICA E TRANSGRESSÕES**
                4. **ANÁLISE JURÍDICA DE VIABILIDADE DE LEGALIZAÇÃO** (Cruzar critérios cumulativos e compatibilidade com a tipologia REN)
                5. **QUADRO SANCIONATÓRIO E NULIDADES**
                6. **PARECER FINAL E MEDIDAS DE REPOSIÇÃO**
                """

                response = model.generate_content(prompt_final)
                
                st.markdown("---")
                st.subheader("📄 Parecer Jurídico Gerado")
                st.markdown(response.text)
                
                st.download_button(
                    label="Descarregar Parecer (Markdown)",
                    data=response.text,
                    file_name="parecer_fiscalizacao_final.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"Erro na geração: {e}")
                st.info("Dica: Se o erro for 404, selecione outro modelo na barra lateral.")
