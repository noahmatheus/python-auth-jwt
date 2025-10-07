import streamlit as st
import requests

# Configuração
API_URL = "http://localhost:6580"  # altere se necessário

st.set_page_config(page_title="Painel de Usuários", layout="wide")

# Inicializa sessão
if "token" not in st.session_state:
    st.session_state["token"] = None
if "refresh" not in st.session_state:
    st.session_state["refresh"] = False


# Funções auxiliares
def get_headers():
    return {"Authorization": f"Bearer {st.session_state['token']}"} if st.session_state["token"] else {}


def listar_usuarios():
    resp = requests.get(f"{API_URL}/usuarios", headers=get_headers())
    return resp.json() if resp.status_code == 200 else []


def criar_usuario(email, senha):
    resp = requests.post(f"{API_URL}/usuarios", json={"email": email, "senha": senha}, headers=get_headers())
    return resp


def editar_usuario(id_usuario, email, senha):
    resp = requests.put(f"{API_URL}/usuarios/{id_usuario}", json={"email": email, "senha": senha}, headers=get_headers())
    return resp


def deletar_usuario(id_usuario):
    resp = requests.delete(f"{API_URL}/usuarios/{id_usuario}", headers=get_headers())
    return resp


def fazer_login(email, senha):
    resp = requests.post(f"{API_URL}/login", json={"email": email, "senha": senha})
    return resp


# Interface
st.title("🔐 Sistema de Usuários com JWT + FastAPI + Streamlit")

if not st.session_state["token"]:
    # --------------------- LOGIN ---------------------
    st.subheader("Acesso ao sistema")

    with st.form("login_form"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            response = fazer_login(email, senha)
            if response.status_code == 200:
                st.session_state["token"] = response.json()["access_token"]
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ E-mail ou senha inválidos")

else:
    # --------------------- HEADER ---------------------
    col1, col2 = st.columns([6, 1])
    with col1:
        st.subheader("📋 Usuários Cadastrados")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state["token"] = None
            st.success("Sessão encerrada.")
            st.rerun()

    st.divider()

    # --------------------- MENU ---------------------
    aba = st.sidebar.radio("Menu", ["Listar", "Cadastrar", "Editar", "Excluir"])

    # --------------------- LISTAR ---------------------
    if aba == "Listar":
        usuarios = listar_usuarios()
        if usuarios:
            st.table(usuarios)
        else:
            st.info("Nenhum usuário encontrado.")

    # --------------------- CADASTRAR ---------------------
    elif aba == "Cadastrar":
        st.subheader("➕ Novo Usuário")
        with st.form("form_cadastro"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Salvar")

            if submitted:
                resp = criar_usuario(email, senha)
                if resp.status_code == 200:
                    st.success("Usuário criado com sucesso!")
                    st.session_state["refresh"] = True
                else:
                    st.error(resp.json().get("detail", "Erro ao criar usuário."))

    # --------------------- EDITAR ---------------------
    elif aba == "Editar":
        st.subheader("✏️ Editar Usuário")

        usuarios = listar_usuarios()
        if usuarios:
            usuario_escolhido = st.selectbox("Selecione o usuário:", usuarios, format_func=lambda u: u["email"])
            novo_email = st.text_input("Novo e-mail", value=usuario_escolhido["email"])
            nova_senha = st.text_input("Nova senha", type="password")

            if st.button("Salvar alterações"):
                resp = editar_usuario(usuario_escolhido["id_usuario"], novo_email, nova_senha)
                if resp.status_code == 200:
                    st.success("Usuário atualizado com sucesso!")
                    st.session_state["refresh"] = True
                else:
                    st.error(resp.json().get("detail", "Erro ao atualizar."))
        else:
            st.info("Nenhum usuário para editar.")

    # --------------------- EXCLUIR ---------------------
    elif aba == "Excluir":
        st.subheader("🗑️ Excluir Usuário")

        usuarios = listar_usuarios()
        if usuarios:
            usuario_escolhido = st.selectbox("Selecione o usuário para deletar:", usuarios, format_func=lambda u: u["email"])
            if st.button("Excluir"):
                resp = deletar_usuario(usuario_escolhido["id_usuario"])
                if resp.status_code == 200:
                    st.success("Usuário excluído com sucesso!")
                    st.session_state["refresh"] = True
                else:
                    st.error(resp.json().get("detail", "Erro ao excluir usuário."))
        else:
            st.info("Nenhum usuário encontrado.")

    # --------------------- RELOAD ---------------------
    if st.session_state["refresh"]:
        st.session_state["refresh"] = False
        st.rerun()
