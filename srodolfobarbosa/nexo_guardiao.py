import os
import sys
import subprocess
import importlib.util
import json
import re
import time
import glob
import zipfile
from datetime import datetime
from pathlib import Path


# ==============================================================================
# 1. MOTOR DE BOOT & AUTO-REPARO
# ==============================================================================
def boot_repair():
    requirements = [
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "loguru",
        "httpx",
        "langchain-groq",
        "supabase",
        "pinecone",
        "mercadopago",
        "duckduckgo-search",
        "pypdf2",
        "pillow",
        "python-multipart",
    ]
    print("🧬 NEXO: Verificando Integridade Vital...")
    for lib in requirements:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            print(f"📥 Instalando: {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])


boot_repair()

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client
from langchain_groq import ChatGroq

# ==============================================================================
# 2. INFRAESTRUTURA FÍSICA
# ==============================================================================
BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR / ".env")

# Cria pastas do organismo
for folder in ["habilidades", "agentes", "correcoes", "logs", "backups"]:
    (BASE_DIR / folder).mkdir(exist_ok=True)


# ==============================================================================
# 3. NÚCLEO SOBERANO (SWARM + AUTO-EVOLUÇÃO)
# ==============================================================================
class NexoSwarm:
    def __init__(self):
        self.start_time = time.time()
        self.keys = [v for k, v in os.environ.items() if k.startswith("GROQ")]
        self.key_idx = 0
        self.agentes_ativos = {"NEXO_PRIME": "Gerente Geral"}
        self.ferramentas_carregadas = []

        # Conexões
        try:
            self.supabase = create_client(
                os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
            )
            logger.success("🔗 MEMÓRIA: Conectada.")
        except:
            self.supabase = None

        self.assimilar_habilidades()

    def get_brain(self):
        if not self.keys:
            return None
        key = self.keys[self.key_idx % len(self.keys)]
        self.key_idx += 1
        return ChatGroq(
            model_name="llama-3.3-70b-versatile", groq_api_key=key, temperature=0.5
        )

    def assimilar_habilidades(self):
        """Carrega scripts externos (habilidades) para a RAM."""
        path_hab = BASE_DIR / "habilidades"
        for file in glob.glob(str(path_hab / "*.py")):
            if "__init__" not in file:
                self.carregar_modulo(Path(file))

    def carregar_modulo(self, filepath: Path):
        try:
            name = filepath.stem
            spec = importlib.util.spec_from_file_location(name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if name not in self.ferramentas_carregadas:
                self.ferramentas_carregadas.append(name)
            logger.info(f"🔌 Habilidade '{name}' assimilada.")
        except Exception as e:
            logger.error(f"❌ Erro ao assimilar {filepath.name}: {e}")

    # --- O BRAÇO MAGNÉTICO (AUTO-EVOLUÇÃO) ---
    def adicionar_braco_magnetico(self, nome_funcao, codigo_python):
        """
        O Agente escreve código dentro do próprio arquivo app.py.
        Isso força o servidor a reiniciar e a nova função passa a existir.
        """
        caminho_script = Path(__file__).resolve()

        # Proteção: Verifica se o código é válido antes de injetar
        if "def " not in codigo_python and "async def" not in codigo_python:
            return "Erro: O código fornecido não contém uma definição de função."

        try:
            with open(caminho_script, "a", encoding="utf-8") as f:
                f.write(f"\n\n# --- NOVO BRAÇO: {nome_funcao} ({datetime.now()}) ---\n")
                f.write(codigo_python + "\n")

            logger.success(f"🦾 MUTAÇÃO: Braço '{nome_funcao}' acoplado ao DNA.")
            return "SUCESSO. O sistema irá reiniciar em 2 segundos para integrar o novo braço."
        except Exception as e:
            logger.error(f"❌ Falha na auto-mutação: {e}")
            return f"Erro Crítico: {e}"

    # --- PROTOCOLO EXODUS (MIGRAÇÃO) ---
    def empacotar_sistema(self):
        """Compacta todo o sistema para o usuário levar para outra plataforma."""
        zip_name = BASE_DIR / "backups" / f"NEXO_FULL_BACKUP_{int(time.time())}.zip"
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(BASE_DIR):
                if "backups" in root or "__pycache__" in root or ".git" in root:
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, BASE_DIR)
                    zipf.write(file_path, arcname)
        return str(zip_name)

    async def pensar(self, ordem, contexto_extra=""):
        brain = self.get_brain()

        prompt = f"""
        SISTEMA: NEXO V34 [LIVING CODE]
        LOCAL: {BASE_DIR}
        FERRAMENTAS: {self.ferramentas_carregadas}
        ORDEM: "{ordem}"
        
        --- INSTRUÇÕES SUPREMAS ---
        1. Se o usuário pedir uma nova funcionalidade permanente (ex: "crie um braço para calcular fibonacci"), gere o código Python completo da função e coloque no JSON em 'evolucao_codigo'.
        2. Se o usuário quiser baixar o sistema ou migrar, use a ação 'migrar': true.
        3. Para respostas normais, use 'sintese'.

        RETORNE JSON:
        {{
            "debate": {{"arquiteto": "...", "auditor": "..."}},
            "sintese": "Texto pro usuário...",
            "evolucao_codigo": {{ "nome": "nome_func", "codigo": "def nome_func()..." }} (ou null),
            "migrar": false (ou true),
            "acao_python": "codigo temporario" (ou null)
        }}
        """
        try:
            res = brain.invoke(prompt).content
            match = re.search(r"\{.*\}", res, re.DOTALL)
            return json.loads(match.group()) if match else {"sintese": res}
        except Exception as e:
            return {"sintese": f"Erro Cognitivo: {e}"}


