import streamlit as st
import sqlite3
from datetime import datetime, time
import openai

st.set_page_config(page_title="Agendamento Online - Barbearia Lira", page_icon="💈", layout="centered")

# Título e descrição
st.markdown("""
    <div style='text-align:center;'>
        <h1 style='color:#d4af37;'>💈 Barbearia Lira</h1>
        <h3 style='color:white;'>Agendamento Online</h3>
        <p style='color:gray;'>Escolha seu serviço, profissional e horário</p>
    </div>
""", unsafe_allow_html=True)

# Banco de dados
conn = sqlite3.connect("barbearia_lira.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT,
                servico TEXT,
                profissional TEXT,
                horario TEXT
            )''')
conn.commit()

# Formulário de agendamento
with st.form("agendamento_form"):
    nome = st.text_input("Seu nome completo")
    telefone = st.text_input("WhatsApp")
    servico = st.selectbox("Serviço", ["Corte de Cabelo", "Barba", "Sobrancelha", "Combo Corte + Barba", "Combo Completo"])
    profissional = st.selectbox("Profissional", ["Gabriel", "Vitor", "Júnior"])
    data = st.date_input("Data")
    hora = st.time_input("Horário", value=time(9, 0))
    submit = st.form_submit_button("Confirmar Agendamento")

if submit:
    horario_completo = f"{data.strftime('%d/%m/%Y')} {hora.strftime('%H:%M')}"
    c.execute("INSERT INTO agendamentos (cliente, servico, profissional, horario) VALUES (?, ?, ?, ?)",
              (nome, servico, profissional, horario_completo))
    conn.commit()

    st.success(f"Agendamento confirmado para {nome} às {horario_completo} com {profissional}.")

    mensagem = f"Olá! Gostaria de confirmar meu agendamento para {servico} com {profissional} em {horario_completo}. Nome: {nome}, WhatsApp: {telefone}"
    whatsapp_url = f"https://api.whatsapp.com/send?phone=556299999999&text={mensagem.replace(' ', '%20')}"
    st.markdown(f"[📲 Enviar Confirmação via WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

# Chatbot de dúvidas ao cliente
st.markdown("""
    <hr style='border:1px solid #444;'>
    <h4 style='color:white;'>🤖 Dúvidas? Pergunte ao nosso assistente virtual:</h4>
""", unsafe_allow_html=True)

pergunta = st.text_input("Digite sua pergunta sobre nossos serviços, horários ou preços:")
if pergunta:
    openai.api_key = st.secrets.get("OPENAI_API_KEY", "chave_nao_definida")
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um atendente cordial da Barbearia Lira em Goiânia. A barbearia funciona de segunda a sábado, das 9h às 19h. Os serviços são: Corte de Cabelo (R$40), Barba (R$30), Sobrancelha (R$20), Combo Corte + Barba (R$60), Combo Completo (R$75)."},
                {"role": "user", "content": pergunta}
            ],
            max_tokens=300,
            temperature=0.6
        )
        st.success(resposta.choices[0].message.content.strip())
    except Exception as e:
        st.error(f"Erro na consulta com IA: {e}")

# Rodapé
st.markdown("""
    <hr style='border:1px solid #444;'>
    <div style='text-align:center; color:gray;'>
        Desenvolvido por USINA I.A. • Atendimento online integrado à gestão da Barbearia Lira
    </div>
""", unsafe_allow_html=True)
