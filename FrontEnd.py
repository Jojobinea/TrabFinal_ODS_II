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

st.title("🎓 EduQuiz Web3 – Quiz Final")
st.write(f"👛 Conectado como: `{address}`")

# --- Obter perguntas do contrato ---
questions = contract.functions.getQuestions().call()

st.subheader("🧠 Responda todas as perguntas:")

user_answers = []
for idx, q in enumerate(questions):
    resposta = st.text_input(f"Q{idx+1}: {q}", key=f"resp_{idx}")
    user_answers.append(resposta)

if st.button("Enviar Respostas"):
    try:
        # Preparar transação
        nonce = w3.eth.get_transaction_count(address)
        tx = contract.functions.answerBatch(user_answers).build_transaction({
            'from': address,
            'nonce': nonce,
            'gas': 400000,
            'gasPrice': w3.to_wei('5', 'gwei')
        })

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        st.success(f"✅ Respostas enviadas! Transação: {tx_hash.hex()}")
    except Exception as e:
        st.error(f"Erro ao enviar respostas: {e}")

# Mostrar saldo final
balance = w3.eth.get_balance(address)
eth_balance = w3.from_wei(balance, 'ether')
st.info(f"💰 Seu saldo atual: {eth_balance:.5f} SepoliaETH")