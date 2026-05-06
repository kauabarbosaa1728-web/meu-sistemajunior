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


# ================= SIMILARIDADE =================
def parecido(pergunta, lista):
    return difflib.get_close_matches(pergunta, lista, n=1, cutoff=0.6)


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

    aprendido = buscar_aprendizado(pergunta_lower)
    if aprendido:
        return t(aprendido)

    conn = conectar()
    cursor = conn.cursor()

    saudacao_kw = ["oi", "ola", "hello", "hola", "eai", "fala"]
    ajuda_kw = ["ajuda", "menu", "opções", "opcoes"]
    estoque_kw = ["estoque", "produto", "produtos", "itens", "quantidade"]
    financeiro_kw = ["financeiro", "saldo", "dinheiro", "lucro", "entrada", "saida"]

    # ================= SAUDAÇÃO =================
    if any(p in pergunta_lower for p in saudacao_kw):
        devolver_conexao(conn)
        return t("👋 Olá! Sistema ativo. Posso ajudar você.")

    # ================= AJUDA =================
    if any(p in pergunta_lower for p in ajuda_kw):
        devolver_conexao(conn)
        return t("📡 Comandos: estoque, financeiro, produtos")

    # ================= ESTOQUE =================
    if any(p in pergunta_lower for p in estoque_kw):
        try:
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(quantidade),0) FROM estoque")
            total, qtd = cursor.fetchone()

            cursor.execute("""
                SELECT produto, quantidade 
                FROM estoque 
                ORDER BY quantidade DESC 
                LIMIT 3
            """)
            top = cursor.fetchall()

            texto = "📦 SISTEMA ESTOQUE ONLINE\n"
            texto += f"TOTAL: {total}\nITENS: {qtd}\n\n"

            if top:
                texto += "TOP PRODUTOS:\n"
                for p, q in top:
                    texto += f"> {p} => {q}\n"

            salvar_aprendizado(pergunta_lower, texto)
            devolver_conexao(conn)
            return t(texto)

        except:
            devolver_conexao(conn)
            return t("ERRO NO ESTOQUE")

    # ================= FINANCEIRO =================
    if any(p in pergunta_lower for p in financeiro_kw):
        try:
            cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='entrada'")
            entrada = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='saida'")
            saida = cursor.fetchone()[0]

            saldo = entrada - saida

            texto = "💰 SISTEMA FINANCEIRO\n"
            texto += f"ENTRADA: R$ {entrada:.2f}\n"
            texto += f"SAÍDA: R$ {saida:.2f}\n"
            texto += f"SALDO: R$ {saldo:.2f}"

            salvar_aprendizado(pergunta_lower, texto)
            devolver_conexao(conn)
            return t(texto)

        except:
            devolver_conexao(conn)
            return t("ERRO FINANCEIRO")

    devolver_conexao(conn)

    resp = "🤖 SISTEMA EM APRENDIZADO..."
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
                {"role": "system", "content": "Você é um assistente de sistema ERP cyber azul."},
                {"role": "user", "content": pergunta}
            ]
        )
        return resposta.choices[0].message.content
    except:
        return ia_free(pergunta)


# ================= IA PRINCIPAL =================
def resposta_inteligente(pergunta):
    if session.get("plano") == "premium":
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

    historico = ""
    for msg in session["chat"]:
        if msg["role"] == "user":
            historico += f"<div class='msg user'>{msg['content']}</div>"
        else:
            historico += f"<div class='msg bot'>{msg['content']}</div>"

    return f"""
    <style>
        body {{
            background: radial-gradient(circle at top, #001a33, #000000);
            color:#00c8ff;
            font-family: 'Courier New', monospace;
        }}

        .container {{
            max-width:800px;
            margin:auto;
            margin-top:20px;
            display:flex;
            flex-direction:column;
            height:90vh;
            border:1px solid #00c8ff;
            box-shadow: 0 0 20px #00c8ff;
            border-radius:12px;
        }}

        .chat-box {{
            flex:1;
            overflow-y:auto;
            padding:15px;
            display:flex;
            flex-direction:column;
        }}

        .msg {{
            padding:10px;
            border-radius:8px;
            margin:6px 0;
            max-width:75%;
            white-space:pre-line;
            border:1px solid #00c8ff;
        }}

        .user {{
            background:#003355;
            align-self:flex-end;
            box-shadow:0 0 10px #00c8ff;
        }}

        .bot {{
            background:#00111f;
            align-self:flex-start;
        }}

        .input-box {{
            display:flex;
            padding:10px;
            border-top:1px solid #00c8ff;
        }}

        input {{
            flex:1;
            padding:15px;
            border:none;
            border-radius:10px;
            background:#00111f;
            color:#00c8ff;
            outline:none;
            border:1px solid #00c8ff;
        }}

        button {{
            padding:15px;
            margin-left:10px;
            border:none;
            border-radius:10px;
            background:#00c8ff;
            color:black;
            font-weight:bold;
            cursor:pointer;
            box-shadow:0 0 10px #00c8ff;
        }}

        button:hover {{
            background:#0099cc;
        }}
    </style>

    <div class="container">
        <div class="chat-box" id="chat">
            {historico}
        </div>

        <form method="post" class="input-box">
            <input name="pergunta" placeholder="{t("Digite comando...")}">
            <button>{t("EXECUTAR")}</button>
        </form>
    </div>

    <script>
        var chat = document.getElementById("chat");
        chat.scrollTop = chat.scrollHeight;
    </script>
    """
