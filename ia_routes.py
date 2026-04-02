from flask import Blueprint, request, session, redirect
from openai import OpenAI
from banco import conectar, devolver_conexao
import os

# ✅ ISSO QUE FALTAVA
ia_bp = Blueprint("ia_bp", __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================= PEGAR ESTOQUE =================
def pegar_estoque():
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT produto, quantidade FROM estoque")
        return cursor.fetchall()
    finally:
        if conn:
            devolver_conexao(conn)


# ================= IA CHAT =================
@ia_bp.route("/ia", methods=["GET", "POST"])
def ia():
    if "user" not in session:
        return redirect("/")

    if "chat" not in session:
        session["chat"] = []

    if request.method == "POST":
        pergunta = request.form.get("pergunta")

        dados = pegar_estoque()
        texto = "\n".join([f"{p}: {q}" for p, q in dados])

        prompt = f"""
        Você é uma IA especialista em gestão de estoque.

        Dados:
        {texto}

        Pergunta:
        {pergunta}
        """

        try:
            chat = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            resposta = chat.choices[0].message.content

        except Exception as e:
            resposta = f"Erro: {str(e)}"

        session["chat"].append(("user", pergunta))
        session["chat"].append(("bot", resposta))

    historico = ""
    for tipo, msg in session["chat"]:
        if tipo == "user":
            historico += f"<div class='msg user'>{msg}</div>"
        else:
            historico += f"<div class='msg bot'>{msg}</div>"

    return f"""
    <style>
        body {{
            background:#000;
            color:#0f0;
            font-family: 'Courier New', monospace;
        }}

        .chat-box {{
            width:80%;
            margin:auto;
            margin-top:20px;
        }}

        .msg {{
            padding:10px;
            margin:10px 0;
            border-radius:10px;
            max-width:70%;
        }}

        .user {{
            background:#003300;
            margin-left:auto;
            text-align:right;
        }}

        .bot {{
            background:#001100;
            margin-right:auto;
        }}

        input {{
            width:80%;
            padding:10px;
            background:black;
            color:#0f0;
            border:1px solid #0f0;
        }}

        button {{
            padding:10px;
            background:#0f0;
            border:none;
            cursor:pointer;
        }}
    </style>

    <div class="chat-box">
        <h2>🤖 Chat IA</h2>

        {historico}

        <form method="post">
            <input name="pergunta" placeholder="Digite sua pergunta...">
            <button>Enviar</button>
        </form>
    </div>
    """