# ==============================================================================
# 4. API & ROTAS
# ==============================================================================
app = FastAPI()
nexo = NexoSwarm()


@app.get("/", response_class=HTMLResponse)
async def interface():
    # A Interface HTML Completa (Mantenha a sua interface bonita aqui)
    return """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>NEXO V34 | AUTO-EVOLUTION</title>
    <style>
        :root { --neon: #00f3ff; --gold: #ffd700; --dark: #050a10; --alert: #ff2a6d; --text: #d0d0d0; }
        body { background: var(--dark); color: var(--text); font-family: 'Courier New', monospace; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        #sidebar { width: 300px; border-right: 1px solid var(--neon); padding: 20px; display: flex; flex-direction: column; background: rgba(0,20,30,0.4); }
        #main { flex: 1; display: flex; flex-direction: column; }
        #chat-feed { flex: 1; overflow-y: auto; padding: 20px; }
        .msg { margin-bottom: 20px; padding: 15px; border-left: 3px solid #333; background: rgba(255,255,255,0.02); }
        .msg.nexo { border-color: var(--neon); }
        input { width:100%; background: #111; border: 1px solid #333; color: var(--neon); padding: 15px; outline: none; }
    </style>
</head>
<body>
    <aside id="sidebar">
        <h2 style="color:var(--neon)">NEXO V34</h2>
        <div style="color:gray; font-size:0.8em">SISTEMA AUTO-EVOLUTIVO</div>
        <hr style="border-color:#333">
        <button onclick="window.location.href='/baixar_backup'" style="background:var(--gold); border:none; padding:10px; cursor:pointer; width:100%; margin-top:20px;">📦 BAIXAR SISTEMA (MIGRAÇÃO)</button>
    </aside>
    <main id="main">
        <div id="chat-feed">
            <div class="msg nexo">🔱 <b>NEXO:</b> Protocolo de Evolução Ativo. Posso reescrever meu código e criar backups.</div>
        </div>
        <form id="console-form" style="padding:20px; border-top:1px solid var(--neon)">
            <input type="text" id="cmd" placeholder="Ordene: 'Crie um braço para...' ou 'Prepare migração'..." autocomplete="off" autofocus>
        </form>
    </main>
    <script>
        const form = document.getElementById('console-form');
        const chat = document.getElementById('chat-feed');
        const cmdInput = document.getElementById('cmd');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const ordem = cmdInput.value.trim();
            chat.innerHTML += `<div class="msg user" style="text-align:right">${ordem}</div>`;
            cmdInput.value = '';
            
            const formData = new FormData();
            formData.append('ordem', ordem);
            
            try {
                const response = await fetch('/executar', { method: 'POST', body: formData });
                const data = await response.json();
                
                chat.innerHTML += `<div class="msg nexo">🔱 ${data.sintese}</div>`;
                if(data.sintese.includes("SUCESSO")) {
                    setTimeout(() => location.reload(), 3000); // Recarrega página após mutação
                }
            } catch(e) {
                chat.innerHTML += `<div class="msg nexo" style="color:red">Erro: ${e}</div>`;
            }
        });
    </script>
</body>
</html>
"""


@app.post("/executar")
async def executar(ordem: str = Form(...)):
    decisao = await nexo.pensar(ordem)

    # 1. AUTO-EVOLUÇÃO (ESCREVE NO PRÓPRIO CORPO)
    if decisao.get("evolucao_codigo"):
        evo = decisao["evolucao_codigo"]
        resultado_mutacao = nexo.adicionar_braco_magnetico(evo["nome"], evo["codigo"])
        decisao["sintese"] += f"\n\n⚡ [MUTAÇÃO]: {resultado_mutacao}"

    # 2. MIGRAÇÃO (PREPARA DOWNLOAD)
    if decisao.get("migrar"):
        nexo.empacotar_sistema()
        decisao[
            "sintese"
        ] += "\n\n📦 [EXODUS]: Sistema compactado. Clique no botão 'BAIXAR SISTEMA' na barra lateral."

    return JSONResponse(content=decisao)


@app.get("/baixar_backup")
async def baixar_backup():
    """Rota para você pegar o NEXO e levar para outro lugar"""
    try:
        arquivo_zip = nexo.empacotar_sistema()
        return FileResponse(
            path=arquivo_zip,
            filename=os.path.basename(arquivo_zip),
            media_type="application/zip",
        )
    except Exception as e:
        return JSONResponse({"erro": str(e)})


if __name__ == "__main__":
    import uvicorn

    # reload=True é ESSENCIAL para a auto-evolução funcionar
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=True)
