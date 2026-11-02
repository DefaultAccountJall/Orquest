import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

# --- CONFIGURAÇÃO DO ZEROKEY (ARQUITETURA HÍBRIDA) ---
# O ZeroKey exige uma string qualquer como API Key local
DEEPSEEK_API_KEY = "zerokey-local"

if not DEEPSEEK_API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY ausente no .env")

# Endpoint do ZeroKey no seu Notebook
BASE_URL = "http://192.168.0.118:7251/v1" 

# --- ROTEAMENTO DE MODELOS ---
# O Claude é usado APENAS para gerar o código (FrontendCoder e LogicCoder)
MODEL = "default" 

# O DeepSeek é usado para PLANEJAR (UIPlanner e Researcher) para salvar a cota do Claude
MODEL_PLANNER = "default"       

# Caminhos
ROOT = Path(__file__).resolve().parent
WORKSPACE_DIR = ROOT / "workspace"
WORKSPACE_DIR.mkdir(exist_ok=True)

# Configurações do Pipeline
# 2 loops é o suficiente para o Claude. Mais que isso gasta sua cota de 5 horas.
MAX_REVIEW_LOOPS = 2 

# Temperaturas (Criatividade vs Precisão)
TEMPERATURE_TECHNICAL = 0.2  # Para JS, Lógica (focado e exato)
TEMPERATURE_CREATIVE = 0.7   # Para Design e HTML (ousado e criativo)