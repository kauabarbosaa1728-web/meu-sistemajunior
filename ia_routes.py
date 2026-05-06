from flask import Blueprint, request, session, redirect
from banco import conectar, devolver_conexao
from tradutor import t
import difflib

ia_bp = Blueprint("ia_bp", __name__)


# ================= NORMALIZAR =================
def normalizar(txt):
    return txt.lower().strip()


# ================= SIMILARIDADE =================
def parecido(pergunta, lista):
    return difflib.get_close_matches(pergunta, lista, n=1, cutoff=0.5)


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
    match = difflib.get_close_matches(pergunta, perguntas, n=1, cutoff=0.6)

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

        if len(pergunta) > 5:
            cursor.execute(
                "INSERT INTO ia_aprendizado (pergunta, resposta) VALUES (%s, %s)",
                (pergunta, resposta)
            )

        conn.commit()
    except:
        pass

    devolver_conexao(conn)


# ================= IA GRATUITA TURBINADA =================
def ia_free(pergunta):
    pergunta_lower = normalizar(pergunta)

    # 🔥 aprendizado
    aprendido = buscar_aprendizado(pergunta_lower)
    if aprendido:
        return t(aprendido)

    conn = conectar()
    cursor = conn.cursor()

    # ===== PALAVRAS CHAVE =====
    estoque_kw = ["estoque", "produto", "produtos", "itens", "quantidade"]
    financeiro_kw = ["financeiro", "saldo", "dinheiro", "lucro", "entrada", "saida"]
    saudacao_kw = ["oi", "ola", "hello", "hola", "eai", "fala"]
    ajuda_kw = ["ajuda", "menu", "opções", "opcoes"]

    # ===== SAUDAÇÃO =====
    if any(p in pergunta_lower for p in saudacao_kw):
        devolver_conexao(conn)
        return t("👋 Olá! Posso te ajudar com estoque, financeiro, veículos e relatórios.")

    # ===== AJUDA =====
    if any(p in pergunta_lower for p in ajuda_kw):
        devolver_conexao(conn)
        return t("📊 Você pode perguntar sobre estoque, financeiro, produtos ou relatórios.")

    # ===== ESTOQUE =====
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

            texto = f"📦 Você tem {total} produtos com {qtd} itens.\n"

            if top:
                texto += "🏆 Top produtos:\n"
                for p, q in top:
                    texto += f"- {p}: {q}\n"

            salvar_aprendizado(pergunta_lower, texto)
            devolver_conexao(conn)
            return t(texto)

        except:
            devolver_conexao(conn)
            return t("Erro ao consultar estoque.")

    # ===== FINANCEIRO =====
    if any(p in pergunta_lower for p in financeiro_kw):
        try:
            cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='entrada'")
            entrada = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='saida'")
            saida = cursor.fetchone()[0]

            saldo = entrada - saida

            texto = f"💰 Entradas: R$ {entrada:.2f}\n"
            texto += f"💸 Saídas: R$ {saida:.2f}\n"
            texto += f"📊 Saldo: R$ {saldo:.2f}"

            salvar_aprendizado(pergunta_lower, texto)
            devolver_conexao(conn)
            return t(texto)

        except:
            devolver_conexao(conn)
            return t("Erro ao consultar financeiro.")

    # ===== SIMILARIDADE =====
    possiveis = ["estoque", "financeiro", "produtos", "saldo"]
    match = parecido(pergunta_lower, possiveis)

    if match:
        return t(f"🤖 Você quis dizer algo sobre {match[0]}?")

    devolver_conexao(conn)

    # ===== DEFAULT =====
    resp = "🤖 Não entendi totalmente, mas posso te ajudar com estoque, financeiro ou produtos."
    salvar_aprendizado(pergunta_lower, resp)

    return t(resp)


# ================= IA PRINCIPAL =================
def resposta_inteligente(pergunta):
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

    # HISTÓRICO
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
            white-space:pre-line;
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
