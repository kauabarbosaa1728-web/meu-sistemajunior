from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao
from layout import container

veiculos_bp = Blueprint("veiculos_bp", __name__)

@veiculos_bp.route("/veiculos", methods=["GET", "POST"])
def veiculos():

    if "user" not in session:
        return redirect("/")

    empresa_id = session.get("empresa_id")

    conn = conectar()
    cursor = conn.cursor()

    # ================= CADASTRAR / EDITAR =================
    if request.method == "POST":
        id_edit = request.form.get("id_edit")

        motorista = request.form.get("motorista")
        nome = request.form.get("nome")
        placa = request.form.get("placa")
        equipe = request.form.get("equipe")

        if id_edit:
            cursor.execute("""
            UPDATE veiculos
            SET motorista=%s, nome=%s, placa=%s, equipe=%s
            WHERE id=%s AND empresa_id=%s
            """, (motorista, nome, placa, equipe, id_edit, empresa_id))
        else:
            cursor.execute("""
            INSERT INTO veiculos (motorista, nome, placa, equipe, empresa_id)
            VALUES (%s, %s, %s, %s, %s)
            """, (motorista, nome, placa, equipe, empresa_id))

        conn.commit()
        return redirect("/veiculos")

    # ================= BUSCA =================
    busca = request.args.get("busca", "")

    if busca:
        cursor.execute("""
        SELECT id, motorista, nome, placa, equipe
        FROM veiculos
        WHERE empresa_id=%s AND placa ILIKE %s
        ORDER BY id DESC
        """, (empresa_id, f"%{busca}%"))
    else:
        cursor.execute("""
        SELECT id, motorista, nome, placa, equipe
        FROM veiculos
        WHERE empresa_id=%s
        ORDER BY id DESC
        """, (empresa_id,))

    dados = cursor.fetchall()

    # ================= DASHBOARD =================
    total = len(dados)
    rede = len([v for v in dados if v[4] == "Rede"])
    suporte = len([v for v in dados if v[4] == "Suporte"])
    motorista_total = len([v for v in dados if v[4] == "Motorista"])

    # ================= LISTA =================
    lista = ""

    for v in dados:
        lista += f"""
        <div class="item">
            <h3>🚗 {v[2]}</h3>
            <p>👤 Motorista: {v[1]}</p>
            <p>🔢 Placa: {v[3]}</p>
            <p>🏢 Equipe: {v[4]}</p>

            <a href="/editar-veiculo/{v[0]}">✏️ Editar</a> |
            <a href="/deletar-veiculo/{v[0]}" onclick="return confirm('Excluir?')">🗑️ Deletar</a>
        </div>
        """

    cursor.close()
    devolver_conexao(conn)

    return container(f"""

<style>

.card {{
    background:#0f172a;
    padding:20px;
    border-radius:12px;
    margin-bottom:20px;
}}

.grid {{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
    gap:10px;
}}

input, select {{
    padding:10px;
    border-radius:8px;
    border:none;
    background:#020617;
    color:white;
}}

.btn {{
    margin-top:10px;
    padding:12px;
    width:100%;
    background:#2563eb;
    border:none;
    border-radius:8px;
    color:white;
    font-weight:bold;
}}

.item {{
    background:#020617;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
    border:1px solid #1e293b;
}}

.dashboard {{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
    gap:10px;
    margin-bottom:20px;
}}

.box {{
    background:#020617;
    padding:15px;
    border-radius:10px;
    text-align:center;
}}

</style>

<h2>🚗 Veículos</h2>

<div class="dashboard">
<div class="box">Total<br><b>{total}</b></div>
<div class="box">Rede<br><b>{rede}</b></div>
<div class="box">Suporte<br><b>{suporte}</b></div>
<div class="box">Motorista<br><b>{motorista_total}</b></div>
</div>

<div class="card">

<form method="GET">
<input name="busca" placeholder="Buscar por placa..." value="{busca}">
<button class="btn">🔍 Buscar</button>
</form>

</div>

<div class="card">

<form method="POST">

<div class="grid">
<input name="motorista" placeholder="Motorista" required>
<input name="nome" placeholder="Veículo" required>
<input name="placa" placeholder="Placa" required>

<select name="equipe" required>
<option value="">Equipe</option>
<option>Rede</option>
<option>Suporte</option>
<option>Motorista</option>
</select>
</div>

<button class="btn">💾 Salvar</button>

</form>

</div>

<h3>📋 Lista</h3>

<div class="card">
{lista if lista else "Nenhum veículo"}
</div>

""")


# ================= DELETAR =================
@veiculos_bp.route("/deletar-veiculo/<int:id>")
def deletar(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM veiculos WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    devolver_conexao(conn)

    return redirect("/veiculos")


# ================= EDITAR =================
@veiculos_bp.route("/editar-veiculo/<int:id>")
def editar(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT motorista, nome, placa, equipe
    FROM veiculos WHERE id=%s
    """, (id,))

    v = cursor.fetchone()

    cursor.close()
    devolver_conexao(conn)

    return container(f"""

<h2>✏️ Editar Veículo</h2>

<form method="POST" action="/veiculos">

<input type="hidden" name="id_edit" value="{id}">

<input name="motorista" value="{v[0]}">
<input name="nome" value="{v[1]}">
<input name="placa" value="{v[2]}">

<select name="equipe">
<option {"selected" if v[3]=='Rede' else ""}>Rede</option>
<option {"selected" if v[3]=='Suporte' else ""}>Suporte</option>
<option {"selected" if v[3]=='Motorista' else ""}>Motorista</option>
</select>

<button>Salvar</button>

</form>

""")
