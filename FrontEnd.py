import streamlit as st
from web3 import Web3
import json
import os
from dotenv import load_dotenv

# --- Carregar variáveis ---
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
INFURA_URL = os.getenv("INFURA_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# --- Conectar à blockchain ---
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
address = account.address

# --- Carregar ABI ---
with open("EduQuiz_ABI.json", "r") as file:
    abi = json.load(file)

contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)

# --- Inicializar sessão ---
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []

# --- Layout ---
st.title("🎓 EduQuiz Web3 – Quiz Interativo")
st.write(f"👛 Conectado como: `{address}`")

# --- Obter perguntas ---
questions = contract.functions.getQuestions().call()

if st.session_state.current_question < len(questions):
    q_index = st.session_state.current_question
    pergunta = questions[q_index]
    
    st.subheader(f"🧠 Pergunta {q_index+1} de {len(questions)}:")
    resposta = st.text_input(f"{pergunta}", key=f"resposta_{q_index}")
    
    if st.button("Responder"):
        if resposta.strip() == "":
            st.warning("❗ Por favor, insira uma resposta antes de continuar.")
        else:
            st.session_state.user_answers.append(resposta)
            st.session_state.current_question += 1
            st.rerun()
else:
    st.success("🎉 Todas as perguntas foram respondidas!")

    if st.button("📤 Enviar Respostas"):
        try:
            nonce = w3.eth.get_transaction_count(address)
            tx = contract.functions.answerBatch(st.session_state.user_answers).build_transaction({
                'from': address,
                'nonce': nonce,
                'gas': 400000,
                'gasPrice': w3.to_wei('5', 'gwei')
            })

            signed_tx = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            st.success(f"✅ Respostas enviadas! Transação: {tx_hash.hex()}")

            # Resetar sessão após envio
            st.session_state.current_question = 0
            st.session_state.user_answers = []
        except Exception as e:
            st.error(f"Erro ao enviar respostas: {e}")

# --- Mostrar saldo ---
balance = w3.eth.get_balance(address)
eth_balance = w3.from_wei(balance, 'ether')
st.info(f"💰 Seu saldo atual: {eth_balance:.5f} SepoliaETH")
