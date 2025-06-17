import streamlit as st
import streamlit.components.v1 as components
import json
import urllib.parse
import os
from dotenv import load_dotenv
from web3 import Web3

# --- Conexão Web3 ---
load_dotenv()
infura_url = os.getenv("INFURA_URL")
w3 = Web3(Web3.HTTPProvider(infura_url))

# --- Sessão ---
if "etapa" not in st.session_state:
    st.session_state["etapa"] = "menu"
if "respostas" not in st.session_state:
    st.session_state["respostas"] = []
if "index" not in st.session_state:
    st.session_state["index"] = 0

st.sidebar.write("🧩 Etapa atual:", st.session_state["etapa"])

# --- Navegação ---
def ir_para_criar():
    st.session_state["etapa"] = "criar"

def ir_para_quiz():
    st.session_state["etapa"] = "quiz"
    st.session_state["respostas"] = []
    st.session_state["index"] = 0

    try:
        with open("EduQuiz_ABI.json") as f:
            abi = json.load(f)
        addr = os.getenv("CONTRACT_ADDRESS")
        contract = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=abi)
        perguntas = contract.functions.getQuestions().call()
        st.session_state["perguntas"] = perguntas
    except Exception as e:
        st.session_state["etapa"] = "erro"
        st.session_state["erro_msg"] = str(e)

def voltar_menu():
    st.session_state["etapa"] = "menu"
    st.session_state.pop("input_perguntas", None)
    st.session_state.pop("input_respostas", None)
    st.session_state["respostas"] = []
    st.session_state["index"] = 0

# --- Menu Principal ---
if st.session_state["etapa"] == "menu":
    st.title("🎯 EduQuiz Web3")
    st.button("📄 Criar novo quiz", on_click=ir_para_criar)

    st.subheader("🧠 Entrar em um quiz existente")
    quiz_addr = st.text_input("Endereço do contrato do quiz")

    def carregar_quiz():
        if Web3.is_address(quiz_addr):
            try:
                with open("EduQuiz_ABI.json") as f:
                    abi = json.load(f)
                contract = w3.eth.contract(address=Web3.to_checksum_address(quiz_addr), abi=abi)
                perguntas = contract.functions.getQuestions().call()
                st.session_state["etapa"] = "quiz"
                st.session_state["contract_address"] = quiz_addr
                st.session_state["perguntas"] = perguntas
                st.session_state["respostas"] = []
                st.session_state["index"] = 0
            except Exception as e:
                st.error(f"Erro ao carregar o contrato: {e}")
        else:
            st.error("Endereço inválido.")

    st.button("▶️ Entrar no quiz", on_click=carregar_quiz)


# --- Etapa: Criar Quiz ---
elif st.session_state["etapa"] == "criar":
    st.title("🛠 Criar Novo Quiz")

    perguntas = st.text_area("Perguntas (uma por linha)", key="input_perguntas")
    respostas = st.text_area("Respostas (na mesma ordem)", key="input_respostas")
    conta = st.text_input("Conta MetaMask (para deploy)", key="input_conta")
    valor_recompensa = st.text_input("Valor por acerto (ETH)", value="0.01", key="input_valor")
    valor_total = st.text_input("Valor total a depositar (ETH)", value="0.1", key="input_valor_total")


    if st.button("📤 Criar contrato"):
        lista_p = [p.strip() for p in perguntas.split("\n") if p.strip()]
        lista_r = [r.strip() for r in respostas.split("\n") if r.strip()]
        
        if len(lista_p) != len(lista_r):
            st.error("❌ Número de perguntas e respostas não coincide.")
        elif not conta:
            st.error("❌ Conta MetaMask obrigatória.")
        else:
            data = {
                "questions": lista_p,
                "answers": lista_r,
                "account": conta,
                "reward": valor_recompensa,
                "total": valor_total
            }
            encoded = urllib.parse.quote(json.dumps(data))
            js = f"""<script>
            window.open("http://localhost:3000/deploy_quiz.html?data={encoded}", "_blank");
            </script>"""
            components.html(js)


# --- Etapa: Quiz ---
elif st.session_state["etapa"] == "quiz":
    st.title("🧠 Quiz em andamento")

    perguntas = st.session_state.get("perguntas", [])
    index = st.session_state["index"]

    if index < len(perguntas):
        pergunta = perguntas[index]
        resposta = st.text_input(pergunta, key=f"resposta_{index}")
        if st.button("Responder"):
            if resposta.strip():
                st.session_state["respostas"].append(resposta.strip())
                st.session_state["index"] += 1
    else:
        st.success("✅ Quiz finalizado!")
        respostas_usuario = st.session_state["respostas"]
        perguntas = st.session_state["perguntas"]
        contrato_addr = st.session_state["contract_address"]

        try:
            with open("EduQuiz_ABI.json") as f:
                abi = json.load(f)
            contrato = w3.eth.contract(address=Web3.to_checksum_address(contrato_addr), abi=abi)

            resultado = contrato.functions.checkAnswers(respostas_usuario).call()
            acertos = sum(resultado)
            recompensa_wei = contrato.functions.rewardPerCorrect().call()
            recompensa_total_wei = recompensa_wei * acertos
            recompensa_total_eth = Web3.from_wei(recompensa_total_wei, 'ether')

            st.info(f"🎯 Você acertou {acertos} de {len(perguntas)} perguntas.")
            st.success(f"💰 Recompensa estimada: {recompensa_total_eth} Sepolia ETH")

        except Exception as e:
            st.error(f"Erro ao verificar respostas: {e}")

        conta = st.text_input("Conta MetaMask para envio:", key="conta_final")
        if st.button("📤 Solicitar recompensa via MetaMask"):
            if conta:
                answers_json = urllib.parse.quote(json.dumps(respostas_usuario))
                url = f"http://localhost:3000/confirm_transaction.html?answers={answers_json}&address={contrato_addr}&account={conta}"
                st.markdown(f"""
                <a href="{url}" target="_blank">
                    <button>🦊 Enviar transação</button>
                </a>
                """, unsafe_allow_html=True)
            else:
                st.error("Preencha a conta MetaMask para continuar.")

        st.button("⬅️ Voltar ao menu", on_click=voltar_menu)


# --- Etapa: Erro ---
elif st.session_state["etapa"] == "erro":
    st.error("Erro ao carregar contrato:")
    st.code(st.session_state.get("erro_msg", "Desconhecido"))
    st.button("⬅️ Voltar ao menu", on_click=voltar_menu)
