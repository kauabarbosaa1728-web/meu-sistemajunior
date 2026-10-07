import json
import calendar
from datetime import datetime


def render_dashboard(
    total_produtos,
    total_qtd,
    total_transferencias,
    usuarios_online,
    nomes,
    valores,
    top_nomes,
    top_valores,
    dias_labels,
    dias_valores,
    baixo_nomes,
    baixo_valores,
    calendario
):

    now = datetime.now()

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
    ][now.month]

    mes = now.month
    ano = now.year

    cal = calendar.monthcalendar(ano, mes)

    # ========================================================
    # CALENDÁRIO
    # ========================================================

    html_calendario = f"""
    <div class="box calendario-box" id="calendarioDashboard">

        <div class="topo-cal">
            <span>
                📅 Calendário •
                <span id="nomeMesDashboard">{nome_mes}</span>
                <span id="anoDashboard">{ano}</span>
            </span>
        </div>

        <div class="cal-grid" id="calGridDashboard">
    """

    dias_semana = [
        "Dom",
        "Seg",
        "Ter",
        "Qua",
        "Qui",
        "Sex",
        "Sab"
    ]

    for d in dias_semana:
        html_calendario += f"""
        <div class="dia-semana">
            {d}
        </div>
        """

    for semana in cal:

        for dia in semana:

            if dia == 0:

                html_calendario += """
                <div class="dia vazio"></div>
                """

            else:

                data_str = f"{ano}-{mes:02d}-{dia:02d}"

                info = calendario.get(
                    data_str,
                    {}
                )

                entrada = info.get(
                    "entrada",
                    0
                )

                saida = info.get(
                    "saida",
                    0
                )

                transf = info.get(
                    "transf",
                    0
                )

                total = info.get(
                    "total",
                    0
                )

                hoje_classe = (
                    "hoje"
                    if dia == now.day
                    else ""
                )

                html_calendario += f"""
                <div class="dia {hoje_classe}">

                    <div class="num">
                        {dia}
                    </div>

                    <div class="linha verde">
                        Entrada: {entrada}
                    </div>

                    <div class="linha vermelho">
                        Saída: {saida}
                    </div>

                    <div class="linha azul">
                        Transf: {transf}
                    </div>

                    <div class="total">
                        Total: {total}
                    </div>

                </div>
                """

    html_calendario += """
        </div>
    </div>
    """

    # ========================================================
    # HTML
    # ========================================================

    html = f"""

    <style>

    .calendario-box {{
        margin-top:20px;
    }}

    .topo-cal {{
        color:#94a3b8;
        margin-bottom:10px;
        font-weight:bold;
    }}

    .cal-grid {{
        display:grid;
        grid-template-columns:repeat(7, 1fr);
        gap:8px;
    }}

    .dia-semana {{
        text-align:center;
        font-size:12px;
        color:#64748b;
    }}

    .dia {{
        background:linear-gradient(
            145deg,
            #020617,
            #0f172a
        );

        border:1px solid #1e293b;

        border-radius:12px;

        padding:10px;

        min-height:110px;

        position:relative;

        transition:0.2s;
    }}

    .dia:hover {{
        transform:scale(1.05);

        box-shadow:
            0 0 15px
            rgba(59,130,246,0.3);
    }}

    .dia.hoje {{
        border:2px solid #3b82f6;

        box-shadow:
            0 0 10px #3b82f6;
    }}

    .num {{
        font-weight:bold;
        color:#fff;
        margin-bottom:5px;
    }}

    .linha {{
        font-size:11px;
        margin:2px 0;
    }}

    .verde {{
        color:#22c55e;
    }}

    .vermelho {{
        color:#ef4444;
    }}

    .azul {{
        color:#38bdf8;
    }}

    .total {{
        position:absolute;
        bottom:6px;
        right:10px;

        font-size:12px;

        color:#fff;

        font-weight:bold;
    }}

    .vazio {{
        background:transparent;
        border:none;
    }}

    .grid {{
        display:grid;

        grid-template-columns:
            2fr 1fr;

        grid-template-rows:
            300px 300px;

        gap:20px;

        margin-top:25px;
    }}

    .grid .box:nth-child(1) {{
        grid-row:span 2;
    }}

    .box {{
        background:
            linear-gradient(
                145deg,
                #020617,
                #0f172a
            );

        border:1px solid #1e293b;

        border-radius:16px;

        padding:15px;

        box-shadow:
            0 0 20px
            rgba(0,0,0,0.5);
    }}

    canvas {{
        width:100% !important;
        height:100% !important;
    }}

    </style>


    <div class="wrap">

        <div class="topo-dashboard">

            <div>

                <h2>
                    📊 Dashboard Executivo •
                    {nome_mes} {now.year}

                    <span
                        class="status-live"
                        id="statusDashboard"
                    >
                        ● AO VIVO
                    </span>

                </h2>

                <p class="subtitulo">
                    Dados atualizados em tempo real •
                    Controle total do seu estoque
                </p>

            </div>


            <form
                method="get"
                class="filtro-data"
            >

                <div class="campo">

                    <label>
                        De
                    </label>

                    <input
                        type="text"
                        class="calendario-input"
                        name="inicio"
                        placeholder="Selecionar data"
                    >

                </div>


                <div class="campo">

                    <label>
                        Até
                    </label>

                    <input
                        type="text"
                        class="calendario-input"
                        name="fim"
                        placeholder="Selecionar data"
                    >

                </div>


                <button>
                    Filtrar
                </button>

            </form>

        </div>


        <div
            id="alertaDashboard"
            class="alerta-topo"
            style="display:{'block' if baixo_nomes else 'none'};"
        >
            ⚠️ Atenção:
            <span id="quantidadeBaixoEstoque">
                {len(baixo_nomes)}
            </span>
            produto(s) com estoque baixo
        </div>


        <!-- KPIs -->

        <div class="cards">

            <div class="card">

                <h1
                    class="azul"
                    id="kpiTotalProdutos"
                >
                    {total_produtos}
                </h1>

                <p>
                    Total Produtos
                </p>

            </div>


            <div class="card">

                <h1
                    class="azul"
                    id="kpiTotalQtd"
                >
                    {total_qtd}
                </h1>

                <p>
                    Quantidade
                </p>

            </div>


            <div class="card">

                <h1
                    class="azul"
                    id="kpiTotalTransferencias"
                >
                    {total_transferencias}
                </h1>

                <p>
                    Movimentações
                </p>

            </div>


            <div class="card">

                <h1
                    style="color:#fff"
                    id="kpiUsuariosOnline"
                >
                    {usuarios_online}
                </h1>

                <p>

                    <span
                        class="status {'on' if usuarios_online > 0 else 'off'}"
                        id="statusUsuarios"
                    ></span>

                    <span id="textoUsuarios">
                        {'Online' if usuarios_online > 0 else 'Offline'}
                    </span>

                </p>

            </div>

        </div>


        {html_calendario}


        <!-- GRÁFICOS -->

        <div class="grid">

            <div class="box">
                <canvas id="linha"></canvas>
            </div>

            <div class="box">
                <canvas id="pizza"></canvas>
            </div>

            <div class="box">
                <canvas id="top"></canvas>
            </div>

            <div class="box">
                <canvas id="baixo"></canvas>
            </div>

        </div>

    </div>


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

    <script
        src="https://cdn.jsdelivr.net/npm/chart.js"
    ></script>


    <script>

    // ======================================================
    // FLATPICKR
    // ======================================================

    flatpickr(
        ".calendario-input",
        {{
            dateFormat:"Y-m-d",
            locale:"pt"
        }}
    );


    // ======================================================
    // CONFIGURAÇÃO DOS GRÁFICOS
    // ======================================================

    const cores = [
        "#38bdf8",
        "#60a5fa",
        "#818cf8",
        "#a78bfa",
        "#22d3ee"
    ];


    const configPadrao = {{

        responsive:true,

        maintainAspectRatio:false,

        plugins:{{
            legend:{{
                labels:{{
                    color:"#cbd5e1"
                }}
            }}
        }},

        scales:{{

            x:{{

                ticks:{{
                    color:"#94a3b8"
                }},

                grid:{{
                    color:
                        "rgba(255,255,255,0.05)"
                }}

            }},

            y:{{

                ticks:{{
                    color:"#94a3b8"
                }},

                grid:{{
                    color:
                        "rgba(255,255,255,0.05)"
                }}

            }}

        }}

    }};


    // ======================================================
    // CRIA OS GRÁFICOS
    // ======================================================

    let graficoPizza = new Chart(
        document.getElementById("pizza"),
        {{

            type:"doughnut",

            data:{{

                labels:{json.dumps(nomes)},

                datasets:[{{

                    data:{json.dumps(valores)},

                    backgroundColor:cores,

                    borderWidth:0

                }}]

            }},

            options:{{

                responsive:true,

                maintainAspectRatio:false,

                cutout:"70%",

                plugins:{{

                    legend:{{

                        position:"bottom",

                        labels:{{

                            color:"#cbd5e1"

                        }}

                    }}

                }}

            }}

        }}
    );


    let graficoLinha = new Chart(
        document.getElementById("linha"),
        {{

            type:"line",

            data:{{

                labels:{json.dumps(dias_labels)},

                datasets:[{{

                    data:{json.dumps(dias_valores)},

                    borderColor:"#38bdf8",

                    backgroundColor:
                        "rgba(56,189,248,0.2)",

                    fill:true,

                    borderWidth:3,

                    tension:0.4,

                    pointRadius:4

                }}]

            }},

            options:configPadrao

        }}
    );


    let graficoTop = new Chart(
        document.getElementById("top"),
        {{

            type:"bar",

            data:{{

                labels:{json.dumps(top_nomes)},

                datasets:[{{

                    data:{json.dumps(top_valores)},

                    backgroundColor:"#3b82f6",

                    borderRadius:8

                }}]

            }},

            options:configPadrao

        }}
    );


    let graficoBaixo = new Chart(
        document.getElementById("baixo"),
        {{

            type:"bar",

            data:{{

                labels:{json.dumps(baixo_nomes)},

                datasets:[{{

                    data:{json.dumps(baixo_valores)},

                    backgroundColor:"#ef4444",

                    borderRadius:8

                }}]

            }},

            options:configPadrao

        }}
    );


    // ======================================================
    // 🔥 ATUALIZAÇÃO AUTOMÁTICA
    // ======================================================

    async function atualizarDashboard() {{

        try {{

            const parametros = new URLSearchParams();


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
            ) {{

                parametros.set(
                    "inicio",
                    campoInicio.value
                );

                parametros.set(
                    "fim",
                    campoFim.value
                );

            }}


            const resposta = await fetch(
                "/painel/dados?" +
                parametros.toString(),
                {{
                    cache:"no-store"
                }}
            );


            if (!resposta.ok) {{
                return;
            }}


            const dados =
                await resposta.json();


            // ==============================================
            // KPIs
            // ==============================================

            const totalProdutos =
                document.getElementById(
                    "kpiTotalProdutos"
                );

            const totalQtd =
                document.getElementById(
                    "kpiTotalQtd"
                );

            const totalTransferencias =
                document.getElementById(
                    "kpiTotalTransferencias"
                );

            const usuariosOnline =
                document.getElementById(
                    "kpiUsuariosOnline"
                );


            if (totalProdutos) {{

                totalProdutos.textContent =
                    dados.total_produtos;

            }}


            if (totalQtd) {{

                totalQtd.textContent =
                    dados.total_qtd;

            }}


            if (totalTransferencias) {{

                totalTransferencias.textContent =
                    dados.total_transferencias;

            }}


            if (usuariosOnline) {{

                usuariosOnline.textContent =
                    dados.usuarios_online;

            }}


            // ==============================================
            // USUÁRIOS ONLINE
            // ==============================================

            const statusUsuarios =
                document.getElementById(
                    "statusUsuarios"
                );

            const textoUsuarios =
                document.getElementById(
                    "textoUsuarios"
                );


            if (statusUsuarios) {{

                statusUsuarios.className =
                    "status " +
                    (
                        dados.usuarios_online > 0
                        ? "on"
                        : "off"
                    );

            }}


            if (textoUsuarios) {{

                textoUsuarios.textContent =
                    dados.usuarios_online > 0
                    ? "Online"
                    : "Offline";

            }}


            // ==============================================
            // GRÁFICO PIZZA
            // ==============================================

            graficoPizza.data.labels =
                dados.nomes;

            graficoPizza.data.datasets[0].data =
                dados.valores;

            graficoPizza.update();


            // ==============================================
            // GRÁFICO LINHA
            // ==============================================

            graficoLinha.data.labels =
                dados.dias_labels;

            graficoLinha.data.datasets[0].data =
                dados.dias_valores;

            graficoLinha.update();


            // ==============================================
            // TOP PRODUTOS
            // ==============================================

            graficoTop.data.labels =
                dados.top_nomes;

            graficoTop.data.datasets[0].data =
                dados.top_valores;

            graficoTop.update();


            // ==============================================
            // BAIXO ESTOQUE
            // ==============================================

            graficoBaixo.data.labels =
                dados.baixo_nomes;

            graficoBaixo.data.datasets[0].data =
                dados.baixo_valores;

            graficoBaixo.update();


            // ==============================================
            // ALERTA DE ESTOQUE BAIXO
            // ==============================================

            const alerta =
                document.getElementById(
                    "alertaDashboard"
                );

            const quantidadeBaixo =
                document.getElementById(
                    "quantidadeBaixoEstoque"
                );


            if (dados.baixo_nomes.length > 0) {{

                if (alerta) {{
                    alerta.style.display = "block";
                }}

                if (quantidadeBaixo) {{

                    quantidadeBaixo.textContent =
                        dados.baixo_nomes.length;

                }}

            }} else {{

                if (alerta) {{
                    alerta.style.display = "none";
                }}

            }}


            // ==============================================
            // ATUALIZA CALENDÁRIO
            // ==============================================

            atualizarCalendario(
                dados.calendario
            );


            // ==============================================
            // INDICA QUE ESTÁ AO VIVO
            // ==============================================

            const status =
                document.getElementById(
                    "statusDashboard"
                );

            if (status) {{

                status.textContent =
                    "● ATUALIZADO";

                setTimeout(() => {{

                    status.textContent =
                        "● AO VIVO";

                }}, 1200);

            }}

        }} catch (erro) {{

            console.log(
                "Erro ao atualizar Dashboard:",
                erro
            );

        }}

    }}


    // ======================================================
    // ATUALIZA O CALENDÁRIO SEM RECARREGAR A PÁGINA
    // ======================================================

    function atualizarCalendario(calendario) {{

        const grid =
            document.getElementById(
                "calGridDashboard"
            );


        if (!grid) {{
            return;
        }}


        const agora = new Date();

        const anoAtual =
            agora.getFullYear();

        const mesAtual =
            agora.getMonth();


        const primeiroDia =
            new Date(
                anoAtual,
                mesAtual,
                1
            ).getDay();


        const ultimoDia =
            new Date(
                anoAtual,
                mesAtual + 1,
                0
            ).getDate();


        let html = "";


        const diasSemana = [
            "Dom",
            "Seg",
            "Ter",
            "Qua",
            "Qui",
            "Sex",
            "Sab"
        ];


        diasSemana.forEach(
            function(dia) {{

                html +=
                    '<div class="dia-semana">' +
                    dia +
                    '</div>';

            }}
        );


        for (
            let i = 0;
            i < primeiroDia;
            i++
        ) {{

            html +=
                '<div class="dia vazio"></div>';

        }}


        for (
            let dia = 1;
            dia <= ultimoDia;
            dia++
        ) {{

            const mesNumero =
                String(
                    mesAtual + 1
                ).padStart(
                    2,
                    "0"
                );


            const diaNumero =
                String(dia).padStart(
                    2,
                    "0"
                );


            const data =
                anoAtual +
                "-" +
                mesNumero +
                "-" +
                diaNumero;


            const info =
                calendario[data] || {};


            const entrada =
                info.entrada || 0;

            const saida =
                info.saida || 0;

            const transf =
                info.transf || 0;

            const total =
                info.total || 0;


            const hoje =
                dia === agora.getDate();


            html += `

                <div class="dia ${{
                    hoje
                    ? "hoje"
                    : ""
                }}">

                    <div class="num">
                        ${{dia}}
                    </div>

                    <div class="linha verde">
                        Entrada: ${{entrada}}
                    </div>

                    <div class="linha vermelho">
                        Saída: ${{saida}}
                    </div>

                    <div class="linha azul">
                        Transf: ${{transf}}
                    </div>

                    <div class="total">
                        Total: ${{total}}
                    </div>

                </div>

            `;

        }}


        grid.innerHTML =
            html;

    }}


    // ======================================================
    // PRIMEIRA ATUALIZAÇÃO
    // ======================================================

    atualizarDashboard();


    // ======================================================
    // 🔥 ATUALIZA A CADA 3 SEGUNDOS
    // ======================================================

    setInterval(
        atualizarDashboard,
        3000
    );

    </script>
    """

    return html
