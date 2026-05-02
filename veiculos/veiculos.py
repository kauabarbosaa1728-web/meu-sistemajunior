from flask import Blueprint, request, redirect, session
from banco import conectar, devolver_conexao
from layout import container

veiculos_bp = Blueprint("veiculos_bp", __name__)

@veiculos_bp.route("/veiculos", methods=["GET", "POST"])
def veiculos():

    if "user" not in session:
        return redirect("/")

    empresa_id = session.get("empresa_id")

    if not empresa_id:
        return container("<h2>❌ Empresa não definida</h2>")

    conn = conectar()
    if conn is None:
        return "Erro ao conectar banco"

    try:
        cursor = conn.cursor()

        # ================= CADASTRAR =================
        if request.method == "POST":
            motorista = request.form.get("motorista")
            nome = request.form.get("nome")
            placa = request.form.get("placa")
            equipe = request.form.get("equipe")

            cursor.execute("""
            INSERT INTO veiculos (motorista, nome, placa, equipe, empresa_id)
            VALUES (%s, %s, %s, %s, %s)
            """, (motorista, nome, placa, equipe, empresa_id))

            conn.commit()
            return redirect("/veiculos")

        # ================= LISTAR =================
        cursor.execute("""
        SELECT motorista, nome, placa, equipe 
        FROM veiculos
        WHERE empresa_id=%s
        ORDER BY id DESC
        """, (empresa_id,))

        dados = cursor.fetchall()

        lista = ""

        for v in dados:
            lista += f"""
            <div class="item">
                <h3>🚗 {v[1]}</h3>
                <p>👤 Motorista: {v[0]}</p>
                <p>🔢 Placa: {v[2]}</p>
                <p>🏢 Equipe: {v[3]}</p>
            </div>
            """

    except Exception as e:
        return f"ERRO: {str(e)}"

    finally:
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

.form-grid {{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
    gap:12px;
}}

.campo {{
    display:flex;
    flex-direction:column;
}}

.campo label {{
    margin-bottom:5px;
    font-size:13px;
    color:#94a3b8;
}}

input, select {{
    padding:10px;
    border-radius:8px;
    border:none;
    background:#020617;
    color:white;
}}

.btn {{
    margin-top:15px;
    padding:12px;
    width:100%;
    background:#2563eb;
    border:none;
    border-radius:8px;
    color:white;
    font-weight:bold;
    cursor:pointer;
}}

.btn:hover {{
    background:#1d4ed8;
}}

.item {{
    background:#020617;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
    border:1px solid #1e293b;
}}

</style>

<h2>🚗 Veículos</h2>

<div class="card">

<form method="POST">

<div class="form-grid">

<div class="campo">
<label>👤 Nome do motorista</label>
<input name="motorista" placeholder="Ex: João Silva" required>
</div>

<div class="campo">
<label>🚗 Nome do veículo</label>
<input name="nome" placeholder="Ex: Saveiro / Fiorino" required>
</div>

<div class="campo">
<label>🔢 Placa completa</label>
<input name="placa" placeholder="ABC-1234" required>
</div>

<div class="campo">
<label>🏢 Equipe</label>
<select name="equipe" required>
<option value="">Selecione</option>
<option>Rede</option>
<option>Suporte</option>
<option>Motorista</option>
</select>
</div>

</div>

<button class="btn">💾 Salvar Veículo</button>

</form>

</div>

<h3>📋 Lista</h3>

<div class="card">
{lista if lista else "<p>Nenhum veículo cadastrado.</p>"}
</div>

""")
