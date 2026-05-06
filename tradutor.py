from flask import session

TRADUCOES = {

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

    "Sair": {
        "pt": "Sair",
        "en": "Logout",
        "es": "Salir"
    }
}


def t(texto):
    idioma = session.get("idioma", "pt")
    return TRADUCOES.get(texto, {}).get(idioma, texto)
