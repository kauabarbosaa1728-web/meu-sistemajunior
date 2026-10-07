import json
from datetime import datetime


def render_dashboard(
    total_produtos,
    total_qtd,
    total_transferencias,
    usuarios_online,
    grafico_labels,
    grafico_valores,
    quantidade_baixo_estoque,
    baixo_produtos
):

    agora = datetime.now()

    nome_mes = [
        "",
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro"
    ][agora.month]

    # ========================================================
    # PREPARA DADOS
    # ========================================================

    labels_json = json.dumps(
        grafico_labels,
        ensure_ascii=False
    )

    valores_json = json.dumps(
        grafico_valores
    )

    # ========================================================
    # ALERTA
    # ========================================================

    if quantidade_baixo_estoque > 0:

        alerta_display = "flex"

        alerta_texto = (
            f"⚠️ Atenção: "
            f"{quantidade_baixo_estoque} "
            f"produto(s) com estoque abaixo de 10 unidades."
        )

    else:

        alerta_display = "none"

        alerta_texto = (
            "✓ Estoque saudável"
        )

    # ========================================================
    # HTML
    # ========================================================

    html = f"""

<style>

/* ==========================================================
   DASHBOARD PRINCIPAL
   ========================================================== */

.dashboard-novo {{

    width:100%;

    padding:10px 0 30px 0;

    color:#e2e8f0;

    box-sizing:border-box;
}}


/* ==========================================================
   CABEÇALHO
   ========================================================== */

.dashboard-cabecalho {{

    display:flex;

    justify-content:space-between;

    align-items:center;

    gap:20px;

    margin-bottom:22px;

    flex-wrap:wrap;
}}


.dashboard-titulo h2 {{

    margin:0;

    font-size:25px;

    color:#ffffff;

    font-weight:700;
}}


.dashboard-subtitulo {{

    margin-top:7px;

    color:#64748b;

    font-size:13px;
}}


.dashboard-live {{

    display:inline-flex;

    align-items:center;

    gap:6px;

    margin-left:8px;

    padding:5px 10px;

    border-radius:20px;

    background:rgba(34,197,94,0.10);

    border:1px solid rgba(34,197,94,0.25);

    color:#22c55e;

    font-size:11px;

    font-weight:700;
}}


/* ==========================================================
   FILTRO
   ========================================================== */

.dashboard-filtro {{

    display:flex;

    align-items:end;

    gap:10px;

    flex-wrap:wrap;
}}


.dashboard-campo {{

    display:flex;

    flex-direction:column;

    gap:5px;
}}


.dashboard-campo label {{

    color:#64748b;

    font-size:11px;

    font-weight:600;
}}


.dashboard-campo input {{

    width:130px;

    padding:10px 12px;

    border-radius:8px;

    border:1px solid #1e293b;

    background:#020617;

    color:#ffffff;

    outline:none;

    box-sizing:border-box;
}}


.dashboard-campo input:focus {{

    border-color:#38bdf8;
}}


.dashboard-filtro button {{

    padding:10px 18px;

    border:none;

    border-radius:8px;

    background:#2563eb;

    color:#ffffff;

    font-weight:700;

    cursor:pointer;

    transition:0.2s;
}}


.dashboard-filtro button:hover {{

    transform:translateY(-1px);

    background:#3b82f6;
}}


/* ==========================================================
   CARDS
   ========================================================== */

.dashboard-cards {{

    display:grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap:15px;

    margin-bottom:18px;
}}


.dashboard-card {{

    background:
        linear-gradient(
            145deg,
            #020617,
            #0f172a
        );

    border:1px solid #1e293b;

    border-radius:14px;

    padding:20px;

    box-shadow:
        0 10px 25px
        rgba(0,0,0,0.25);

    transition:0.2s;
}}


.dashboard-card:hover {{

    transform:translateY(-2px);

    border-color:#334155;
}}


.dashboard-card-topo {{

    display:flex;

    justify-content:space-between;

    align-items:center;

    margin-bottom:10px;
}}


.dashboard-card-icone {{

    width:34px;

    height:34px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:9px;

    background:rgba(56,189,248,0.10);

    font-size:16px;
}}


.dashboard-card h3 {{

    margin:0;

    color:#ffffff;

    font-size:27px;

    font-weight:700;
}}


.dashboard-card p {{

    margin:5px 0 0 0;

    color:#64748b;

    font-size:12px;
}}


/* ==========================================================
   ALERTA
   ========================================================== */

.dashboard-alerta {{

    display:{alerta_display};

    align-items:center;

    gap:10px;

    margin-bottom:18px;

    padding:13px 16px;

    border-radius:10px;

    background:rgba(239,68,68,0.08);

    border:1px solid rgba(239,68,68,0.25);

    color:#fca5a5;

    font-size:13px;

    font-weight:600;
}}


/* ==========================================================
   GRÁFICO INTELIGENTE
   ========================================================== */

.dashboard-grafico-box {{

    background:
        linear-gradient(
            145deg,
            #020617,
            #0f172a
        );

    border:1px solid #1e293b;

    border-radius:16px;

    padding:20px;

    box-shadow:
        0 10px 30px
        rgba(0,0,0,0.30);

    min-height:430px;
}}


.dashboard-grafico-cabecalho {{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

    gap:15px;

    margin-bottom:18px;
}}


.dashboard-grafico-titulo h3 {{

    margin:0;

    color:#ffffff;

    font-size:17px;
}}


.dashboard-grafico-titulo p {{

    margin:5px 0 0 0;

    color:#64748b;

    font-size:12px;
}}


.dashboard-indicador {{

    padding:7px 11px;

    border-radius:8px;

    background:rgba(56,189,248,0.08);

    border:1px solid rgba(56,189,248,0.18);

    color:#38bdf8;

    font-size:11px;

    white-space:nowrap;
}}


.dashboard-grafico-area {{

    position:relative;

    height:340px;

    width:100%;
}}


.dashboard-grafico-area canvas {{

    width:100% !important;

    height:100% !important;
}}


/* ==========================================================
   RESUMO ESTOQUE BAIXO
   ========================================================== */

.dashboard-resumo {{

    display:grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap:12px;

    margin-top:15px;
}}


.dashboard-produto-baixo {{

    padding:12px;

    border-radius:10px;

    background:#020617;

    border:1px solid #1e293b;

    display:flex;

    justify-content:space-between;

    align-items:center;

    gap:10px;
}}


.dashboard-produto-nome {{

    color:#cbd5e1;

    font-size:12px;

    overflow:hidden;

    text-overflow:ellipsis;

    white-space:nowrap;
}}


.dashboard-produto-qtd {{

    color:#ef4444;

    font-weight:700;

    font-size:12px;
}}


/* ==========================================================
   RESPONSIVO
   ========================================================== */

@media(max-width:900px) {{

    .dashboard-cards {{

        grid-template-columns:
            repeat(2, 1fr);

    }}

    .dashboard-resumo {{

        grid-template-columns:
            repeat(2, 1fr);

    }}

}}


@media(max-width:600px) {{

    .dashboard-cards {{

        grid-template-columns:
            1fr;

    }}

    .dashboard-resumo {{

        grid-template-columns:
            1fr;

    }}

    .dashboard-cabecalho {{

        align-items:stretch;

    }}

    .dashboard-filtro {{

        width:100%;

    }}

    .dashboard-campo input {{

        width:100%;

    }}

}}


</style>


<div class="dashboard-novo">


    <!-- =====================================================
         CABEÇALHO
         ===================================================== -->

    <div class="dashboard-cabecalho">

        <div class="dashboard-titulo">

            <h2>

                📊 Dashboard Executivo

                <span
                    class="dashboard-live"
                    id="statusDashboard"
                >
                    ● AO VIVO
                </span>

            </h2>

            <div class="dashboard-subtitulo">

                Visão inteligente do estoque •
                {nome_mes} {agora.year}

            </div>

        </div>


        <form
            method="get"
            class="dashboard-filtro"
        >

            <div class="dashboard-campo">

                <label>
                    De
                </label>

                <input
                    type="text"
                    class="calendario-input"
                    name="inicio"
                    placeholder="Selecionar"
                >

            </div>


            <div class="dashboard-campo">

                <label>
                    Até
                </label>

                <input
                    type="text"
                    class="calendario-input"
                    name="fim"
                    placeholder="Selecionar"
                >

            </div>


            <button type="submit">
                Filtrar
            </button>

        </form>

    </div>


    <!-- =====================================================
         CARDS
         ===================================================== -->

    <div class="dashboard-cards">


        <!-- PRODUTOS -->

        <div class="dashboard-card">

            <div class="dashboard-card-topo">

                <div>

                    <h3 id="kpiTotalProdutos">
                        {total_produtos}
                    </h3>

                    <p>
                        Produtos cadastrados
                    </p>

                </div>

                <div class="dashboard-card-icone">
                    📦
                </div>

            </div>

        </div>


        <!-- QUANTIDADE -->

        <div class="dashboard-card">

            <div class="dashboard-card-topo">

                <div>

                    <h3 id="kpiTotalQtd">
                        {total_qtd}
                    </h3>

                    <p>
                        Quantidade em estoque
                    </p>

                </div>

                <div class="dashboard-card-icone">
                    📊
                </div>

            </div>

        </div>


        <!-- MOVIMENTAÇÕES -->

        <div class="dashboard-card">

            <div class="dashboard-card-topo">

                <div>

                    <h3 id="kpiTotalTransferencias">
                        {total_transferencias}
                    </h3>

                    <p>
                        Movimentações
                    </p>

                </div>

                <div class="dashboard-card-icone">
                    🔄
                </div>

            </div>

        </div>


        <!-- USUÁRIOS -->

        <div class="dashboard-card">

            <div class="dashboard-card-topo">

                <div>

                    <h3 id="kpiUsuariosOnline">
                        {usuarios_online}
                    </h3>

                    <p>

                        <span
                            id="statusUsuarios"
                        >
                            ●
                        </span>

                        <span id="textoUsuarios">

                            {'Online' if usuarios_online > 0 else 'Offline'}

                        </span>

                    </p>

                </div>

                <div class="dashboard-card-icone">
                    👥
                </div>

            </div>

        </div>


    </div>


    <!-- =====================================================
         ALERTA
         ===================================================== -->

    <div
        class="dashboard-alerta"
        id="alertaDashboard"
    >

        <span id="textoAlertaDashboard">
            {alerta_texto}
        </span>

    </div>


    <!-- =====================================================
         GRÁFICO INTELIGENTE
         ===================================================== -->

    <div class="dashboard-grafico-box">


        <div class="dashboard-grafico-cabecalho">

            <div class="dashboard-grafico-titulo">

                <h3>
                    🧠 Visão Inteligente do Estoque
                </h3>

                <p>
                    Produtos com maior quantidade em estoque.
                    A linha indica o limite de alerta de 10 unidades.
                </p>

            </div>


            <div
                class="dashboard-indicador"
                id="indicadorEstoque"
            >

                Limite: 10 unidades

            </div>

        </div>


        <div class="dashboard-grafico-area">

            <canvas
                id="graficoInteligente"
            ></canvas>

        </div>


    </div>


    <!-- =====================================================
         PRODUTOS COM ESTOQUE BAIXO
         ===================================================== -->

    <div
        class="dashboard-resumo"
        id="resumoEstoqueBaixo"
    >

"""

    # ========================================================
    # PRODUTOS COM ESTOQUE BAIXO
    # ========================================================

    for produto in baixo_produtos:

        html += f"""

        <div class="dashboard-produto-baixo">

            <span class="dashboard-produto-nome">

                {produto["produto"]}

            </span>

            <span class="dashboard-produto-qtd">

                {produto["quantidade"]} un.

            </span>

        </div>

        """

    html += """

    </div>


</div>


<!-- ==========================================================
     FLATPICKR
     ========================================================== -->

<link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css"
>

<script
    src="https://cdn.jsdelivr.net/npm/flatpickr"
></script>

<script
    src="https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/pt.js"
></script>


<!-- ==========================================================
     CHART.JS
     ========================================================== -->

<script
    src="https://cdn.jsdelivr.net/npm/chart.js"
></script>


<script>


// ==========================================================
// FLATPICKR
// ==========================================================

flatpickr(
    ".calendario-input",
    {

        dateFormat: "Y-m-d",

        locale: "pt"

    }
);


// ==========================================================
// DADOS INICIAIS DO GRÁFICO
// ==========================================================

const labelsInicial = """ + labels_json + """;

const valoresIniciais = """ + valores_json + """;


// ==========================================================
// FUNÇÃO PARA DEFINIR CORES INTELIGENTES
// ==========================================================

function gerarCores(valores) {

    return valores.map(function(valor) {

        if (Number(valor) < 10) {

            return "#ef4444";

        }

        if (Number(valor) < 20) {

            return "#f59e0b";

        }

        return "#38bdf8";

    });

}


// ==========================================================
// GRÁFICO INTELIGENTE
// ==========================================================

const elementoGrafico =
    document.getElementById(
        "graficoInteligente"
    );


let graficoInteligente = null;


if (elementoGrafico) {

    graficoInteligente = new Chart(
        elementoGrafico,
        {

            data: {

                labels: labelsInicial,

                datasets: [

                    {

                        type: "bar",

                        label: "Quantidade em estoque",

                        data: valoresIniciais,

                        backgroundColor:
                            gerarCores(valoresIniciais),

                        borderRadius: 8,

                        borderSkipped: false

                    },

                    {

                        type: "line",

                        label: "Limite de alerta",

                        data: labelsInicial.map(
                            function() {
                                return 10;
                            }
                        ),

                        borderColor: "#ef4444",

                        backgroundColor:
                            "rgba(239,68,68,0.08)",

                        borderWidth: 2,

                        borderDash: [6, 6],

                        pointRadius: 0,

                        fill: false,

                        tension: 0

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                interaction: {

                    mode: "index",

                    intersect: false

                },

                plugins: {

                    legend: {

                        position: "top",

                        labels: {

                            color: "#cbd5e1",

                            usePointStyle: true,

                            padding: 18

                        }

                    },

                    tooltip: {

                        backgroundColor: "#020617",

                        borderColor: "#1e293b",

                        borderWidth: 1,

                        titleColor: "#ffffff",

                        bodyColor: "#cbd5e1",

                        padding: 12

                    }

                },

                scales: {

                    x: {

                        ticks: {

                            color: "#94a3b8",

                            maxRotation: 35,

                            minRotation: 0

                        },

                        grid: {

                            color:
                                "rgba(255,255,255,0.04)"

                        }

                    },

                    y: {

                        beginAtZero: true,

                        ticks: {

                            color: "#94a3b8"

                        },

                        grid: {

                            color:
                                "rgba(255,255,255,0.05)"

                        }

                    }

                }

            }

        }
    );

}


// ==========================================================
// ATUALIZAÇÃO AUTOMÁTICA
// ==========================================================

async function atualizarDashboard() {

    try {

        const parametros =
            new URLSearchParams();


        const campoInicio =
            document.querySelector(
                'input[name="inicio"]'
            );


        const campoFim =
            document.querySelector(
                'input[name="fim"]'
            );


        if (
            campoInicio &&
            campoInicio.value &&
            campoFim &&
            campoFim.value
        ) {

            parametros.set(
                "inicio",
                campoInicio.value
            );

            parametros.set(
                "fim",
                campoFim.value
            );

        }


        const resposta =
            await fetch(
                "/painel/dados?" +
                parametros.toString(),
                {
                    cache: "no-store"
                }
            );


        if (!resposta.ok) {

            console.log(
                "Dashboard retornou:",
                resposta.status
            );

            return;

        }


        const dados =
            await resposta.json();


        // ==================================================
        // KPI PRODUTOS
        // ==================================================

        const totalProdutos =
            document.getElementById(
                "kpiTotalProdutos"
            );


        if (totalProdutos) {

            totalProdutos.textContent =
                dados.total_produtos;

        }


        // ==================================================
        // KPI QUANTIDADE
        // ==================================================

        const totalQtd =
            document.getElementById(
                "kpiTotalQtd"
            );


        if (totalQtd) {

            totalQtd.textContent =
                dados.total_qtd;

        }


        // ==================================================
        // KPI TRANSFERÊNCIAS
        // ==================================================

        const totalTransferencias =
            document.getElementById(
                "kpiTotalTransferencias"
            );


        if (totalTransferencias) {

            totalTransferencias.textContent =
                dados.total_transferencias;

        }


        // ==================================================
        // KPI USUÁRIOS
        // ==================================================

        const usuariosOnline =
            document.getElementById(
                "kpiUsuariosOnline"
            );


        if (usuariosOnline) {

            usuariosOnline.textContent =
                dados.usuarios_online;

        }


        // ==================================================
        // STATUS USUÁRIOS
        // ==================================================

        const textoUsuarios =
            document.getElementById(
                "textoUsuarios"
            );


        if (textoUsuarios) {

            textoUsuarios.textContent =
                dados.usuarios_online > 0
                    ? "Online"
                    : "Offline";

        }


        const statusUsuarios =
            document.getElementById(
                "statusUsuarios"
            );


        if (statusUsuarios) {

            statusUsuarios.style.color =
                dados.usuarios_online > 0
                    ? "#22c55e"
                    : "#ef4444";

        }


        // ==================================================
        // ATUALIZA GRÁFICO
        // ==================================================

        if (graficoInteligente) {

            graficoInteligente.data.labels =
                dados.grafico_labels;


            graficoInteligente.data.datasets[0].data =
                dados.grafico_valores;


            graficoInteligente.data.datasets[0]
                .backgroundColor =
                gerarCores(
                    dados.grafico_valores
                );


            graficoInteligente.data.datasets[1].data =
                dados.grafico_labels.map(
                    function() {
                        return 10;
                    }
                );


            graficoInteligente.update();

        }


        // ==================================================
        // ALERTA DE ESTOQUE
        // ==================================================

        const alerta =
            document.getElementById(
                "alertaDashboard"
            );


        const textoAlerta =
            document.getElementById(
                "textoAlertaDashboard"
            );


        if (
            dados.quantidade_baixo_estoque > 0
        ) {

            if (alerta) {

                alerta.style.display =
                    "flex";

            }


            if (textoAlerta) {

                textoAlerta.textContent =
                    "⚠️ Atenção: " +
                    dados.quantidade_baixo_estoque +
                    " produto(s) com estoque abaixo de 10 unidades.";

            }

        } else {

            if (alerta) {

                alerta.style.display =
                    "none";

            }

        }


        // ==================================================
        // ATUALIZA LISTA DE ESTOQUE BAIXO
        // ==================================================

        const resumo =
            document.getElementById(
                "resumoEstoqueBaixo"
            );


        if (resumo) {

            resumo.innerHTML = "";


            dados.baixo_produtos.forEach(
                function(produto) {

                    const item =
                        document.createElement(
                            "div"
                        );


                    item.className =
                        "dashboard-produto-baixo";


                    item.innerHTML =

                        '<span class="dashboard-produto-nome">' +

                        produto.produto +

                        '</span>' +

                        '<span class="dashboard-produto-qtd">' +

                        produto.quantidade +

                        ' un.</span>';


                    resumo.appendChild(item);

                }
            );

        }


        // ==================================================
        // STATUS AO VIVO
        // ==================================================

        const status =
            document.getElementById(
                "statusDashboard"
            );


        if (status) {

            status.textContent =
                "● ATUALIZADO";


            setTimeout(
                function() {

                    status.textContent =
                        "● AO VIVO";

                },
                1000
            );

        }

    }

    catch (erro) {

        console.log(
            "Erro ao atualizar Dashboard:",
            erro
        );

    }

}


// ==========================================================
// PRIMEIRA ATUALIZAÇÃO
// ==========================================================

atualizarDashboard();


// ==========================================================
// ATUALIZA A CADA 3 SEGUNDOS
// ==========================================================

setInterval(
    atualizarDashboard,
    3000
);


</script>

"""

    return html
