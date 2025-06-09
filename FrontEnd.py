import streamlit as st
from web3 import Web3
import json
import os

# --- Conexão Web3 ---
provider_url = "https://sepolia.infura.io/v3/SUA_INFURA_API_KEY"
w3 = Web3(Web3.HTTPProvider(provider_url))

# --- Endereço do contrato ---
contract_address = "0xSEU_CONTRATO"
with open("EduQuiz_ABI.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)

# --- Conta do jogador ---
private_key = st.text_input("Chave privada da sua carteira:", type="password")
if private_key:
    account = w3.eth.account.from_key(private_key)
    st.write(f"🧑 Carteira conectada: `{account.address}`")

    # --- Mostrar pergunta ---
    question = contract.functions.getQuestion().call()
    st.subheader("🧠 Pergunta do dia:")
    st.write(question)

    answer = st.text_input("Sua resposta:")

    if st.button("Responder"):
        try:
            nonce = w3.eth.get_transaction_count(account.address)
            tx = contract.functions.answer(answer).build_transaction({
                'from': account.address,
                'gas': 200000,
                'nonce': nonce
            })
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            st.success(f"✅ Resposta enviada! Verifique a transação: {w3.to_hex(tx_hash)}")
        except Exception as e:
            st.error(f"❌ Erro: {e}")
