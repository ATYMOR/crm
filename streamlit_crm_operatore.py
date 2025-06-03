import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = "e_lux_crm.db"
UPLOAD_FOLDER = "documenti_caricati"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Connessione al database
def get_connection():
    return sqlite3.connect(DB_PATH)

# Caricamento dati clienti
def load_clienti():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM clienti", conn)
    conn.close()
    return df

# Inserimento nuovo cliente
def add_cliente(nome, tipo_cliente, responsabile, email, telefono):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clienti (nome, tipo_cliente, responsabile, fase, stato, email, telefono)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, tipo_cliente, responsabile, "1. Identificazione Cliente", "In attesa", email, telefono))
    conn.commit()
    conn.close()

# Caricamento documento per cliente
def upload_documento(cliente_id, file):
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, f"{cliente_id}_{file.name}")
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documenti (cliente_id, tipo_documento, nome_file)
            VALUES (?, ?, ?)
        """, (cliente_id, "Generico", file.name))
        conn.commit()
        conn.close()
        return True
    return False

st.set_page_config(page_title="Inserimento Dati Clienti - E-Lux", layout="wide")
st.title("Modulo Operatore - E-Lux S.r.l.")

menu = ["📋 Lista Clienti", "➕ Nuovo Cliente", "📁 Upload Documenti"]
scelta = st.sidebar.selectbox("Navigazione", menu)

if scelta == "📋 Lista Clienti":
    st.subheader("Elenco Clienti")
    df = load_clienti()
    st.dataframe(df)

elif scelta == "➕ Nuovo Cliente":
    st.subheader("Inserisci un nuovo cliente")
    with st.form("nuovo_cliente"):
        nome = st.text_input("Nome Cliente")
        tipo_cliente = st.selectbox("Tipo Cliente", ["P.IVA", "Condominio", "Privato"])
        responsabile = st.selectbox("Responsabile", ["Elena", "Ingrid", "Michela"])
        email = st.text_input("Email")
        telefono = st.text_input("Telefono")
        submitted = st.form_submit_button("Salva Cliente")

        if submitted:
            if nome and email:
                add_cliente(nome, tipo_cliente, responsabile, email, telefono)
                st.success("Cliente aggiunto correttamente!")
            else:
                st.error("Compila almeno nome ed email.")

elif scelta == "📁 Upload Documenti":
    st.subheader("Carica documento per cliente")
    df = load_clienti()
    clienti_options = df[["id", "nome"]].apply(lambda x: f"{x['id']} - {x['nome']}", axis=1).tolist()
    cliente_selezionato = st.selectbox("Cliente", clienti_options)
    cliente_id = int(cliente_selezionato.split(" - ")[0])
    file = st.file_uploader("Carica file", type=["pdf", "jpg", "jpeg", "png", "docx"])
    if st.button("Salva Documento"):
        if upload_documento(cliente_id, file):
            st.success("Documento caricato con successo!")
        else:
            st.error("Errore durante il caricamento.")
