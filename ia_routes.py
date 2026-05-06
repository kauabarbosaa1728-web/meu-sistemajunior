from flask import Blueprint, request, session, redirect
from banco import conectar, devolver_conexao
from tradutor import t
import difflib
import os

# (opcional premium)
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
except:
    openai = None

ia_bp = Blueprint("ia_bp", __name__)


# ================= NORMALIZAR =================
def normalizar(txt):
    return txt.lower().strip()


# ================= APRENDIZADO =================
def buscar_aprendizado(pergunta):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT pergunta, resposta FROM ia_aprendizado")
        dados = cursor.fetchall()
    except:
        devolver_conexao(conn)
        return None

    devolver_conexao(conn)

    perguntas = [p[0] for p in dados]
    match = difflib.get_close_matches(pergunta, perguntas, n=1, cutoff=0.7)

    if match:
        for p, r in dados:
            if p == match[0]:
                return r

    return None


def salvar_aprendizado(pergunta, resposta):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ia_aprendizado (
            id SERIAL PRIMARY KEY,
            pergunta TEXT,
            resposta TEXT
        )
        """)

        cursor.execute(
            "INSERT INTO ia_aprendizado (pergunta, resposta) VALUES (%s, %s)",
            (pergunta, resposta)
        )

        conn.commit()
    except:
        pass

    devolver_conexao(conn)


# ================= IA FREE =================
def ia_free(pergunta):
    pergunta_lower = normalizar(pergunta)

    # 🔥 aprendizado
    aprendido = buscar_aprendizado(pergunta_lower)
    if aprendido:
        return t(aprendido)

    conn = conectar()
    cursor = conn.cursor()

    # SAUDAÇÃO
    if any(p in pergunta_lower for p in ["oi", "ola", "hello", "hola"]):
        devolver_conexao(conn)
        return t("Olá! Posso te ajudar com estoque, financeiro e veículos.")

    # ESTOQUE
    if "estoque" in pergunta_lower:
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(quantidade),0) FROM estoque")
        total, qtd = cursor.fetchone()
        devolver_conexao(conn)

        resp = f"Você tem {total} produtos e {qtd} itens no estoque."
        salvar_aprendizado(pergunta_lower, resp)
        return t(resp)

    # FINANCEIRO
    if "financeiro" in pergunta_lower:
        cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='entrada'")
        entrada = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='saida'")
        saida = cursor.fetchone()[0]

        saldo = entrada - saida
        devolver_conexao(conn)

        resp = f"Seu saldo atual é R$ {saldo:.2f}"
        salvar_aprendizado(pergunta_lower, resp)
        return t(resp)

    devolver_conexao(conn)

    resp = "Ainda estou aprendendo 😄"
    salvar_aprendizado(pergunta_lower, resp)
    return t(resp)


# ================= IA PREMIUM =================
def ia_premium(pergunta):
    if not openai:
        return ia_free(pergunta)

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente de sistema ERP."},
                {"role": "user", "content": pergunta}
            ]
        )
        return resposta.choices[0].message.content
    except:
        return ia_free(pergunta)


# ================= IA PRINCIPAL =================
def resposta_inteligente(pergunta):
    plano = session.get("plano", "free")

    if plano == "premium":
        return ia_premium(pergunta)

    return ia_free(pergunta)


# ================= ROTA =================
@ia_bp.route("/ia", methods=["GET", "POST"])
def ia():
    if "user" not in session:
        return redirect("/")

    if "chat" not in session:
        session["chat"] = []

    if request.method == "POST":
        pergunta = request.form.get("pergunta")
        resposta = resposta_inteligente(pergunta)

        session["chat"].append({"role": "user", "content": pergunta})
        session["chat"].append({"role": "assistant", "content": resposta})

    # 🔥 HISTÓRICO
    historico = ""
    for msg in session["chat"]:
        if msg["role"] == "user":
            historico += f"<div class='msg user'>{msg['content']}</div>"
        else:
            historico += f"<div class='msg bot'>{msg['content']}</div>"

    return f"""
    <style>
        body {{
            background:#0f0f0f;
            color:white;
            font-family: Arial;
        }}

        .container {{
            max-width:800px;
            margin:auto;
            margin-top:20px;
            display:flex;
            flex-direction:column;
            height:90vh;
        }}

        .chat-box {{
            flex:1;
            overflow-y:auto;
            padding:10px;
            display:flex;
            flex-direction:column;
        }}

        .msg {{
            padding:12px;
            border-radius:12px;
            margin:6px 0;
            max-width:70%;
            word-wrap:break-word;
        }}

        .user {{
            background:#2563eb;
            align-self:flex-end;
        }}

        .bot {{
            background:#1f2937;
            align-self:flex-start;
        }}

        .input-box {{
            display:flex;
            padding:10px;
            border-top:1px solid #333;
        }}

        input {{
            flex:1;
            padding:15px;
            border:none;
            border-radius:10px;
            background:#2b2b2b;
            color:white;
        }}

        button {{
            padding:15px;
            margin-left:10px;
            border:none;
            border-radius:10px;
            background:white;
            cursor:pointer;
        }}
    </style>

    <div class="container">

        <div class="chat-box" id="chat">
            {historico}
        </div>

        <form method="post" class="input-box">
            <input name="pergunta" placeholder="{t("Pergunte qualquer coisa...")}">
            <button>{t("Enviar")}</button>
        </form>

    </div>

    <script>
        var chat = document.getElementById("chat");
        chat.scrollTop = chat.scrollHeight;
    </script>
    """
