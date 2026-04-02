from flask import Blueprint, request, session, redirect
from openai import OpenAI
from banco import conectar, devolver_conexao
import os

ia_bp = Blueprint("ia_bp", __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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


@ia_bp.route("/ia", methods=["GET", "POST"])
def ia():
    if "user" not in session:
        return redirect("/")

    resposta = ""

    if request.method == "POST":
        pergunta = request.form.get("pergunta")

        dados = pegar_estoque()
        texto = "\n".join([f"{p}: {q}" for p, q in dados])

        prompt = f"""
        Você é uma IA especialista em estoque.

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

    return f"""
    <div style='color:#00ff00'>
        <h2>🤖 IA DO SISTEMA</h2>

        <form method='post'>
            <input name='pergunta' placeholder='Pergunte algo...' style='width:300px'>
            <button>Enviar</button>
        </form>

        <pre>{resposta}</pre>
    </div>
    """
