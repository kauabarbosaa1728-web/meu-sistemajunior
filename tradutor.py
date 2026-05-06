from flask import session
from deep_translator import GoogleTranslator

# ================= BASE MANUAL (opcional, mais rápido) =================
TRADUCOES = {
    "Painel": {"pt": "Painel", "en": "Dashboard", "es": "Panel"},
    "Usuários": {"pt": "Usuários", "en": "Users", "es": "Usuarios"},
    "Logs": {"pt": "Logs", "en": "Logs", "es": "Registros"},
    "Configurações": {"pt": "Configurações", "en": "Settings", "es": "Configuración"},
    "Idioma": {"pt": "Idioma", "en": "Language", "es": "Idioma"},
    "Data / Hora": {"pt": "Data / Hora", "en": "Date / Time", "es": "Fecha / Hora"},
    "Salvar": {"pt": "Salvar", "en": "Save", "es": "Guardar"},
    "Sair": {"pt": "Sair", "en": "Logout", "es": "Salir"},
}

# ================= CACHE (melhora performance) =================
_cache = {}


# ================= FUNÇÃO PRINCIPAL =================
def t(texto):
    idioma = session.get("idioma", "pt")

    # se for português, não traduz
    if idioma == "pt":
        return texto

    chave = f"{idioma}:{texto}"

    # cache
    if chave in _cache:
        return _cache[chave]

    # 1️⃣ tenta tradução manual primeiro
    if texto in TRADUCOES and idioma in TRADUCOES[texto]:
        traduzido = TRADUCOES[texto][idioma]

    else:
        # 2️⃣ tradução automática
        try:
            traduzido = GoogleTranslator(source='auto', target=idioma).translate(texto)
        except:
            traduzido = texto  # fallback se falhar

    _cache[chave] = traduzido
    return traduzido
