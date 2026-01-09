"""
NEXO Maestro - Sistema de Orquestração Inteligente (Versão Final de Ativação)
"""

import os
from fastapi import FastAPI
import uvicorn

# 1. Importações Ativadas (Removido os comentários)
try:
    from supabase import create_client, Client
    import google.generativeai as genai
    from groq import Groq

    DEPENDENCIES_OK = True
except ImportError as e:
    print(f"⚠️ Erro de dependência: {e}")
    DEPENDENCIES_OK = False

app = FastAPI(
    title="NEXO Maestro",
    description="Sistema inteligente de orquestração",
    version="1.0.0",
)

# 2. Lista de Secrets necessárias (Alinhadas com seu painel Settings)
REQUIRED_VARS = ["SUPABASE_URL", "SUPABASE_KEY", "GEMINI_API_KEY", "GROQ_API_KEY"]


def check_environment():
    missing_vars = [var for var in REQUIRED_VARS if not os.environ.get(var)]
    return (len(missing_vars) == 0), missing_vars


@app.get("/")
async def root():
    env_ok, missing = check_environment()

    if not env_ok:
        return {
            "status": "warning",
            "message": "NEXO Maestro está online, mas aguardando configuração",
            "missing_secrets": missing,
            "instruction": "Adicione estas chaves em Settings -> Variables and Secrets no seu Space",
        }

    return {
        "status": "success",
        "message": "NEXO Maestro está online e com o cérebro conectado! 🧬",
        "version": "1.0.0",
        "ready": True,
    }


@app.get("/health")
async def health_check():
    env_ok, _ = check_environment()
    return {
        "status": "healthy" if env_ok and DEPENDENCIES_OK else "degraded",
        "environment": "ready" if env_ok else "missing_secrets",
        "dependencies": "ok" if DEPENDENCIES_OK else "error",
    }


# 3. Porta 7860 configurada para o Hugging Face Spaces
if __name__ == "__main__":
    print("🧬 Despertando NEXO Maestro...")
    uvicorn.run(app, host="0.0.0.0", port=7860)
