from flask import Blueprint

financeiro_bp = Blueprint("financeiro_bp", __name__)

# IMPORTA ROTAS
from .financeiro_main import *
from .financeiro_entrada import *
from .financeiro_saida import *
from .financeiro_resumo import *
