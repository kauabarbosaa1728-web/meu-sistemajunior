from flask import Blueprint, request, session, redirect, render_template_string
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

# ================= IA =================
def ia_free(pergunta):
    pergunta_lower = normalizar(pergunta)

    aprendido = buscar_aprendizado(pergunta_lower)
    if aprendido:
        return t(aprendido)

    conn = conectar()
    cursor = conn.cursor()

    estoque_kw = ["estoque", "produto", "produtos", "itens", "quantidade"]
    financeiro_kw = ["financeiro", "saldo", "dinheiro", "lucro", "entrada", "saida"]
    saudacao_kw = ["oi", "ola", "hello", "eai", "fala"]
    ajuda_kw = ["ajuda", "menu", "opções", "opcoes"]

    if any(p in pergunta_lower for p in saudacao_kw):
        devolver_conexao(conn)
        return t("👋 Olá! Posso te ajudar com o sistema.")

    if any(p in pergunta_lower for p in ajuda_kw):
        devolver_conexao(conn)
        return t("📊 Pergunte sobre estoque ou financeiro.")

    if any(p in pergunta_lower for p in estoque_kw):
        try:
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(quantidade),0) FROM estoque")
            total, qtd = cursor.fetchone()
            devolver_conexao(conn)
            return t(f"📦 Estoque: {total} produtos | {qtd} itens")
        except:
            devolver_conexao(conn)
            return t("Erro estoque.")

    if any(p in pergunta_lower for p in financeiro_kw):
        try:
            cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='entrada'")
            entrada = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='saida'")
            saida = cursor.fetchone()[0]

            saldo = entrada - saida
            devolver_conexao(conn)

            return t(f"💰 Entrada: {entrada} | Saída: {saida} | Saldo: {saldo}")
        except:
            devolver_conexao(conn)
            return t("Erro financeiro.")

    devolver_conexao(conn)

    resp = "🤖 Não entendi."
    salvar_aprendizado(pergunta_lower, resp)
    return t(resp)

# ================= DASHBOARD NOVO =================
@ia_bp.route("/dashboard")
def dashboard():

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total_estoque = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantidade),0) FROM estoque")
        itens_estoque = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='entrada'")
        entrada = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(valor),0) FROM financeiro WHERE tipo='saida'")
        saida = cursor.fetchone()[0]

        saldo = entrada - saida

    except:
        total_estoque = 0
        itens_estoque = 0
        entrada = 0
        saida = 0
        saldo = 0

    devolver_conexao(conn)

    html = f"""
    <style>
    body {{
        margin:0;
        font-family:Arial;
        background:#0a0f1c;
        color:white;
    }}

    .container {{
        padding:20px;
    }}

    .title {{
        font-size:28px;
        margin-bottom:20px;
        color:#38bdf8;
    }}

    .grid {{
        display:grid;
        grid-template-columns:repeat(4,1fr);
        gap:15px;
    }}

    .card {{
        background:#111827;
        padding:20px;
        border-radius:12px;
        border:1px solid #1f2937;
        box-shadow:0 0 15px #0ea5e9;
    }}

    .card h2 {{
        font-size:18px;
        color:#94a3b8;
    }}

    .card p {{
        font-size:22px;
        margin-top:10px;
        color:#38bdf8;
    }}

    a {{
        color:white;
        text-decoration:none;
    }}
    </style>

    <div class="container">

        <div class="title">📊 DASHBOARD SISTEMA</div>

        <div class="grid">

            <div class="card">
                <h2>📦 Produtos</h2>
                <p>{total_estoque}</p>
            </div>

            <div class="card">
                <h2>📊 Itens Estoque</h2>
                <p>{itens_estoque}</p>
            </div>

            <div class="card">
                <h2>💰 Entradas</h2>
                <p>R$ {entrada}</p>
            </div>

            <div class="card">
                <h2>💸 Saídas</h2>
                <p>R$ {saida}</p>
            </div>

            <div class="card">
                <h2>📈 Saldo</h2>
                <p>R$ {saldo}</p>
            </div>

        </div>

        <br><br>
        <a href="/ia">🤖 Ir para IA</a>

    </div>
    """

    return render_template_string(html)
