import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import sqlite3
import openai
from datetime import datetime
import calendar

st.set_page_config(page_title="Barbearia Lira", page_icon="💈", layout="wide")

# Modo escuro total com gradiente
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to bottom, #1c1c1c, #2c2c2c);
        color: white;
    }
    .css-18e3th9 { padding-top: 2rem; }
    .card {
        background-color: #2e2e2e;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.3);
    }
    .title { font-size: 2.5rem; font-weight: 700; color: #ffffff; }
    .subtitle { color: #d4af37; font-weight: 500; margin-top: -10px; }
    .info { font-size: 1rem; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# Sistema de autenticação
usuarios = {
    "sandro": {"senha": "admin123", "perfil": "Administrador"},
    "gabriel": {"senha": "barbeiro1", "perfil": "Barbeiro"},
    "vitor": {"senha": "barbeiro2", "perfil": "Barbeiro"},
    "junior": {"senha": "barbeiro3", "perfil": "Barbeiro"},
    "cliente": {"senha": "cliente123", "perfil": "Cliente"}
}

usuario = st.sidebar.text_input("Usuário").strip().lower()
senha = st.sidebar.text_input("Senha", type="password")

if usuario in usuarios and senha == usuarios[usuario]["senha"]:
    perfil = usuarios[usuario]["perfil"]
    if perfil != "Cliente":
        st.sidebar.success(f"Bem-vindo, {usuario} ({perfil})")

    # Cabeçalho com imagem
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("302f04a5517946beae1749489002d1-barbearia-lira-biz-photo-f5a6e581d8a74a2ab9aca5367d3eb1-booksy.jpeg", width=600)
        st.markdown(f"<div style='text-align:center; background-color:#1c1c1c; padding:15px; border-radius:8px;'>"
                    f"<p class='title'>Barbearia Lira</p>"
                    f"<p class='subtitle'>Estilo, tradição e tecnologia</p>"
                    f"<p class='info'>Usuário logado: <strong>{usuario.upper()}</strong> ({perfil})</p>"
                    f"</div>", unsafe_allow_html=True)

    # Conexão com banco
    conn = sqlite3.connect("barbearia_lira.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS agendamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente TEXT, servico TEXT, profissional TEXT, horario TEXT)''')
    conn.commit()

    # Menu lateral somente se não for cliente
    if perfil != "Cliente":
        menu = st.sidebar.radio("Navegação", ["🏠 Início", "🧠 Recomendação de Serviços", "📊 Relatórios", "📅 Calendário", "🤖 Chatbot IA"])
    else:
        menu = "📅 Calendário"

    clientes = [f"Cliente_{i}" for i in range(1, 21)]
    servicos = ["Corte de Cabelo", "Barba", "Sobrancelha", "Combo Corte + Barba", "Combo Completo"]
    profissionais = ["Gabriel", "Vitor", "Júnior"]

    if menu == "🏠 Início":
        st.subheader("📋 Painel Inicial")
        st.markdown("Gerencie seus agendamentos e utilize inteligência artificial para melhorar sua performance.")

    elif menu == "🧠 Recomendação de Serviços":
        st.subheader("🎯 Recomendação de Serviços Inteligente")
        cliente = st.selectbox("Selecione um cliente", clientes)
        if st.button("🔍 Gerar Recomendações"):
            recomendados = random.sample(servicos, 3)
            scores = [round(random.uniform(0.7, 0.95), 2) for _ in recomendados]
            for s, sc in zip(recomendados, scores):
                st.markdown(f"- **{s}** (chance de aceitação: {int(sc*100)}%)")

    elif menu == "📊 Relatórios":
        st.subheader("📈 Relatórios de Agendamentos")
        df = pd.read_sql_query("SELECT * FROM agendamentos", conn)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar CSV", csv, "agendamentos.csv", "text/csv")

    elif menu == "📅 Calendário":
        st.subheader("📅 Agendamentos por Calendário")
        data = st.date_input("Escolha uma data para visualizar agendamentos")
        data_formatada = data.strftime('%d/%m/%Y')
        df_cal = pd.read_sql_query("SELECT * FROM agendamentos", conn)
        st.markdown(f"### Agendamentos para {data_formatada} (simulado)")
        st.dataframe(df_cal[df_cal["horario"].str.contains(data_formatada[-2:])])

    elif menu == "🤖 Chatbot IA":
        st.subheader("🤖 Assistente Virtual da Barbearia")
        pergunta = st.text_input("Digite sua pergunta:")
        if pergunta:
            openai.api_key = st.secrets.get("OPENAI_API_KEY", "chave_nao_definida")
            try:
                resposta = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Você é um atendente cordial da Barbearia Lira em Goiânia. A barbearia funciona de segunda a sábado, das 9h às 19h."},
                        {"role": "user", "content": pergunta}
                    ],
                    max_tokens=300, temperature=0.6)
                st.success(resposta.choices[0].message.content.strip())
            except Exception as e:
                st.error(f"Erro na consulta com IA: {e}")
else:
    st.sidebar.warning("Acesso restrito. Insira usuário e senha válidos.")
