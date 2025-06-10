import streamlit as st
from web3 import Web3
import json
import os
from dotenv import load_dotenv

# --- Carregar variáveis ---
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")        # Conta do aluno
INFURA_URL = os.getenv("INFURA_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# --- Conexão com a blockchain ---
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
address = account.address

# --- Carregar ABI do contrato ---
with open("EduQuiz_ABI.json", "r") as file:
    abi = json.load(file)

contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)

# --- Interface Streamlit ---
st.title("🎓 EduQuiz Web3 – Aluno")
st.write(f"👛 Conectado como: `{address}`")

# --- Obter pergunta do contrato ---
question = contract.functions.getQuestion().call()
st.subheader("🧠 Pergunta do dia:")
st.write(f"**{question}**")

resposta = st.text_input("Digite sua resposta:")

if st.button("Enviar resposta"):
    try:
        nonce = w3.eth.get_transaction_count(address)
        tx = contract.functions.answer(resposta).build_transaction({
            'from': address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.to_wei('5', 'gwei')
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        st.success(f"✅ Resposta enviada! Transação: {tx_hash.hex()}")
    except Exception as e:
        st.error(f"Erro ao enviar resposta: {e}")
