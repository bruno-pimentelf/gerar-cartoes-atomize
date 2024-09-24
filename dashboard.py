import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import streamlit as st
import io
from PIL import Image
from reportlab.lib.utils import ImageReader
import zipfile

# Registrar as fontes Poppins
pdfmetrics.registerFont(TTFont('Poppins', 'poppins/Poppins-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Poppins_Bold', 'poppins/Poppins-Bold.ttf'))

# Função para criar um PDF estilizado no formato de cartão com imagem de fundo
def criar_pdf_personalizado(escola, nome, email, senha, imagem_frente_curta, imagem_frente_longa, imagem_verso):
    largura, altura = 3.5 * inch, 2 * inch
    buffer = io.BytesIO()
    
    nome_formatado = nome.title()
    if len(nome_formatado) > 42:
        imagem_fundo_frente = Image.open(imagem_frente_longa)
    else:
        imagem_fundo_frente = Image.open(imagem_frente_curta)

    c = canvas.Canvas(buffer, pagesize=(largura, altura))

    # Frente do cartão
    c.drawImage(ImageReader(imagem_fundo_frente), 0, 0, width=largura, height=altura)
    c.setFont("Poppins_Bold", 8)
    c.setFillColor(colors.darkblue)
    
    # Dividir o nome se for maior que 42 caracteres
    if len(nome_formatado) > 42:
        palavras = nome_formatado.split()
        primeira_linha = ""
        segunda_linha = ""
        for palavra in palavras:
            if len(primeira_linha) + len(palavra) <= 42:
                primeira_linha += palavra + " "
            else:
                segunda_linha += palavra + " "
        c.drawString(0.36 * inch, altura - 0.5 * inch, primeira_linha.strip())
        c.drawString(0.36 * inch, altura - 0.65 * inch, segunda_linha.strip())
    else:
        c.drawString(0.36 * inch, altura - 0.5 * inch, nome_formatado)
    
    c.setFont("Poppins", 6.5)
    c.setFillColor(colors.black)
    c.drawString(0.7 * inch, altura - 1.18 * inch, f"{email}")
    c.drawString(0.74 * inch, altura - 1.37 * inch, f"{senha}")
    c.drawString(0.37 * inch, altura - 0.21 * inch, f"{escola}")

    # Verso do cartão
    c.showPage()
    c.drawImage(ImageReader(Image.open(imagem_verso)), 0, 0, width=largura, height=altura)

    c.save()
    buffer.seek(0)
    return buffer

# Configuração da página Streamlit
st.set_page_config(page_title="Gerador de Cartões PDF", layout="wide")

st.title("Gerador de Cartões PDF")

st.write("""
Este aplicativo gera cartões PDF personalizados com base em uma planilha de dados.
Por favor, siga as instruções abaixo para gerar seus cartões:
""")

# Upload das imagens de fundo
st.header("1. Faça o upload das imagens de fundo")

imagem_frente_curta = st.file_uploader("Imagem de fundo para nomes curtos (até 42 caracteres)", type=["png", "jpg", "jpeg"])
imagem_frente_longa = st.file_uploader("Imagem de fundo para nomes longos (mais de 42 caracteres)", type=["png", "jpg", "jpeg"])
imagem_verso = st.file_uploader("Imagem de fundo para o verso do cartão", type=["png", "jpg", "jpeg"])

# Upload da planilha
st.header("2. Faça o upload da planilha de dados")

st.write("""
A planilha deve conter as seguintes colunas:
- Escola
- Nome
- Email
- Senha
""")

arquivo_csv = st.file_uploader("Selecione o arquivo CSV", type="csv")

if arquivo_csv and imagem_frente_curta and imagem_frente_longa and imagem_verso:
    df = pd.read_csv(arquivo_csv)
    
    if st.button("Gerar PDFs"):
        # Criar um arquivo ZIP para armazenar todos os PDFs
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # Gerar PDFs para cada aluno
            for index, row in df.iterrows():
                escola = row['Escola']
                nome = row['Nome']
                email = row['Email']
                senha = row['Senha']
                
                pdf_buffer = criar_pdf_personalizado(escola, nome, email, senha, imagem_frente_curta, imagem_frente_longa, imagem_verso)
                
                # Adicionar o PDF ao arquivo ZIP
                zip_file.writestr(f"{nome.replace(' ', '_')}_cartao.pdf", pdf_buffer.getvalue())
        
        # Oferecer o download do arquivo ZIP
        zip_buffer.seek(0)
        st.success("Todos os PDFs foram gerados com sucesso!")
        st.download_button(
            label="Baixar todos os PDFs (ZIP)",
            data=zip_buffer,
            file_name="cartoes.zip",
            mime="application/zip"
        )
else:
    st.warning("Por favor, faça o upload de todas as imagens de fundo e da planilha CSV para gerar os PDFs.")
