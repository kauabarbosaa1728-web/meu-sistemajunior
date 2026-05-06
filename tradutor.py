from flask import session

TRADUCOES = {

    # ===== GERAL =====
    "Painel": {
        "pt": "Painel",
        "en": "Dashboard",
        "es": "Panel"
    },

    "Usuários": {
        "pt": "Usuários",
        "en": "Users",
        "es": "Usuarios"
    },

    "Logs": {
        "pt": "Logs",
        "en": "Logs",
        "es": "Registros"
    },

    "Configurações": {
        "pt": "Configurações",
        "en": "Settings",
        "es": "Configuración"
    },

    "Idioma": {
        "pt": "Idioma",
        "en": "Language",
        "es": "Idioma"
    },

    "Data / Hora": {
        "pt": "Data / Hora",
        "en": "Date / Time",
        "es": "Fecha / Hora"
    },

    "Salvar": {
        "pt": "Salvar",
        "en": "Save",
        "es": "Guardar"
    },

    "Sair": {
        "pt": "Sair",
        "en": "Logout",
        "es": "Salir"
    },

    # ===== MENU SISTEMA =====
    "Sistema": {
        "pt": "Sistema",
        "en": "System",
        "es": "Sistema"
    },

    # ===== ESTOQUE =====
    "Estoque": {
        "pt": "Estoque",
        "en": "Inventory",
        "es": "Inventario"
    },

    "Ver Estoque": {
        "pt": "Ver Estoque",
        "en": "View Inventory",
        "es": "Ver Inventario"
    },

    "Transferência": {
        "pt": "Transferência",
        "en": "Transfer",
        "es": "Transferencia"
    },

    "Entrada": {
        "pt": "Entrada",
        "en": "Entry",
        "es": "Entrada"
    },

    "Histórico": {
        "pt": "Histórico",
        "en": "History",
        "es": "Historial"
    },

    # ===== FINANCEIRO =====
    "Financeiro": {
        "pt": "Financeiro",
        "en": "Financial",
        "es": "Finanzas"
    },

    "Relatório": {
        "pt": "Relatório",
        "en": "Report",
        "es": "Reporte"
    },

    "Entradas": {
        "pt": "Entradas",
        "en": "Entries",
        "es": "Entradas"
    },

    "Saídas": {
        "pt": "Saídas",
        "en": "Expenses",
        "es": "Salidas"
    },

    "Resumo Geral": {
        "pt": "Resumo Geral",
        "en": "Overview",
        "es": "Resumen"
    },

    # ===== RELATÓRIOS =====
    "Relatórios": {
        "pt": "Relatórios",
        "en": "Reports",
        "es": "Informes"
    },

    "Geral": {
        "pt": "Geral",
        "en": "General",
        "es": "General"
    },

    # ===== VEÍCULOS =====
    "Veículos": {
        "pt": "Veículos",
        "en": "Vehicles",
        "es": "Vehículos"
    },

    "Manutenções": {
        "pt": "Manutenções",
        "en": "Maintenance",
        "es": "Mantenimiento"
    },

    "Dashboard": {
        "pt": "Dashboard",
        "en": "Dashboard",
        "es": "Panel"
    },

    "Rotas": {
        "pt": "Rotas",
        "en": "Routes",
        "es": "Rutas"
    },

    # ===== ERROS =====
    "Acesso negado": {
        "pt": "Acesso negado",
        "en": "Access denied",
        "es": "Acceso denegado"
    },

    "Você não tem permissão para acessar esta área.": {
        "pt": "Você não tem permissão para acessar esta área.",
        "en": "You do not have permission to access this area.",
        "es": "No tienes permiso para acceder a esta área."
    },

    "Voltar para o painel": {
        "pt": "Voltar para o painel",
        "en": "Back to dashboard",
        "es": "Volver al panel"
    }
}


def t(texto):
    idioma = session.get("idioma", "pt")
    return TRADUCOES.get(texto, {}).get(idioma, texto)
