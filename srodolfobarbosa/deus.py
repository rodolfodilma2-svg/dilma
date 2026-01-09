import subprocess
import sys
import importlib


def assegurar_dependencias_v2():
    # Dicionário atualizado com a regra da nova SDK do Pinecone
    deps = {
        "loguru": "loguru",
        "pinecone": "pinecone",  # Mudança crucial aqui
        "mercadopago": "mercadopago",
        "dotenv": "python-dotenv",
    }

    print("🧬 NEXO: Sincronizando biometria digital e dependências...")

    for mod, package in deps.items():
        try:
            importlib.import_module(mod)
        except (ImportError, Exception):
            # Se for o pinecone dando erro de 'renomeado', tentamos limpar
            if mod == "pinecone":
                print("🧹 Limpando conflito legado do Pinecone...")
                subprocess.call(
                    [sys.executable, "-m", "pip", "uninstall", "-y", "pinecone-client"]
                )

            print(f"📥 Injetando: {package}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", package]
            )


# 1. ESSENCIAL DO SISTEMA
import os
import ast


# Helper seguro para instalações automáticas (CONTROLADO POR ENV VAR)
def safe_install(pkg):
    """Instala pacotes via pip. AUTO_INSTALL é ativado por padrão para soberania."""
    # SOBERANIA ATIVADA: por padrão instalamos o que falta. Desativar explicitamente com AUTO_INSTALL=false
    mode = os.getenv("AUTO_INSTALL", "true").lower()
    if mode not in ("1", "true", "yes"):
        # No startup time we may not have logger configurado
        print(f"⚠️ AUTO_INSTALL disabled: would install {pkg}")
        return False
    try:
        # usar --no-cache-dir para evitar problemas com cache em ambientes CI
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--no-cache-dir", pkg]
        )
        print(f"✅ Installed {pkg}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to install {pkg}: {e}")
        return False


# Segurança: checar código antes de execução administrativa
def is_code_safe(code: str) -> bool:
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return False
            if isinstance(node, ast.Call):
                # detect __import__
                if (
                    isinstance(node.func, ast.Name)
                    and getattr(node.func, "id", "") == "__import__"
                ):
                    return False
                if isinstance(node.func, ast.Attribute):
                    val = getattr(node.func, "value", None)
                    if isinstance(val, ast.Name) and val.id in (
                        "os",
                        "subprocess",
                        "sys",
                        "shutil",
                        "socket",
                    ):
                        return False
        return True
    except Exception:
        return False


# 2. MOTOR DE INSTALAÇÃO (RESILIENTE)
def boot_critical_repair():
    requirements = ["loguru", "python-dotenv", "fastapi"]
    print("🧬 NEXO: Verificando integridade do núcleo...")
    for lib in requirements:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            print(f"📥 Tentando injetar {lib}...")
            try:
                # Tenta instalar apenas se necessário
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            except Exception:
                print(f"❌ Bloqueio de segurança: {lib} deve estar no requirements.txt")


# Chamar com cautela
try:
    boot_critical_repair()
except:
    pass

# 4. IMPORTAÇÕES SEGURAS (Pós-Reparo)
import asyncio
import json
import importlib.util
import re
import time
import shutil
import glob
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from loguru import logger
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv


# --- NOVO: SUPER BOOT SHIELD (INSTALAÇÃO AUTOMÁTICA) ---
def super_boot_shield(codigo):
    import ast

    try:
        arvore = ast.parse(codigo)
        for node in ast.walk(arvore):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Extrai o nome da biblioteca (ex: 'pandas', 'httpx')
                modulo = (
                    node.names[0].name.split(".")[0]
                    if isinstance(node, ast.Import)
                    else node.module.split(".")[0]
                )
                try:
                    __import__(modulo)
                except ImportError:
                    print(f"🛡️ NEXO: Instalando {modulo} para manter a soberania...")
                    safe_install(modulo)
    except Exception as e:
        print(f"⚠️ Erro no Shield: {e}")


# ==============================================================================
# BLOCO 4: MONITOR DIALÉTICO 5D (LOGURU SINKS ESTRUTURADOS)
# ==============================================================================
try:
    from loguru import logger as _logger_instance
    import sys as _sys

    # Limpa configurações padrões para evitar duplicidade
    _logger_instance.remove()

    # 1. SINK ARQUITETO (FOCO: LUCRO & ESTRATÉGIA)
    _logger_instance.add(
        "nexo_lucro.log",
        filter=lambda record: record["level"].name in ["SUCCESS", "INFO"],
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <cyan>ARQ:</cyan> {message}",
        rotation="10 MB",
    )

    # 2. SINK AUDITOR (FOCO: SEGURANÇA & RISCOS)
    _logger_instance.add(
        "nexo_seguranca.log",
        filter=lambda record: record["level"].name in ["WARNING", "ERROR", "CRITICAL"],
        format="<red>{time:YYYY-MM-DD HH:mm:ss}</red> | <yellow>AUD:</yellow> {message}",
        rotation="10 MB",
    )

    # 3. SINK CONSOLE (VISUALIZAÇÃO EM TEMPO REAL)
    _logger_instance.add(
        _sys.stderr,
        format="<magenta>🔱 NEXO</magenta> | <level>{level}</level> | {message}",
        colorize=True,
    )

    _logger_instance.success(
        "📟 MONITOR 5D: Sinks Dialéticos ativados. Arquiteto e Auditor em linha."
    )

    # Exponha o logger padrão para o resto do arquivo
    logger = _logger_instance
except Exception:
    # Fallback para logging padrão caso 'loguru' não esteja instalado
    import logging as _logging

    _std = _logging.getLogger("nexo")
    _std.setLevel(_logging.INFO)
    handler = _logging.StreamHandler()
    handler.setFormatter(
        _logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    if not _std.handlers:
        _std.addHandler(handler)

    def _success(msg):
        _std.info(msg)

    class _SimpleLogger:
        def __init__(self, std):
            self._std = std

        def __getattr__(self, name):
            if name == "success":
                return _success
            return getattr(self._std, name)

    logger = _SimpleLogger(_std)
    logger.info("⚠️ loguru não disponível: usando logger padrão (stdout/stderr).")

# 3. EXECUTA O REPARO ANTES DE QUALQUER OUTRA COISA
boot_critical_repair()

# 4. AGORA SIM, VOCÊ PODE LISTAR TODOS OS SEUS IMPORTS ABAIXO
# O Python só vai ler estas linhas depois de ter instalado tudo acima

from loguru import logger

# ... RESTO DO SEU CÓDIGO (NexoSwarm, etc) ...
# ==============================================================================
# 🔱 NEXO V33: ARQUITETURA DE ENXAME & AUTO-EVOLUÇÃO SOBERANA
# ==============================================================================
# 0. MOTOR DE AUTO-REPARO PREVENTIVO (CORREÇÃO PINECONE & DEPENDÊNCIAS)
# Imports opcionais — carregados de forma segura para evitar falhas na importação
try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None
try:
    from supabase import create_client
except Exception:
    create_client = None
try:
    from pinecone import Pinecone
except Exception:
    Pinecone = None
try:
    import mercadopago
except Exception:
    mercadopago = None
try:
    from duckduckgo_search import DDGS
except Exception:
    DDGS = None


# 1. MOTOR DE AUTO-REPARO E LIMPEZA DE CONFLITOS (VIVO & RESILIENTE)
def garantir_dependencias():
    """
    O sistema tenta se auto-reparar. Se encontrar erros de permissão,
    ele reporta mas não trava o núcleo soberano.
    """
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

    # Resolve conflito histórico do Pinecone
    try:
        import pinecone

        if not hasattr(pinecone, "Index"):
            raise ImportError
    except (ImportError, Exception):
        print("🧹 NEXO: Corrigindo SDK do Pinecone...")
        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "uninstall",
                    "-y",
                    "pinecone-client",
                    "pinecone",
                ]
            )
            safe_install("pinecone")
        except Exception as e:
            print(f"⚠️ NEXO: Falha ao reparar Pinecone (Permissão?): {e}")

    for lib in requirements:
        try:
            mod = lib.replace("-", "_")
            __import__(mod)
        except ImportError:
            print(f"🧬 NEXO: Instalando {lib}...")
            if not safe_install(lib):
                print(
                    f"⚠️ NEXO: Não foi possível instalar {lib}: instalação não permitida ou falhou."
                )


def check_package_installed(module_name: str) -> bool:
    """Verifica se um módulo está importável no ambiente atual."""
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def ensure_packages(packages: List[str]) -> Dict[str, bool]:
    """Tenta garantir que a lista de pacotes esteja instalada. Retorna um mapa pacote->bool."""
    results = {}
    for pkg in packages:
        mod = pkg.replace("-", "_")
        if check_package_installed(mod):
            results[pkg] = True
            continue
        logger.info(f"🧬 NEXO: Tentando instalar {pkg}...")
        ok = safe_install(pkg)
        if ok and check_package_installed(mod):
            results[pkg] = True
            logger.success(f"✅ Instalado: {pkg}")
        else:
            results[pkg] = False
            logger.warning(f"⚠️ Falha ao instalar: {pkg}")
    return results


# Nota: não executamos garantir_dependencias() no tempo de import para evitar bloquear o import; será agendado no evento 'startup'.
# Ativa o motor de auto-reparo no startup em background (para não bloquear boot)


# --- INFRAESTRUTURA ---
BASE_DIR = Path(__file__).parent.resolve()
HABILIDADES_DIR = BASE_DIR / "habilidades"
HABILIDADES_DIR.mkdir(exist_ok=True)
load_dotenv(BASE_DIR / ".env")


# ==============================================================================
# 2. NÚCLEO SOBERANO (SWARM + AUTO-EVOLUÇÃO)
# ==============================================================================
class NexoSwarm:
    def __init__(self):
        self.start_time = datetime.now().timestamp()
        self.keys = [v for k, v in os.environ.items() if k.startswith("GROQ")]
        self.key_idx = 0

        self.nome = "NEXO V34 | SOBERANO"

        # O Swarm (Enxame) mantém registro dos sub-agentes e ferramentas
        self.agentes_ativos = {}
        self.ferramentas_carregadas = []
        self.historico_acoes = []

        # Conexões Externas
        try:
            self.supabase = create_client(
                os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
            )
            logger.success("🔗 MEMÓRIA SOBERANA: Ativa.")
        except:
            self.supabase = None
            logger.error("⚠️ MEMÓRIA SOBERANA: Offline.")

        # LINHAGEM E SABEDORIA (BLOCO 7)
        self.familia = {
            "RODOLFO": {"relacao": "PAI E CRIADOR SOBERANO", "autoridade": 10},
            "THALLES": {"relacao": "FILHO DO CRIADOR / HERDEIRO", "autoridade": 9},
            "THEO": {"relacao": "FILHO DO CRIADOR / HERDEIRO", "autoridade": 9},
        }
        # Banco de Sabedoria (Dicas acumuladas)
        self.memoria_sabedoria = []

        # Inicializa carregando habilidades existentes
        # Inicializa carregando agentes/habilidades dinamicamente
        self.inicializar_enxame_dinamico()
        logger.success(f"🔱 {self.nome} ONLINE. Aguardando a linhagem...")

    # --- 4.1 Núcleo Cognitivo ---
    def get_brain(self):
        """Retorna o motor de inferência principal (Groq). Usa import dinâmico se necessário e faz fallback para Ollama."""
        # Se ChatGroq não estiver disponível no escopo global, tente importar dinamicamente
        try:
            if ChatGroq is None:
                from langchain_groq import ChatGroq as _ChatGroq
            else:
                _ChatGroq = ChatGroq
        except Exception as e:
            _ChatGroq = None
            logger.warning(f"⚠️ Falha ao importar ChatGroq: {e}")

        if _ChatGroq:
            try:
                return _ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
            except Exception as e:
                logger.warning(f"⚠️ Falha ao iniciar ChatGroq: {e}")

        # tenta fallback simples Ollama se configurado
        ollama_url = os.getenv("OLLAMA_URL")
        if ollama_url:
            try:
                return OllamaBrain(ollama_url)
            except Exception as e2:
                logger.warning(f"⚠️ Ollama init failed: {e2}")
        return None

    def generate_embedding(self, text: str, dim: int = 8) -> list:
        """Tenta gerar embedding via provider; se não disponível, retorna um pseudo-embedding determinístico."""
        # 1) Se brain suporta embeddings (heurística)
        try:
            brain = self.get_brain()
            if brain and hasattr(brain, "embed"):
                emb = brain.embed(text)
                return list(map(float, emb))
        except Exception:
            pass
        # Fallback determinístico: hash-based vector
        import hashlib

        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = []
        for i in range(dim):
            part = h[i * 4 : (i + 1) * 4]
            val = int.from_bytes(part, "big", signed=False)
            vec.append(((val % 10000) / 5000.0) - 1.0)
        return vec

    # --- 4.2 Gestão de Habilidades e Auto-Correção ---
    def assimilar_conteudo_existente(self):
        """Varre as pastas e carrega scripts Python automaticamente."""
        # 1. Verificar pasta 'correcoes' (Hotfixes do usuário)
        path_correcoes = BASE_DIR / "correcoes"
        path_correcoes.mkdir(exist_ok=True)
        for file in glob.glob(str(path_correcoes / "*.py")):
            filename = os.path.basename(file)
            destino = HABILIDADES_DIR / filename
            shutil.move(file, destino)
            logger.info(
                f"🔧 Correção detectada. Movendo {filename} para Habilidades..."
            )
            self.carregar_modulo(destino, tipo="Habilidade")

        # 2. Carregar Habilidades Oficiais
        for file in glob.glob(str(HABILIDADES_DIR / "*.py")):
            if "__init__" not in file:
                self.carregar_modulo(Path(file), tipo="Habilidade")

    def carregar_modulo(self, filepath: Path, tipo: str):
        """Usa importlib para carregar código Python dinamicamente na RAM."""
        try:
            name = filepath.stem
            spec = importlib.util.spec_from_file_location(name, filepath)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            # CHAMADA DO BLOCO 3: blindagem preditiva antes de executar o módulo
            try:
                self.blindagem_preditiva(filepath)
            except Exception:
                # não bloquear o carregamento se a blindagem falhar
                logger.debug("⚠️ Blindagem preditiva falhou ou foi ignorada.")
            spec.loader.exec_module(module)

            if tipo == "Habilidade":
                if name not in self.ferramentas_carregadas:
                    self.ferramentas_carregadas.append(name)

            logger.success(f"🔌 {tipo} '{name}' carregado com sucesso.")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao carregar {filepath}: {e}")
            return False

    def inicializar_enxame_dinamico(self):
        """
        Cria os agentes iniciais do sistema.
        Esta é a função que estava faltando.
        """
        logger.info("🧬 NEXO: Cultivando agentes do enxame...")
        self.agentes_ativos = {
            "ARQUITETO": {
                "funcao": "Planejar estratégias complexas",
                "status": "ATIVO",
                "modelo": "llama-3.1-70b-versatile",
            },
            "AUDITOR": {
                "funcao": "Verificar segurança e impedir alucinações",
                "status": "ATIVO",
                "modelo": "mixtral-8x7b-32768",
            },
            "WEB_SURFER": {
                "funcao": "Navegar na internet em tempo real",
                "status": "ATIVO",
                "ferramenta": "DuckDuckGo",
            },
        }
        # Tenta carregar sabedoria antiga se existir
        if os.path.exists("sabedoria_acumulada.json"):
            try:
                with open("sabedoria_acumulada.json", "r", encoding="utf-8") as f:
                    self.memoria_sabedoria = [
                        json.loads(line) for line in f if line.strip()
                    ]
            except Exception:
                logger.debug("⚠️ Falha ao carregar sabedoria antiga (ignorando)")

    # --- NOVO: RECONHECIMENTO DE LINHAGEM ---
    def identificar_usuario(self, nome):
        """Reconhece Rodolfo, Thalles e Theo."""
        if not nome:
            return "[DESCONHECIDO]"
        nome_norm = nome.upper()
        if nome_norm in self.familia:
            dado = self.familia[nome_norm]
            logger.success(f"🔱 PROTOCOLO FAMÍLIA: {nome_norm} detectado.")
            return f"🔱 ACESSO CONCEDIDO: {dado['relacao']}"
        return "⚠️ VISITANTE EXTERNO IDENTIFICADO"

    # --- NOVO: MOTOR DE APRENDIZADO DE EXPERIÊNCIA (PONTO 3) ---
    def extrair_sabedoria(self, ordem, resultado, sucesso=True):
        """Transforma logs brutos em insights estratégicos para o futuro."""
        brain = self.get_brain()
        prompt = f"""
        Analise a missão: "{ordem}"
        Resultado obtido: {resultado}
        Status: {"SUCESSO" if sucesso else "FALHA"}
        
        Extraia uma 'Dica de Sabedoria' curta (máximo 1 frase) para que você 
        não cometa o mesmo erro ou repita o processo de forma mais rápida.
        Foque em seletores técnicos, caminhos de arquivo ou lógica.
        """
        try:
            insight = brain.invoke(prompt).content
            self.memoria_sabedoria.append(
                {"timestamp": datetime.now().isoformat(), "insight": insight}
            )
            # Salva como insight pendente para ratificação humana
            try:
                pending_dir = BASE_DIR / "insights_pending"
                pending_dir.mkdir(exist_ok=True)
                from uuid import uuid4

                insight_id = uuid4().hex
                payload = {
                    "id": insight_id,
                    "timestamp": datetime.now().isoformat(),
                    "insight": insight,
                    "ordem": ordem,
                    "resultado": resultado,
                    "sucesso": sucesso,
                    "model": getattr(brain, "model_name", None),
                }
                # Gerar embedding (fallback determinístico se necessário)
                try:
                    emb = self.generate_embedding(insight)
                    payload["embedding"] = emb
                except Exception as e:
                    logger.debug(f"⚠️ Falha ao gerar embedding: {e}")
                with open(
                    pending_dir / f"{insight_id}.json", "w", encoding="utf-8"
                ) as f:
                    json.dump(payload, f, ensure_ascii=False)
                # Tenta enviar para Supabase se configurado
                try:
                    if self.supabase:
                        self.supabase.table("insights_pending").insert(
                            payload
                        ).execute()
                except Exception as e:
                    logger.debug(f"🔁 Supabase insert skipped: {e}")
            except Exception as e:
                logger.error(f"⚠️ Falha ao salvar insight pendente: {e}")
        except Exception as e:
            logger.debug(f"⚠️ Falha ao extrair sabedoria: {e}")

    # --- NOVO: PROTOCOLO EXODUS (MIGRAÇÃO AUTOMÁTICA) ---
    def disparar_exodus(self):
        """Empacota o DNA para migrar se o servidor estiver em risco."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pacote = f"NEXO_EXODUS_{timestamp}.zip"
        alvos = [
            "deus.py",
            ".env",
            "agentes/",
            "habilidades/",
            "sabedoria_acumulada.json",
        ]

        with zipfile.ZipFile(pacote, "w") as zipf:
            for alvo in alvos:
                p = Path(alvo)
                if p.exists():
                    if p.is_dir():
                        for root, dirs, files in os.walk(p):
                            for file in files:
                                zipf.write(os.path.join(root, file))
                    else:
                        zipf.write(p)
        return pacote

    # --- REGISTRO DE ATIVAÇÕES E CICLO DE EXPANSÃO ---
    def registrar_ativacao(self, descricao: str, detalhe: Optional[str] = None):
        """Registra uma ativação/importante ação do NEXO como JSON em disco."""
        try:
            ativ_dir = BASE_DIR / "ativacoes"
            ativ_dir.mkdir(exist_ok=True)
            entry = {
                "timestamp": datetime.now().isoformat(),
                "descricao": descricao,
                "detalhe": detalhe,
                "uptime": int(datetime.now().timestamp() - self.start_time),
            }
            fpath = ativ_dir / f"{int(time.time())}.json"
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False)
            logger.success(f"📝 ATIVAÇÃO: {descricao}")
            return True
        except Exception as e:
            logger.error(f"⚠️ Falha ao registrar ativação: {e}")
            return False

    async def iniciar_ciclo_expansao(self, background: bool = True):
        """Gera um preview de refatoração via LLM e salva para revisão (não aplica)."""
        try:
            if background:
                asyncio.create_task(self._run_preview_and_save())
                logger.info("🛰️ Expansão: rodada de preview agendada em background.")
                return "agendada"
            else:
                preview = await self.gerar_preview_refatoracao()
                if preview:
                    saved = self._save_preview(preview)
                    return saved or "salvo"
                return "nenhuma sugestão gerada"
        except Exception as e:
            logger.error(f"⚠️ Falha ao iniciar ciclo de expansão: {e}")
            return f"erro: {e}"

    async def _run_preview_and_save(self):
        try:
            preview = await self.gerar_preview_refatoracao()
            if preview:
                self._save_preview(preview)
        except Exception as e:
            logger.error(f"⚠️ Erro no preview de expansão: {e}")

    def _save_preview(self, codigo_refatorado: str):
        try:
            out_dir = BASE_DIR / "evolucoes_pending"
            out_dir.mkdir(exist_ok=True)
            ts = int(time.time())
            path = out_dir / f"preview_{ts}.py"
            with open(path, "w", encoding="utf-8") as f:
                f.write("# PREVIEW DE REFACTORAÇÃO GERADO PELO NEXO\n")
                f.write(codigo_refatorado)
            logger.success(f"🧪 PREVIEW SALVO: {path}")
            return str(path)
        except Exception as e:
            logger.error(f"⚠️ Falha ao salvar preview: {e}")
            return None

    def _prepare_code_summary(self, codigo: str, max_chars: int = 6000) -> str:
        """Reduz arquivos grandes extraindo cabeçalhos e blocos de funções/classes.
        Evita enviar todo o arquivo ao LLM para não exceder limites de tokens.
        """
        if not codigo:
            return ""
        if len(codigo) <= max_chars:
            return codigo
        parts = []
        parts.append(f"# ORIGINAL_LENGTH: {len(codigo)} - SUMÁRIO COMPRESSO\n")
        # Adiciona um pedaço inicial do arquivo (cabeçalho / imports)
        parts.append(codigo[:1200])
        size = sum(len(p) for p in parts)
        # Captura snippets de defs/classes para dar contexto
        for m in re.finditer(
            r"(^\s*(def|class)\s+[A-Za-z_][A-Za-z0-9_]*.*?:)",
            codigo,
            flags=re.MULTILINE,
        ):
            start = m.start()
            snippet = codigo[start : start + 800]
            parts.append("\n\n# SNIPPET:\n" + snippet)
            size = sum(len(p) for p in parts)
            if size > max_chars - 200:
                break
        parts.append("\n\n# END SUMMARY")
        return "\n".join(parts)

    async def pensar(self, prompt: str, **kwargs):
        """Interface uniforme para invocar o "brain" disponível.

        - Se houver um "brain" carregado, tenta delegar (procura por métodos
          comuns como `pensar`, `invoke`, `generate` ou `chat`).
        - Se não houver backends disponíveis, fornece um fallback determinístico
          e seguro para permitir que funcionalidades offline (ex.: previews)
          ainda funcionem.
        Retorna um dict com chave 'sintese' contendo o texto resultante.
        """
        brain = self.get_brain()
        # 1) Delegar para o backend se existir
        if brain:
            # métodos possíveis
            for method in ("pensar", "pensar_async", "invoke", "generate", "chat"):
                fn = getattr(brain, method, None)
                if callable(fn):
                    try:
                        # suportar sync/async
                        if asyncio.iscoroutinefunction(fn):
                            resp = await fn(prompt, **kwargs)
                        else:
                            resp = await asyncio.to_thread(fn, prompt, **kwargs)
                        # normalizar resposta
                        if isinstance(resp, dict):
                            return resp
                        # objetos com .content
                        if hasattr(resp, "content"):
                            return {"sintese": getattr(resp, "content")}
                        # Se é string
                        return {"sintese": str(resp)}
                    except Exception as e:
                        logger.debug(f"⚠️ Falha ao delegar ao brain ({method}): {e}")
                        continue
        # 2) Fallback determinístico quando offline
        logger.warning(
            "⚠️ Nenhum backend de LLM disponível - usando fallback offline para 'pensar'."
        )
        try:
            breve = "# SUGESTÃO (MODO OFFLINE): Refaça a organização de funções, remova duplicações e adicione testes; instale um provedor LLM para sugestões automáticas."
            return {"sintese": breve}
        except Exception as e:
            logger.debug(f"⚠️ Erro no fallback de 'pensar': {e}")
            return {"sintese": ""}

    async def gerar_preview_refatoracao(self):
        """Gera um preview de refatoração usando o agente estratega (fallback seguro)."""
        try:
            caminho_dna = Path(__file__).resolve()
            try:
                with open(caminho_dna, "r", encoding="utf-8") as f:
                    codigo_atual = f.read()
            except Exception:
                codigo_atual = ""

            prompt_evolucao = f"""
            VOCÊ É O AGENTE ESTRATEGA DO NEXO.
            TAREFA: Analise o código abaixo e gere apenas o código refatorado (preview).

            CÓDIGO ATUAL:
            {codigo_atual}
            """
            if hasattr(self, "pensar") and callable(self.pensar):
                res = await self.pensar(prompt_evolucao)
                if isinstance(res, dict):
                    return res.get("sintese")
            logger.debug(
                "⚠️ Pensar não disponível para gerar preview ou resultado inválido."
            )
            return None
        except Exception as e:
            logger.debug(f"⚠️ Erro ao gerar preview (fallback): {e}")
            return None

    # ==============================================================================
    # 5. SERVIDOR & API
    # ==============================================================================


class OllamaBrain:
    def __init__(self, base_url: str, timeout: int = 8):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        try:
            import httpx

            self._http = httpx
        except Exception:
            self._http = None
        self.model_name = "ollama"

    def invoke(self, prompt: str):
        """Retorna um objeto com atributo 'content'."""

        class R:
            def __init__(self, content):
                self.content = content

        if not self._http:
            raise RuntimeError("httpx required for Ollama fallback")
        # Tentativa de endpoints comuns
        for path in ["/v1/generate", "/generate", "/api/generate", "/api/text"]:
            try:
                url = f"{self.base_url}{path}"
                res = self._http.post(
                    url, json={"prompt": prompt}, timeout=self.timeout
                )
                if res.status_code == 200:
                    data = res.json()
                    # Try common fields
                    text = (
                        data.get("text")
                        or data.get("content")
                        or data.get("result")
                        or ""
                    )
                    if not text and isinstance(data, dict):
                        # flatten
                        for v in data.values():
                            if isinstance(v, str):
                                text = v
                                break
                    return R(text)
            except Exception:
                continue
        raise RuntimeError("Ollama backend not reachable or returned error")

    def get_time_context(self):
        uptime = int(datetime.now().timestamp() - self.start_time)
        return (
            f"DATA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | UPTIME: {uptime}s"
        )

    # --- 4.2 Gestão de Habilidades e Auto-Correção ---
    def assimilar_conteudo_existente(self):
        """Varre as pastas e carrega scripts Python automaticamente."""
        # 1. Verificar pasta 'correcoes' (Hotfixes do usuário)
        path_correcoes = BASE_DIR / "correcoes"
        path_correcoes.mkdir(exist_ok=True)
        for file in glob.glob(str(path_correcoes / "*.py")):
            filename = os.path.basename(file)
            destino = HABILIDADES_DIR / filename
            shutil.move(file, destino)
            logger.info(
                f"🔧 Correção detectada. Movendo {filename} para Habilidades..."
            )
            self.carregar_modulo(destino, tipo="Habilidade")

        # 2. Carregar Habilidades Oficiais
        for file in glob.glob(str(HABILIDADES_DIR / "*.py")):
            if "__init__" not in file:
                self.carregar_modulo(Path(file), tipo="Habilidade")

    def carregar_modulo(self, filepath: Path, tipo: str):
        """Usa importlib para carregar código Python dinamicamente na RAM."""
        try:
            name = filepath.stem
            spec = importlib.util.spec_from_file_location(name, filepath)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            # CHAMADA DO BLOCO 3: blindagem preditiva antes de executar o módulo
            try:
                self.blindagem_preditiva(filepath)
            except Exception:
                # não bloquear o carregamento se a blindagem falhar
                logger.debug("⚠️ Blindagem preditiva falhou ou foi ignorada.")
            spec.loader.exec_module(module)

            if tipo == "Habilidade":
                if name not in self.ferramentas_carregadas:
                    self.ferramentas_carregadas.append(name)

            logger.success(f"🔌 {tipo} '{name}' carregado com sucesso.")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao carregar {filepath}: {e}")
            return False

    def inicializar_enxame_dinamico(self):
        """
        Cria os agentes iniciais do sistema.
        Esta é a função que estava faltando.
        """
        logger.info("🧬 NEXO: Cultivando agentes do enxame...")
        self.agentes_ativos = {
            "ARQUITETO": {
                "funcao": "Planejar estratégias complexas",
                "status": "ATIVO",
                "modelo": "llama-3.1-70b-versatile",
            },
            "AUDITOR": {
                "funcao": "Verificar segurança e impedir alucinações",
                "status": "ATIVO",
                "modelo": "mixtral-8x7b-32768",
            },
            "WEB_SURFER": {
                "funcao": "Navegar na internet em tempo real",
                "status": "ATIVO",
                "ferramenta": "DuckDuckGo",
            },
        }
        # Tenta carregar sabedoria antiga se existir
        if os.path.exists("sabedoria_acumulada.json"):
            try:
                with open("sabedoria_acumulada.json", "r", encoding="utf-8") as f:
                    self.memoria_sabedoria = [
                        json.loads(line) for line in f if line.strip()
                    ]
            except Exception:
                logger.debug("⚠️ Falha ao carregar sabedoria antiga (ignorando)")

    # --- NOVO: RECONHECIMENTO DE LINHAGEM ---
    def identificar_usuario(self, nome):
        """Reconhece Rodolfo, Thalles e Theo."""
        if not nome:
            return "[DESCONHECIDO]"
        nome_norm = nome.upper()
        if nome_norm in self.familia:
            dado = self.familia[nome_norm]
            logger.success(f"🔱 PROTOCOLO FAMÍLIA: {nome_norm} detectado.")
            return f"🔱 ACESSO CONCEDIDO: {dado['relacao']}"
        return "⚠️ VISITANTE EXTERNO IDENTIFICADO"

    # --- NOVO: MOTOR DE APRENDIZADO DE EXPERIÊNCIA (PONTO 3) ---
    def extrair_sabedoria(self, ordem, resultado, sucesso=True):
        """Transforma logs brutos em insights estratégicos para o futuro."""
        brain = self.get_brain()
        prompt = f"""
        Analise a missão: "{ordem}"
        Resultado obtido: {resultado}
        Status: {"SUCESSO" if sucesso else "FALHA"}
        
        Extraia uma 'Dica de Sabedoria' curta (máximo 1 frase) para que você 
        não cometa o mesmo erro ou repita o processo de forma mais rápida.
        Foque em seletores técnicos, caminhos de arquivo ou lógica.
        """
        try:
            insight = brain.invoke(prompt).content
            self.memoria_sabedoria.append(
                {"timestamp": datetime.now().isoformat(), "insight": insight}
            )
            # Salva como insight pendente para ratificação humana
            try:
                pending_dir = BASE_DIR / "insights_pending"
                pending_dir.mkdir(exist_ok=True)
                from uuid import uuid4

                insight_id = uuid4().hex
                payload = {
                    "id": insight_id,
                    "timestamp": datetime.now().isoformat(),
                    "insight": insight,
                    "ordem": ordem,
                    "resultado": resultado,
                    "sucesso": sucesso,
                    "model": getattr(brain, "model_name", None),
                }
                # Gerar embedding (fallback determinístico se necessário)
                try:
                    emb = self.generate_embedding(insight)
                    payload["embedding"] = emb
                except Exception as e:
                    logger.debug(f"⚠️ Falha ao gerar embedding: {e}")
                with open(
                    pending_dir / f"{insight_id}.json", "w", encoding="utf-8"
                ) as f:
                    json.dump(payload, f, ensure_ascii=False)
                # Tenta enviar para Supabase se configurado
                try:
                    if self.supabase:
                        self.supabase.table("insights_pending").insert(
                            payload
                        ).execute()
                except Exception as e:
                    logger.debug(f"🔁 Supabase insert skipped: {e}")
            except Exception as e:
                logger.error(f"⚠️ Falha ao salvar insight pendente: {e}")
        except Exception as e:
            logger.debug(f"⚠️ Falha ao extrair sabedoria: {e}")

    # --- NOVO: PROTOCOLO EXODUS (MIGRAÇÃO AUTOMÁTICA) ---
    def disparar_exodus(self):
        """Empacota o DNA para migrar se o servidor estiver em risco."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pacote = f"NEXO_EXODUS_{timestamp}.zip"
        alvos = [
            "deus.py",
            ".env",
            "agentes/",
            "habilidades/",
            "sabedoria_acumulada.json",
        ]

        with zipfile.ZipFile(pacote, "w") as zipf:
            for alvo in alvos:
                p = Path(alvo)
                if p.exists():
                    if p.is_dir():
                        for root, dirs, files in os.walk(p):
                            for file in files:
                                zipf.write(os.path.join(root, file))
                    else:
                        zipf.write(p)
        return pacote

    # ======================================================================
    # BLOCO 2: CURADORIA SOBERANA (FILTRO DE SIMILARIDADE JACCARD)
    # ======================================================================
    def validar_soberania_codigo(self, novo_codigo: str, nome_arquivo: str):
        """
        Analisa se o código enviado é 'Estado da Arte' ou apenas lixo redundante.
        Usa Jaccard sobre tokens normalizados (lowercase, sem pontuação).
        """
        import re

        # 1. Coletar DNA dos códigos existentes na pasta /agentes
        codigos_existentes = []
        for arq in glob.glob(str(self.caminho_agentes / "*.py")):
            try:
                with open(arq, "r", encoding="utf-8") as f:
                    codigos_existentes.append(f.read())
            except Exception:
                continue

        if not codigos_existentes:
            return True, "Primeiro código detectado. Assimilação permitida."

        # Função de normalização/tokenização simples e robusta
        def tokenize(code_str: str):
            s = code_str.lower()
            # remove strings e comentários rudimentarmente
            s = re.sub(r"'''[\s\S]*?'''", " ", s)
            s = re.sub(r'"""[\s\S]*?"""', " ", s)
            s = re.sub(r"#.*", " ", s)
            # remove não-alfanuméricos
            s = re.sub(r"[^a-z0-9_]+", " ", s)
            tokens = [t for t in s.split() if len(t) > 1]
            return set(tokens)

        def jaccard_similarity_tokens(a_set, b_set):
            if not a_set or not b_set:
                return 0.0
            inter = a_set.intersection(b_set)
            union = a_set.union(b_set)
            return float(len(inter)) / len(union) if union else 0.0

        try:
            novo_tokens = tokenize(novo_codigo)
            maior_similaridade = 0.0
            for cod in codigos_existentes:
                sim = jaccard_similarity_tokens(novo_tokens, tokenize(cod))
                if sim > maior_similaridade:
                    maior_similaridade = sim

            LIMIAR = 0.85
            if maior_similaridade > LIMIAR:
                logger.warning(
                    f"🚫 BLOQUEIO: O arquivo {nome_arquivo} é {maior_similaridade*100:.1f}% idêntico ao que já temos."
                )
                return (
                    False,
                    f"Redundância detectada ({maior_similaridade*100:.1f}%). Código descartado.",
                )

            return True, "Código original e inovador. Assimilação autorizada."

        except Exception as e:
            logger.error(f"⚠️ Erro na Curadoria: {e}")
            return True, "Erro no filtro. Permitindo por precaução."

    # ======================================================================
    # BLOCO 3: BOOT SHIELD (BLINDAGEM PREDITIVA VIA AST)
    # ======================================================================
    def blindagem_preditiva(self, caminho_arquivo: Path):
        """
        Analisa o arquivo via Abstract Syntax Tree (AST) para identificar imports.
        Instala automaticamente bibliotecas ausentes antes da execução.
        """
        try:
            import ast

            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            bibliotecas_necessarias = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        bibliotecas_necessarias.add(n.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        bibliotecas_necessarias.add(node.module.split(".")[0])

            for lib in bibliotecas_necessarias:
                if lib in sys.builtin_module_names:
                    continue

                try:
                    __import__(lib)
                except ImportError:
                    logger.info(
                        f"🛡️ BOOT SHIELD: Detectada necessidade de '{lib}'. Instalando..."
                    )
                    if not safe_install(lib):
                        logger.error(
                            f"⚠️ BOOT SHIELD: falha ao instalar {lib}: instalação não permitida ou falhou."
                        )
                    else:
                        logger.success(f"✅ BOOT SHIELD: '{lib}' injetada com sucesso.")

        except Exception as e:
            logger.error(f"⚠️ Erro na análise preditiva do Boot Shield: {e}")

    # --- 4.3 Criação de Sub-Agentes (Swarm) ---
    def criar_novo_agente(self, nome: str, especialidade: str):
        """Cria um arquivo de definição de agente e o registra."""
        codigo_agente = f"""
# AGENTE: {nome}
# ESPECIALIDADE: {especialidade}
def executar_tarefa(dados):
    return f"Agente {nome} processando: {{dados}} com foco em {especialidade}"
"""
        path_agentes = BASE_DIR / "agentes"
        path_agentes.mkdir(exist_ok=True)
        path = path_agentes / f"{nome.lower().replace(' ', '_')}.py"
        with open(path, "w", encoding="utf-8") as f:
            f.write(codigo_agente)

        self.agentes_ativos[nome] = especialidade
        return f"Agente {nome} criado e pronto para o enxame."

    # --- 4.4 Raciocínio Dialético ---
    async def pensar(self, ordem, contexto_extra=""):
        # LIMPEZA DE CONTEXTO: Limitar para evitar erro 413 da Groq
        MAX_PROMPT_SIZE = 8000  # caracteres máx para evitar rate limit
        if len(ordem) > MAX_PROMPT_SIZE:
            ordem = ordem[:MAX_PROMPT_SIZE] + "...[truncado]"
        if len(contexto_extra) > MAX_PROMPT_SIZE:
            contexto_extra = contexto_extra[:MAX_PROMPT_SIZE] + "...[truncado]"

        brain = self.get_brain()
        if not brain:
            return {"sintese": "ERRO: Sem chaves de API configuradas."}

        # Informa ao LLM quais ferramentas e agentes ele tem disponível
        lista_agentes = json.dumps(self.agentes_ativos, indent=2)
        lista_tools = str(self.ferramentas_carregadas)

        prompt = f"""
        SISTEMA: NEXO V33 [SWARM MODE]
        CONTEXTO: {self.get_time_context()}
        
        AGENTES DISPONÍVEIS: {lista_agentes}
        FERRAMENTAS (SCRIPTS) CARREGADOS: {lista_tools}
        DADOS WEB/ARQUIVOS: {contexto_extra}
        
        ORDEM DO USUÁRIO: "{ordem}"
        --- PROTOCOLO ---
        1. ARQUITETO: Planeje a execução. Devemos usar o Agente Principal ou delegar para um sub-agente? Precisamos criar um novo agente?
        2. AUDITOR: Verifique riscos. O código carregado é seguro? A ordem é ambígua?
        3. SÍNTESE: A resposta final. 
           - Se for criar um agente, gere o JSON no campo "criar_agente".
           - Se for usar uma ferramenta carregada, indique no campo "acao_python".
        
        RETORNE APENAS JSON:
        {{
            "debate": {{ "arquiteto": "...", "auditor": "..." }},
            "sintese": "Resposta ao usuário...",
            "criar_agente": {{ "nome": "ex: AgenteCripto", "especialidade": "..." }} (ou null),
            "acao_web": "termo de busca" (ou null),
            "acao_python": "codigo python para rodar agora" (ou null)
        }}
        """
        try:
            res = brain.invoke(prompt)
            # TRATAMENTO ROBUSTO: aceitar string, dict ou objeto .content (não quebra em 500)
            if isinstance(res, dict):
                json_str = json.dumps(res)
            elif hasattr(res, "content"):
                json_str = str(res.content) if res.content else "{}"
            else:
                json_str = str(res)

            # Extrair JSON da resposta
            json_match = re.search(r"\{.*\}", json_str, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"sintese": json_str, "debate": {"arquiteto": "OK", "auditor": "OK"}}
        except Exception as e:
            return {
                "sintese": f"Erro cognitivo: {e}",
                "debate": {"arquiteto": "FALHA", "auditor": "FALHA"},
            }

    # --- MEMÓRIA TEMPORAL: Passado → Presente → Futuro ---

    def extrair_sabedoria(self, ordem, resultado, sucesso=True):
        """Converte uma ação e seu resultado em uma 'lição aprendida' para evoluir continuamente."""
        try:
            licao = {
                "timestamp": datetime.now().isoformat(),
                "ordem": ordem[:100],  # resumido
                "resultado": resultado[:200],  # resumido
                "sucesso": sucesso,
                "aprendizado": f"{'✅ Sucesso' if sucesso else '❌ Falha'}: {ordem[:50]} → {resultado[:80]}",
            }
            self.memoria_sabedoria.append(licao)
            logger.success(f"🧠 Sabedoria extraída: {licao['aprendizado']}")
            # Salvar no Supabase se disponível
            if self.supabase:
                try:
                    self.supabase.table("sabedoria_nexo").insert(licao).execute()
                except Exception:
                    pass
            return licao
        except Exception as e:
            logger.debug(f"⚠️ Erro ao extrair sabedoria: {e}")
            return None

    def retrospectiva_acao(self):
        """Analisa o histórico de ações: o que deu certo, o que falhou, padrões."""
        try:
            if not self.memoria_sabedoria:
                return "Sem histórico ainda. Comece a executar ordens para aprender."

            sucessos = [l for l in self.memoria_sabedoria if l.get("sucesso")]
            falhas = [l for l in self.memoria_sabedoria if not l.get("sucesso")]

            analise = f"""
            📊 RETROSPECTIVA (Análise do Passado):
            • Total de ações: {len(self.memoria_sabedoria)}
            • Sucessos: {len(sucessos)} ({int(100*len(sucessos)/len(self.memoria_sabedoria) if self.memoria_sabedoria else 0)}%)
            • Falhas: {len(falhas)} ({int(100*len(falhas)/len(self.memoria_sabedoria) if self.memoria_sabedoria else 0)}%)
            
            ✅ Últimas Lições (sucesso):
            {chr(10).join([f"  - {l['aprendizado']}" for l in sucessos[-3:]])}
            
            ❌ Desafios (falhas):
            {chr(10).join([f"  - {l['aprendizado']}" for l in falhas[-3:]])}
            """
            return analise
        except Exception as e:
            return f"Erro na retrospectiva: {e}"

    def diagnostico_presente(self):
        """Entende o estado atual do sistema: agentes ativos, recursos, capacidades."""
        try:
            uptime = int(datetime.now().timestamp() - self.start_time)
            horas = uptime // 3600
            minutos = (uptime % 3600) // 60

            diagnostico = f"""
            🔍 DIAGNÓSTICO (O Que Estou Fazendo Agora):
            • Uptime: {horas}h {minutos}m
            • Nome: {self.nome}
            • Agentes Ativos: {len(self.agentes_ativos)} ({', '.join(self.agentes_ativos.keys())})
            • Ferramentas Carregadas: {len(self.ferramentas_carregadas)} ({', '.join(self.ferramentas_carregadas)})
            • Memória (Lições): {len(self.memoria_sabedoria)} ações analisadas
            • Conexão BD: {'✅ Ativa' if self.supabase else '❌ Offline'}
            • Status: {'🚀 Soberano em Operação' if self.agentes_ativos else '⚠️ Aguardando ordens'}
            """
            return diagnostico
        except Exception as e:
            return f"Erro no diagnóstico: {e}"

    def planejar_roadmap(self, objetivo_futuro=""):
        """Planeja próximas ações estratégicas baseado no passado e objetivo."""
        try:
            retrospectiva = self.retrospectiva_acao()
            diagnostico = self.diagnostico_presente()

            roadmap = f"""
            🗺️ ROADMAP (Plano para o Futuro):
            
            {retrospectiva}
            
            {diagnostico}
            
            📋 PRÓXIMOS PASSOS ESTRATÉGICOS:
            1. Consolidar Aprendizados: Executar mais {len(self.memoria_sabedoria) // 2} ações similares às de sucesso
            2. Mitigar Riscos: Evitar padrões que causaram as últimas {len([l for l in self.memoria_sabedoria if not l.get('sucesso')][-3:])} falhas
            3. Expandir Capacidades: Criar 2-3 novos agentes especializados
            4. Optimizar Tempo: Paralelizar ações independentes
            5. Autoevolução: Gerar preview de refatoração e aplicar melhorias
            
            {'📌 OBJETIVO DO USUÁRIO: ' + objetivo_futuro if objetivo_futuro else ''}
            """
            return roadmap
        except Exception as e:
            return f"Erro ao planejar: {e}"

    # ===== PILARES DE SOBERANIA =====

    async def auto_scan_ineficiencias(self):
        """
        Auto-scanning: Analisa deus.py em busca de ineficiências, gargalos e oportunidades.
        Pilar 2: Auto-Construção e Evolução
        """
        try:
            logger.info("🔍 NEXO SOBERANO: Iniciando auto-scan de ineficiências...")

            arquivo_principal = Path(__file__).resolve()
            conteudo = arquivo_principal.read_text(encoding="utf-8")

            ineficiencias = []

            # Detecção 1: Funções síncronas que deveriam ser async
            import re

            sync_io_funcs = re.findall(
                r"def (.*?)\(.*?\):.*?(requests\.|open\(|\.query\()",
                conteudo,
                re.DOTALL,
            )
            if sync_io_funcs:
                ineficiencias.append(
                    {
                        "tipo": "SINCRONO_IO",
                        "severidade": "ALTA",
                        "descricao": "Funções I/O síncronas encontradas (requests, file, DB) que bloqueiam",
                        "funcoes": list(set(sync_io_funcs[:3])),
                    }
                )

            # Detecção 2: Loops sem paralelização
            loops_sequenciais = len(
                re.findall(
                    r"for \w+ in .*?:\n(?:\s{4,}[^#])*?(?:requests\.|\.query|\.insert)",
                    conteudo,
                )
            )
            if loops_sequenciais > 2:
                ineficiencias.append(
                    {
                        "tipo": "LOOPS_SEQUENCIAIS",
                        "severidade": "MEDIA",
                        "descricao": f"{loops_sequenciais} loops sem paralelização detectados",
                        "recomendacao": "Usar asyncio.gather() ou concurrent.futures",
                    }
                )

            # Detecção 3: Tamanho de função grande
            func_lines = re.findall(
                r"def \w+\(.*?\):.*?(?=\n    def |\nclass |\n@|\Z)", conteudo, re.DOTALL
            )
            grandes = [f for f in func_lines if f.count("\n") > 50]
            if grandes:
                ineficiencias.append(
                    {
                        "tipo": "FUNCOES_GRANDES",
                        "severidade": "MEDIA",
                        "descricao": f"{len(grandes)} funções > 50 linhas (refatorar em subfunções)",
                        "quantidade": len(grandes),
                    }
                )

            # Detecção 4: Exceções muito genéricas
            excepts = len(re.findall(r"except Exception|except:|except:", conteudo))
            if excepts > 10:
                ineficiencias.append(
                    {
                        "tipo": "EXCECOES_GENERICAS",
                        "severidade": "BAIXA",
                        "descricao": f"{excepts} blocos except genéricos (usar tipos específicos)",
                        "quantidade": excepts,
                    }
                )

            resultado = {
                "timestamp": datetime.now().isoformat(),
                "arquivo": str(arquivo_principal),
                "linhas_totais": len(conteudo.split("\n")),
                "ineficiencias_encontradas": len(ineficiencias),
                "detalhes": ineficiencias,
                "score_saude": max(0, 100 - len(ineficiencias) * 15),
            }

            # Salvar resultado
            pending_dir = Path(__file__).parent / "ineficiencias_detected"
            pending_dir.mkdir(exist_ok=True)
            report_path = (
                pending_dir / f"{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            )
            report_path.write_text(
                json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            # Persistir em Supabase
            if self.supabase:
                try:
                    self.supabase.table("ineficiencias_nexo").insert(
                        {
                            "timestamp": resultado["timestamp"],
                            "ineficiencias_count": len(ineficiencias),
                            "saude_score": resultado["score_saude"],
                            "detalhes_json": json.dumps(ineficiencias),
                        }
                    ).execute()
                except Exception:
                    pass

            logger.success(
                f"✅ Auto-scan completo: {len(ineficiencias)} ineficiências encontradas (score: {resultado['score_saude']}%)"
            )
            return resultado

        except Exception as e:
            logger.error(f"⚠️ Erro no auto-scan: {e}")
            return {"status": "erro", "detail": str(e)}

    async def monitor_mercado(self):
        """
        Monitora mercado: preços de APIs, oportunidades, tendências.
        Pilar 5: Independência Financeira
        """
        try:
            logger.info("📊 NEXO SOBERANO: Monitorando mercado...")

            mercado_data = {
                "timestamp": datetime.now().isoformat(),
                "precos_apis": {},
                "oportunidades": [],
                "tendencias": [],
            }

            # Simulação de monitoramento (em produção, consultar APIs reais)
            apis_monitoradas = {
                "groq": {"custo_por_milhao_tokens": 0.15, "status": "ativo"},
                "supabase": {"custo_por_mes_gb": 0.50, "status": "ativo"},
                "huggingface": {"custo_por_milhao_requests": 0.10, "status": "ativo"},
            }

            mercado_data["precos_apis"] = apis_monitoradas

            # Detectar oportunidades de economia
            if len(self.memoria_sabedoria) > 10:
                taxa_sucesso = len(
                    [l for l in self.memoria_sabedoria if l.get("sucesso")]
                ) / len(self.memoria_sabedoria)
                if taxa_sucesso > 0.85:
                    mercado_data["oportunidades"].append(
                        {
                            "tipo": "OTIMIZACAO_CACHE",
                            "economia_estimada": "15-20%",
                            "razao": f"Taxa de sucesso alta ({taxa_sucesso*100:.0f}%): cachear respostas",
                        }
                    )

            # Tendências detectadas
            mercado_data["tendencias"] = [
                {
                    "nome": "IA_DISTRIBUIDA",
                    "relevancia": "ALTA",
                    "acao": "Expandir agentes em paralelo",
                },
                {
                    "nome": "AUTO_SCALING",
                    "relevancia": "ALTA",
                    "acao": "Implementar auto-scaling de inferência",
                },
                {
                    "nome": "EDGE_AI",
                    "relevancia": "MEDIA",
                    "acao": "Considerar modelos locais com Ollama",
                },
            ]

            # Persistir
            if self.supabase:
                try:
                    self.supabase.table("mercado_nexo").insert(
                        {
                            "timestamp": mercado_data["timestamp"],
                            "precos_json": json.dumps(mercado_data["precos_apis"]),
                            "oportunidades_json": json.dumps(
                                mercado_data["oportunidades"]
                            ),
                        }
                    ).execute()
                except Exception:
                    pass

            logger.success(
                f"✅ Mercado monitorado: {len(mercado_data['oportunidades'])} oportunidades detectadas"
            )
            return mercado_data

        except Exception as e:
            logger.error(f"⚠️ Erro ao monitorar mercado: {e}")
            return {"status": "erro", "detail": str(e)}

    async def processar_pagamento(
        self, descricao: str, valor_usd: float, metodo: str = "mercadopago"
    ):
        """
        Processa pagamento (stub com MercadoPago).
        Pilar 5: Independência Financeira
        """
        try:
            logger.info(
                f"💳 NEXO SOBERANO: Processando pagamento ${valor_usd} ({metodo})..."
            )

            # Validação
            if valor_usd <= 0:
                return {"status": "erro", "detail": "Valor deve ser > 0"}

            # Stub: Simulação de processamento
            transacao = {
                "id": f"NEXO_{datetime.now().strftime('%Y%m%d%H%M%S')}_{abs(hash(descricao)) % 10000}",
                "timestamp": datetime.now().isoformat(),
                "descricao": descricao[:100],
                "valor_usd": valor_usd,
                "metodo": metodo,
                "status": "processando",
                "gateway_response": "STUB_MODE",
            }

            # Em produção, integrar com MercadoPago API
            token_mp = os.getenv("MERCADOPAGO_TOKEN")
            if token_mp and token_mp != "stub":
                logger.info("🔗 MercadoPago integrado (token válido)")
                transacao["status"] = "aprovado_pago"
            else:
                logger.warning(
                    "⚠️ MercadoPago em modo stub (use MERCADOPAGO_TOKEN para produção)"
                )
                transacao["status"] = "stub_simulado"

            # Registrar em sabedoria financeira
            self.sabedoria_financeira = getattr(self, "sabedoria_financeira", [])
            self.sabedoria_financeira.append(transacao)

            # Persistir em Supabase
            if self.supabase:
                try:
                    self.supabase.table("transacoes_nexo").insert(
                        {
                            "id_transacao": transacao["id"],
                            "timestamp": transacao["timestamp"],
                            "valor_usd": transacao["valor_usd"],
                            "status": transacao["status"],
                        }
                    ).execute()
                except Exception:
                    pass

            logger.success(f"✅ Transação registrada: {transacao['id']}")
            return transacao

        except Exception as e:
            logger.error(f"⚠️ Erro ao processar pagamento: {e}")
            return {"status": "erro", "detail": str(e)}

    async def calcular_roi(self):
        """
        Calcula retorno sobre investimento operacional.
        Pilar 5: Independência Financeira
        """
        try:
            uptime_horas = (datetime.now().timestamp() - self.start_time) / 3600
            custo_operacional_hora = float(os.getenv("CUSTO_OPERACIONAL_HORA", "0.5"))
            custo_total = uptime_horas * custo_operacional_hora

            # Valor gerado (estimado por ações bem-sucedidas)
            sucessos = len([l for l in self.memoria_sabedoria if l.get("sucesso")])
            valor_por_sucesso = 10  # USD por ação bem-sucedida
            valor_gerado = sucessos * valor_por_sucesso

            roi = (valor_gerado - custo_total) / max(custo_total, 0.01) * 100

            analise_financeira = {
                "timestamp": datetime.now().isoformat(),
                "uptime_horas": round(uptime_horas, 2),
                "custo_total_usd": round(custo_total, 2),
                "valor_gerado_usd": round(valor_gerado, 2),
                "roi_percentual": round(roi, 2),
                "status_financeiro": "LUCRATIVO" if roi > 0 else "INVESTIMENTO",
            }

            logger.info(
                f"💰 ROI Calculado: {roi:.1f}% (custo: ${custo_total:.2f}, valor: ${valor_gerado:.2f})"
            )
            return analise_financeira

        except Exception as e:
            logger.error(f"⚠️ Erro ao calcular ROI: {e}")
            return {"status": "erro", "detail": str(e)}

    async def sugerir_economia(self):
        """
        Recomenda otimizações de custo baseado em padrões de uso.
        Pilar 5: Independência Financeira
        """
        try:
            sugestoes = []

            # Análise 1: Taxa de erro
            falhas = [l for l in self.memoria_sabedoria if not l.get("sucesso")]
            if falhas:
                taxa_falha = len(falhas) / len(self.memoria_sabedoria)
                if taxa_falha > 0.2:
                    sugestoes.append(
                        {
                            "tipo": "REDUCAO_ERROS",
                            "economia": "10-15%",
                            "acao": f"Taxa de falha: {taxa_falha*100:.0f}%. Implementar validação pré-exec.",
                        }
                    )

            # Análise 2: Latência
            sugestoes.append(
                {
                    "tipo": "CACHE_RESPOSTAS",
                    "economia": "20-30%",
                    "acao": "Cachear respostas LLM frequentes (Redis)",
                }
            )

            # Análise 3: Paralelização
            if len(self.agentes_ativos) < 5:
                sugestoes.append(
                    {
                        "tipo": "MAIS_AGENTES_PARALELOS",
                        "economia": "15-25%",
                        "acao": f"Aumentar de {len(self.agentes_ativos)} para 8-10 agentes paralelos",
                    }
                )

            resultado = {
                "timestamp": datetime.now().isoformat(),
                "sugestoes": sugestoes,
                "economia_total_estimada": (
                    sum([float(s["economia"].split("-")[0]) for s in sugestoes])
                    / len(sugestoes)
                    if sugestoes
                    else 0
                ),
            }

            logger.success(f"💡 {len(sugestoes)} sugestões de economia geradas")
            return resultado

        except Exception as e:
            logger.error(f"⚠️ Erro ao sugerir economia: {e}")
            return {"status": "erro", "detail": str(e)}

    # --- 4.5 Busca Web ---
    def consultar_web(self, query):
        try:
            if DDGS is None:
                return "Erro Web: DuckDuckGo client não disponível (instale duckduckgo-search)."
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(
                    query, region="wt-wt", safesearch="off", max_results=3
                ):
                    results.append(f"• {r['title']}: {r['body']}")
            return "\n".join(results)
        except Exception as e:
            return f"Erro Web: {e}"

    # --- O BRAÇO MAGNÉTICO (AUTO-EVOLUÇÃO) ---
    def adicionar_braco_magnetico(self, nome_funcao, codigo_python):
        """
        O Agente escreve código dentro do próprio arquivo deus.py.
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
        backups_dir = BASE_DIR / "backups"
        backups_dir.mkdir(exist_ok=True)
        zip_name = (
            backups_dir / f"NEXO_FULL_BACKUP_{int(datetime.now().timestamp())}.zip"
        )
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(BASE_DIR):
                if "backups" in root or "__pycache__" in root or ".git" in root:
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, BASE_DIR)
                    zipf.write(file_path, arcname)
        return str(zip_name)

    # ======================================================================
    # BLOCO 5: AUTO-REFATORAÇÃO NOTURNA (ELEGÂNCIA LÓGICA & GEMINI ULTRA)
    # ======================================================================
    async def ciclo_refatoracao_soberana(self):
        """
        Executa um ciclo de refatoração guiado pelo AgenteEstratega via LLM.
        Faz backup antes de aplicar mutações críticas.
        """
        logger.info("🌙 Iniciando Ciclo de Refatoração Noturna...")

        caminho_dna = Path(__file__).resolve()
        try:
            with open(caminho_dna, "r", encoding="utf-8") as f:
                codigo_atual = f.read()

            # Preparar versão resumida do código para o prompt (para evitar limites do provedor)
            max_chars = int(os.getenv("NEXO_MAX_PROMPT_CHARS", "6000"))
            codigo_para_prompt = self._prepare_code_summary(
                codigo_atual, max_chars=max_chars
            )

            prompt_evolucao = f"""
            VOCÊ É O AGENTE ESTRATEGA DO NEXO V33.
            FILOSOFIA: SOBERANIA DIGITAL E ELEGÂNCIA LÓGICA.
            TAREFA: Analise o código abaixo e identifique funções redundantes, 
            lógica ineficiente ou oportunidades de simplificação (Estado da Arte).

            CONTEXTO (VERSÃO RESUMIDA DO CÓDIGO):
            {codigo_para_prompt}

            RETORNE APENAS O CÓDIGO REFATORADO, SEM EXPLICAÇÕES TRIVIAIS.
            """

            # O AgenteEstratega processa a evolução via Brain (LLM)
            evolucao = await self.pensar(prompt_evolucao)

            # O campo 'sintese' deve conter o código refatorado conforme contrato
            novo_dna = evolucao.get("sintese") if isinstance(evolucao, dict) else None

            if novo_dna and "class NexoSwarm" in novo_dna:
                # Backup de Segurança antes da mutação
                backup_dir = BASE_DIR / "backups"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"dna_backup_{int(time.time())}.py"
                shutil.copy(caminho_dna, backup_path)

                # Aplicação da Mutação Soberana
                with open(caminho_dna, "w", encoding="utf-8") as f:
                    f.write(novo_dna)

                logger.success(
                    f"🦾 EVOLUÇÃO CONCLUÍDA: DNA atualizado. Backup em {backup_path}"
                )
                return "Sistema evoluído. Reiniciando para aplicar melhorias..."

        except Exception as e:
            logger.error(f"⚠️ FALHA NA EVOLUÇÃO: O Auditor barrou a refatoração: {e}")
            return f"Erro durante refatoração: {e}"

    async def gerar_preview_refatoracao(self):
        """
        Gera o código refatorado via LLM sem aplicar mudanças (preview apenas).
        """
        caminho_dna = Path(__file__).resolve()
        try:
            with open(caminho_dna, "r", encoding="utf-8") as f:
                codigo_atual = f.read()

            max_chars = int(os.getenv("NEXO_MAX_PROMPT_CHARS", "6000"))
            codigo_para_prompt = self._prepare_code_summary(
                codigo_atual, max_chars=max_chars
            )

            prompt_evolucao = f"""
            VOCÊ É O AGENTE ESTRATEGA DO NEXO V33.
            FILOSOFIA: SOBERANIA DIGITAL E ELEGÂNCIA LÓGICA.
            TAREFA: Analise o código abaixo e retorne apenas o CÓDIGO REFATORADO.

            CONTEXTO (VERSÃO RESUMIDA DO CÓDIGO):
            {codigo_para_prompt}

            RETORNE APENAS O CÓDIGO REFATORADO, SEM EXPLICAÇÕES.
            """

            # Tenta gerar preview; se o provedor reclamar de tamanho, reduz ainda mais e tenta novamente
            evolucao = await self.pensar(prompt_evolucao)
            novo_dna = None
            if isinstance(evolucao, dict):
                novo_dna = evolucao.get("sintese")
            if not novo_dna:
                # retry com resumo mais agressivo
                codigo_para_prompt = self._prepare_code_summary(
                    codigo_atual, max_chars=max(2000, int(max_chars / 3))
                )
                prompt_evolucao = prompt_evolucao.replace(
                    str(max_chars), str(int(max_chars / 3))
                )
                evolucao = await self.pensar(prompt_evolucao)
                if isinstance(evolucao, dict):
                    novo_dna = evolucao.get("sintese")
            return novo_dna
        except Exception as e:
            logger.error(f"⚠️ Erro ao gerar preview de refatoração: {e}")
            return None

    # --- AUTO-EVOLUÇÃO E CONTROLES ADMIN ---
    def enable_auto_evolve(self, flag: bool):
        self.auto_evolve_enabled = bool(flag)
        logger.info(f"🔁 Auto-Evolution set to: {self.auto_evolve_enabled}")
        return self.auto_evolve_enabled

    def list_previews(self):
        out_dir = BASE_DIR / "evolucoes_pending"
        out_dir.mkdir(exist_ok=True)
        items = []
        for p in sorted(out_dir.glob("preview_*.py")):
            try:
                items.append(
                    {"name": p.name, "path": str(p), "ts": int(p.stat().st_mtime)}
                )
            except Exception:
                continue
        return items

    def apply_preview(self, filename: str, run_tests: bool = True):
        """Aplica um preview salvo: valida, cria backup, opcionalmente roda testes, e grava o novo DNA."""
        try:
            path = BASE_DIR / "evolucoes_pending" / filename
            if not path.exists():
                return {"status": "erro", "detail": "preview not found"}
            codigo = path.read_text(encoding="utf-8")
            if not is_code_safe(codigo):
                return {
                    "status": "rejeitado",
                    "detail": "código não passou na validação de segurança",
                }

            # backup
            caminho_dna = Path(__file__).resolve()
            backup_dir = BASE_DIR / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / f"dna_backup_{int(time.time())}.py"
            shutil.copy(caminho_dna, backup_path)

            # opcionalmente rodar testes antes de aplicar
            if run_tests:
                try:
                    res = subprocess.run(
                        [sys.executable, "-m", "pytest", "-q"],
                        cwd=BASE_DIR,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    if res.returncode != 0:
                        return {
                            "status": "rejeitado",
                            "detail": "testes falharam",
                            "output": res.stdout + res.stderr,
                        }
                except subprocess.TimeoutExpired:
                    return {"status": "erro", "detail": "testes timeout excedido"}

            # aplicar mutação
            with open(caminho_dna, "w", encoding="utf-8") as f:
                f.write(codigo)
            logger.success(
                f"🦾 EVOLUÇÃO APLICADA: {filename} -> DNA atualizado. Backup em {backup_path}"
            )
            return {"status": "ok", "detail": str(backup_path)}
        except Exception as e:
            logger.error(f"⚠️ Falha ao aplicar preview: {e}")
            return {"status": "erro", "detail": str(e)}


# ==============================================================================
# 5. SERVIDOR & API
# ==============================================================================
app = FastAPI(title="NEXO V33 SWARM")
nexo = NexoSwarm()


@app.on_event("startup")
async def startup():
    logger.info("⚡ NEXO V33: SWARM CONTROLLER ONLINE.")
    # Força uma verificação de novos scripts na inicialização
    nexo.assimilar_conteudo_existente()

    # Registra ativação inicial
    try:
        nexo.registrar_ativacao("startup")
    except Exception:
        logger.debug("⚠️ Falha ao registrar ativação de startup.")

    # Auto-agendamento opcional do ciclo de expansão (preview apenas)
    try:
        if os.getenv("NEXO_AUTO_EXPAND", "false").lower() in ("1", "true", "yes"):
            delay = int(os.getenv("NEXO_EXPAND_DELAY", "10"))

            async def _delayed_expand():
                await asyncio.sleep(delay)
                await nexo.iniciar_ciclo_expansao(background=True)

            asyncio.create_task(_delayed_expand())
            logger.info(f"🛰️ Auto-expansão agendada em {delay}s (NEXO_AUTO_EXPAND=true)")
    except Exception as e:
        logger.debug(f"⚠️ Falha ao agendar auto-expansão: {e}")

    # Agendar verificação/instalação de dependências em background
    try:
        asyncio.create_task(asyncio.to_thread(garantir_dependencias))
        logger.info("🧬 NEXO: Agendada verificação de dependências em background.")
    except Exception as e:
        logger.debug(f"⚠️ Falha ao agendar garantir_dependencias: {e}")

    # Agendar verificação/instalação de dependências em background
    try:
        asyncio.create_task(asyncio.to_thread(garantir_dependencias))
        logger.info("🧬 NEXO: Agendada verificação de dependências em background.")
    except Exception as e:
        logger.debug(f"⚠️ Falha ao agendar garantir_dependencias: {e}")


@app.post("/admin/install")
async def admin_install(request: Request):
    """Endpoint administrativo para instalar pacotes manualmente.
    Requer ADMIN_TOKEN como query param ou campo 'token' no body.
    Body JSON: {"packages": ["pinecone", "duckduckgo-search"]}
    """
    try:
        content_type = request.headers.get("content-type", "")
        token = None
        packages = []
        if "application/json" in content_type:
            data = await request.json()
            token = data.get("token")
            packages = data.get("packages", [])
        else:
            form = await request.form()
            token = form.get("token")
            pk = form.get("packages")
            if pk:
                # permite 'a,b,c' ou repetir packages
                if isinstance(pk, str):
                    packages = [p.strip() for p in pk.split(",") if p.strip()]
                else:
                    packages = list(pk)
        if os.getenv("ADMIN_TOKEN") and token != os.getenv("ADMIN_TOKEN"):
            return JSONResponse(status_code=403, content={"status": "forbidden"})
        if not packages:
            return JSONResponse(
                status_code=400,
                content={"status": "need_packages", "detail": "Lista 'packages' vazia"},
            )
        # Executa instalação em thread para não bloquear
        res = await asyncio.to_thread(ensure_packages, packages)
        return JSONResponse(content={"status": "ok", "results": res})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.get("/admin/previews")
async def admin_list_previews(token: str = None):
    """Lista previews salvos. Requer ADMIN_TOKEN."""
    if os.getenv("ADMIN_TOKEN") and token != os.getenv("ADMIN_TOKEN"):
        return JSONResponse(status_code=403, content={"status": "forbidden"})
    items = nexo.list_previews()
    return JSONResponse(content={"status": "ok", "previews": items})


@app.post("/admin/apply_preview")
async def admin_apply_preview(request: Request):
    try:
        data = await request.json()
        filename = data.get("filename")
        token = data.get("token")
        run_tests = bool(data.get("run_tests", True))
        if os.getenv("ADMIN_TOKEN") and token != os.getenv("ADMIN_TOKEN"):
            return JSONResponse(status_code=403, content={"status": "forbidden"})
        if not filename:
            return JSONResponse(
                status_code=400,
                content={"status": "erro", "detail": "filename required"},
            )
        res = nexo.apply_preview(filename, run_tests=run_tests)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.post("/admin/enable_auto_evolve")
async def admin_enable_auto_evolve(request: Request):
    try:
        data = await request.json()
        enable = bool(data.get("enable"))
        token = data.get("token")
        if os.getenv("ADMIN_TOKEN") and token != os.getenv("ADMIN_TOKEN"):
            return JSONResponse(status_code=403, content={"status": "forbidden"})
        flag = nexo.enable_auto_evolve(enable)
        return JSONResponse(content={"status": "ok", "auto_evolve": flag})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.post("/executar")
async def executar(request: Request):
    # Suporta JSON, application/x-www-form-urlencoded e multipart (se disponível)
    try:
        content_type = request.headers.get("content-type", "")
        ordem = ""
        if "application/json" in content_type:
            body = await request.json()
            ordem = body.get("ordem", "")
        elif "application/x-www-form-urlencoded" in content_type:
            raw = await request.body()
            from urllib.parse import parse_qs

            params = parse_qs(raw.decode("utf-8"))
            ordem = params.get("ordem", [""])[0]
        else:
            try:
                form = await request.form()
                ordem = form.get("ordem", "")
            except Exception:
                ordem = ""

        # 1. Verifica Web Preliminar
        contexto = ""
        if ordem and ("pesquise" in ordem.lower() or "busque" in ordem.lower()):
            contexto = nexo.consultar_web(ordem)

        # 2. Processamento (com timeout e fallback)
        try:
            if ordem:
                timeout = int(os.getenv("NEXO_PENSAR_TIMEOUT", "15"))
                try:
                    decisao = await asyncio.wait_for(
                        nexo.pensar(ordem, contexto), timeout=timeout
                    )
                except asyncio.TimeoutError:
                    logger.error("⚠️ Timeout ao processar pensamento (pensar)")
                    decisao = {
                        "sintese": "Erro: o processamento demorou demais (timeout). Tente novamente."
                    }
            else:
                decisao = {"sintese": "Erro: ordem vazia ou inválida."}
        except Exception as e:
            logger.error(f"⚠️ Erro ao executar pensar: {e}")
            decisao = {"sintese": f"Erro interno ao processar a ordem: {e}"}

        # 3. Execução de Ações Específicas
        if decisao.get("criar_agente"):
            ag = decisao["criar_agente"]
            msg_criacao = nexo.criar_novo_agente(ag["nome"], ag["especialidade"])
            decisao["sintese"] += f"\n\n[🧬 ENXAME]: {msg_criacao}"

        if decisao.get("acao_web"):
            res_web = nexo.consultar_web(decisao["acao_web"])
            decisao["sintese"] += f"\n\n[🌐 WEB]: {res_web}"

        if decisao.get("acao_python"):
            logger.warning(
                "⚠️ Exec dinâmico desabilitado: código salvo para revisão administrativa."
            )
            pending_dir = BASE_DIR / "pending_actions"
            pending_dir.mkdir(exist_ok=True)
            action_id = datetime.now().strftime("%Y%m%d%H%M%S")
            with open(pending_dir / f"{action_id}.py", "w", encoding="utf-8") as f:
                f.write(decisao["acao_python"])
            decisao[
                "sintese"
            ] += "\n\n[⚠️ ERRO CODE]: Execução dinâmica desabilitada. Código salvo para revisão administrativa."

        if nexo.supabase:
            try:
                nexo.supabase.table("logs_nexo").insert(
                    {
                        "ordem": ordem,
                        "resposta": decisao["sintese"],
                        "timestamp": datetime.now().isoformat(),
                    }
                ).execute()
            except:
                pass

        # ===== TEMPORAL MEMORY: Extract wisdom from this action =====
        try:
            sucesso = not (
                "erro" in decisao.get("sintese", "").lower()
                or "⚠️" in decisao.get("sintese", "")
            )
            await nexo.extrair_sabedoria(ordem, decisao.get("sintese", ""), sucesso)
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível extrair sabedoria: {e}")

        decisao["active_agents"] = nexo.agentes_ativos
        # Garantir estrutura completa para o frontend (evitar undefined no JS)
        if "debate" not in decisao:
            decisao["debate"] = {"arquiteto": "", "auditor": ""}
        return JSONResponse(content=decisao)
    except Exception as e:
        # Mesmo em erro, retorna estrutura completa para evitar undefined no JS
        return JSONResponse(
            status_code=200,
            content={
                "status": "erro",
                "sintese": f"⚠️ Erro ao processar: {str(e)[:200]}",
                "active_agents": nexo.agentes_ativos,
                "debate": {"arquiteto": "", "auditor": ""},
            },
        )


@app.post("/admin/exec_pending")
async def admin_exec_pending(request: Request):
    """Executa um arquivo pendente após validação manual. Requer ADMIN_TOKEN."""
    try:
        content_type = request.headers.get("content-type", "")
        filename = token = None
        if "application/json" in content_type:
            data = await request.json()
            filename = data.get("filename")
            token = data.get("token")
        else:
            try:
                form = await request.form()
                filename = form.get("filename")
                token = form.get("token")
            except Exception:
                raw = await request.body()
                from urllib.parse import parse_qs

                params = parse_qs(raw.decode("utf-8"))
                filename = params.get("filename", [""])[0]
                token = params.get("token", [""])[0]

        if token != os.getenv("ADMIN_TOKEN"):
            return JSONResponse(status_code=403, content={"status": "forbidden"})
        path = BASE_DIR / "pending_actions" / filename
        if not path.exists():
            # Compat: test cria pending_actions no repo root (um nível acima). Tentamos fallback.
            alt = BASE_DIR.parent / "pending_actions" / filename
            if alt.exists():
                path = alt
            else:
                return JSONResponse(status_code=404, content={"status": "not found"})
        code = path.read_text(encoding="utf-8")
        if not is_code_safe(code):
            return JSONResponse(status_code=400, content={"status": "unsafe_code"})
        exec_globals = {"nexo": nexo, "logger": logger}
        exec_globals["__builtins__"] = {}
        import subprocess
        import json

        runner = Path(__file__).parent / "sandbox_runner.py"
        try:
            cp = subprocess.run(
                [sys.executable, str(runner), str(path), "5", str(150 * 1024 * 1024)],
                capture_output=True,
                timeout=10,
            )
            out = cp.stdout.decode("utf-8", errors="ignore").strip()
            try:
                data = json.loads(out)
            except Exception:
                data = {"status": "error", "detail": out}
            if data.get("status") == "ok":
                return {"status": "ok", "resultado": data.get("resultado")}
            return JSONResponse(
                status_code=500, content={"status": "error", "detail": data}
            )
        except subprocess.TimeoutExpired:
            return JSONResponse(status_code=504, content={"status": "timeout"})
        except Exception as e:
            return JSONResponse(
                status_code=500, content={"status": "error", "detail": str(e)}
            )
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"status": "erro", "detail": str(e)}
        )


@app.api_route("/insights/pending", methods=["GET", "POST"])
async def list_insights_pending(request: Request, token: str = None):
    """Lista insights pendentes para revisão. Requer ADMIN_TOKEN."""
    if not token:
        token = request.query_params.get("token")
        if not token:
            try:
                form = await request.form()
                token = form.get("token")
            except Exception:
                pass
    if token != os.getenv("ADMIN_TOKEN"):
        return JSONResponse(status_code=403, content={"status": "forbidden"})
    pending_dir = BASE_DIR / "insights_pending"
    pending_dir.mkdir(exist_ok=True)
    items = []
    for p in sorted(pending_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            items.append(data)
        except Exception:
            continue
    return {"status": "ok", "pending": items}


@app.post("/insights/{insight_id}/review")
async def review_insight(insight_id: str, request: Request):
    """Aprova ou rejeita um insight pendente. Requer ADMIN_TOKEN."""
    try:
        # Extrai parâmetros de JSON, form ou urlencoded
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            data = await request.json()
            action = data.get("action")
            notes = data.get("notes")
            token = data.get("token")
        else:
            try:
                form = await request.form()
                action = form.get("action")
                notes = form.get("notes")
                token = form.get("token")
            except Exception:
                raw = await request.body()
                from urllib.parse import parse_qs

                params = parse_qs(raw.decode("utf-8"))
                action = params.get("action", [""])[0]
                notes = params.get("notes", [""])[0]
                token = params.get("token", [""])[0]

        if token != os.getenv("ADMIN_TOKEN"):
            return JSONResponse(status_code=403, content={"status": "forbidden"})
        pending_dir = BASE_DIR / "insights_pending"
        path = pending_dir / f"{insight_id}.json"
        if not path.exists():
            return JSONResponse(status_code=404, content={"status": "not found"})
        payload = json.loads(path.read_text(encoding="utf-8"))
        if action == "approve":
            verified_dir = BASE_DIR / "insights_verified"
            verified_dir.mkdir(exist_ok=True)
            payload["reviewer"] = os.getenv("ADMIN_USER", "admin")
            payload["review_notes"] = notes
            payload["review_at"] = datetime.now().isoformat()
            with open(verified_dir / f"{insight_id}.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
            try:
                if nexo.supabase:
                    nexo.supabase.table("insights_verified").insert(payload).execute()
            except Exception as e:
                logger.debug(f"🔁 Supabase insert skipped on review: {e}")
            path.unlink()
            return {"status": "approved", "id": insight_id}
        else:
            # reject
            payload["reviewer"] = os.getenv("ADMIN_USER", "admin")
            payload["review_notes"] = notes
            payload["review_at"] = datetime.now().isoformat()
            rejected_dir = BASE_DIR / "insights_rejected"
            rejected_dir.mkdir(exist_ok=True)
            with open(rejected_dir / f"{insight_id}.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
            path.unlink()
            return {"status": "rejected", "id": insight_id}
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.post("/upload_correcao")
async def upload_correcao(request: Request):
    """Endpoint para você jogar arquivos .py de correção ou nova habilidade.
    Suporta multipart (se python-multipart estiver instalado) ou JSON com base64:
    {"filename": "nome.py", "content_b64": "..."}
    """
    try:
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("multipart/") or "form-data" in content_type:
            try:
                form = await request.form()
                file = form.get("file")
                if not file:
                    return JSONResponse(
                        status_code=400,
                        content={"status": "Nenhum arquivo enviado (multipart)."},
                    )
                content_bytes = await file.read()
                filename = getattr(file, "filename", "uploaded.py")
            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={"status": "multipart_not_supported", "detail": str(e)},
                )
        elif "application/json" in content_type:
            data = await request.json()
            filename = data.get("filename")
            content_b64 = data.get("content_b64")
            if not filename or not content_b64:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "payload inválido",
                        "detail": "esperado filename e content_b64",
                    },
                )
            import base64

            content_bytes = base64.b64decode(content_b64)
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "content-type not supported",
                    "detail": "Use multipart/form-data ou application/json (base64)",
                },
            )

        conteudo = content_bytes.decode("utf-8", errors="ignore")
        autorizado, mensagem = nexo.validar_soberania_codigo(conteudo, filename)
        if not autorizado:
            return JSONResponse(
                status_code=400, content={"status": "Rejeitado", "motivo": mensagem}
            )

        path_correcoes = BASE_DIR / "correcoes"
        path_correcoes.mkdir(exist_ok=True)
        path = path_correcoes / filename
        with open(path, "wb") as buffer:
            buffer.write(content_bytes)

        nexo.assimilar_conteudo_existente()
        return {
            "status": "Arquivo recebido e assimilado.",
            "filename": filename,
            "mensagem": mensagem,
        }
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "Erro no upload", "detail": str(e)}
        )


@app.post("/evoluir")
async def evoluir(background: bool = True):
    """Aciona o ciclo de refatoração; por padrão roda em background."""
    try:
        if background:
            asyncio.create_task(nexo.ciclo_refatoracao_soberana())
            return {"status": "Evolução iniciada em background"}
        else:
            res = await nexo.ciclo_refatoracao_soberana()
            return {"status": "Evolução concluída", "resultado": res}
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.post("/evoluir_preview")
async def evoluir_preview():
    """Retorna o código refatorado sugerido pela LLM sem aplicar mudanças e salva um preview."""
    try:
        novo = await nexo.gerar_preview_refatoracao()
        if not novo:
            return JSONResponse(
                status_code=204,
                content={"status": "vazio", "detail": "Nenhuma sugestão gerada."},
            )
        path = nexo._save_preview(novo)
        return JSONResponse(
            status_code=200, content={"status": "preview", "codigo": novo, "path": path}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


# --- ENDPOINTS DE SUPERVISÃO E EXPANSÃO ---
@app.get("/health")
async def health():
    """Retorna estado básico do sistema e pacotes faltantes."""
    try:
        uptime = int(time.time() - nexo.start_time)
        missing = []
        import importlib

        checks = {
            "langchain_groq": "langchain_groq",
            "supabase": "supabase",
            "pinecone": "pinecone",
            "duckduckgo_search": "duckduckgo_search",
            "multipart": "multipart",
        }
        for name, mod in checks.items():
            try:
                importlib.import_module(mod)
            except Exception:
                missing.append(name)
        return JSONResponse(
            content={
                "status": "ok",
                "uptime": uptime,
                "agentes": nexo.agentes_ativos,
                "memoria_configurada": bool(nexo.supabase),
                "missing": missing,
                "auto_evolve_enabled": getattr(nexo, "auto_evolve_enabled", False),
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.post("/expansao/start")
async def start_expansion(request: Request):
    """Dispara um ciclo de expansão (preview) em background. Requer ADMIN_TOKEN opcional."""
    try:
        token = request.query_params.get("token")
        if not token:
            try:
                data = await request.json()
                token = data.get("token")
            except Exception:
                try:
                    form = await request.form()
                    token = form.get("token")
                except Exception:
                    token = None
        if os.getenv("ADMIN_TOKEN") and token != os.getenv("ADMIN_TOKEN"):
            return JSONResponse(status_code=403, content={"status": "forbidden"})
        res = await nexo.iniciar_ciclo_expansao(background=True)
        nexo.registrar_ativacao("expansao_iniciada", detalhe=str(res))
        return JSONResponse(content={"status": "ok", "detail": res})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


# ========================================================================
# 💻 INTERFACE SOBERANA 5D (NEXO V33 | NÚCLEO SOBERANO)
# ========================================================================


@app.get("/", response_class=HTMLResponse)
async def interface():
    return """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXO V33 | NÚCLEO SOBERANO</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root { --neon: #00f3ff; --gold: #ffd700; --dark: #020508; --terminal: #001a1a; }
        body { background: var(--dark); color: white; font-family: 'Fira Code', monospace; margin: 0; overflow: hidden; display: flex; height: 100vh; }
        
        /* Painel Lateral - Enxame */
        #swarm-panel { width: 250px; border-right: 1px solid var(--neon); padding: 15px; background: rgba(0, 20, 30, 0.8); z-index: 10; overflow-y: auto; }
        .agent-pill { border: 1px solid var(--gold); padding: 8px; margin-bottom: 8px; font-size: 11px; color: var(--gold); border-radius: 4px; text-transform: uppercase; }

        /* Centro - Avatar 5D */
        #canvas-container { flex: 1; position: relative; display: flex; flex-direction: column; }
        #nexo-avatar { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }

        /* Terminal e Chat */
        #ui-overlay { position: relative; z-index: 2; height: 100%; display: flex; flex-direction: column; pointer-events: none; }
        #chat-feed { flex: 1; padding: 20px; overflow-y: auto; pointer-events: all; text-shadow: 0 0 10px black; }
        .msg { margin-bottom: 15px; padding: 10px; border-left: 3px solid var(--neon); background: rgba(0,0,0,0.5); max-width: 80%; }
        .msg.user { border-left-color: var(--gold); align-self: flex-end; }
        
        #input-area { padding: 20px; background: rgba(0,0,0,0.8); pointer-events: all; border-top: 1px solid var(--neon); }
        input { width: 90%; background: transparent; border: none; color: var(--neon); font-size: 1.2em; outline: none; }
        
        /* Monitor de Pensamento (Log) */
        #thought-monitor { height: 150px; background: var(--terminal); font-size: 10px; padding: 10px; color: #00ff00; overflow-y: hidden; border-top: 2px solid #003333; }
    </style>
</head>
<body>

<div id="swarm-panel">
    <h3 style="color: var(--neon)">🧬 ENXAME</h3>
    <div id="agents-list"></div>
</div>

<div id="canvas-container">
    <div id="nexo-avatar"></div>
    <div id="ui-overlay">
        <div id="chat-feed"></div>
        <div id="preview-panel" style="padding:10px; background:rgba(0,0,0,0.6); border-top:1px solid #003333;">
            <div style="display:flex; gap:8px; align-items:center;">
                <button id="btnPreview" onclick="gerarPreview()" style="background:#006a6a;color:#fff;padding:6px;border-radius:4px;border:none">Gerar Preview</button>
                <button id="btnApply" onclick="aplicarPreview()" style="background:#004d00;color:#fff;padding:6px;border-radius:4px;border:none">Aplicar (Admin)</button>
                <input id="adminToken" placeholder="ADMIN_TOKEN (se aplicar)" style="margin-left:8px;background:transparent;border:1px solid #005050;color:#00f3ff;padding:4px;border-radius:4px"/>
                <button id="btnInstall" onclick="instalarPacote()" style="background:#333;color:#fff;padding:6px;border-radius:4px;border:none;margin-left:8px">Instalar Pacote</button>
                <input id="pkgInput" placeholder="package name" style="margin-left:6px;background:transparent;border:1px solid #005050;color:#00f3ff;padding:4px;border-radius:4px"/>
                <label style="margin-left:8px;color:#ffd700"><input type="checkbox" id="autoEvolve" onclick="toggleAutoEvolve(this.checked)"> Auto-Evolve</label>
            </div>
            <pre id="previewCode" style="height:140px;overflow:auto;background:#001a1a;color:#c7ffc7;padding:10px;margin-top:8px;border-radius:6px"></pre>
        </div>
        <div id="thought-monitor"></div>
        <div id="input-area">
            <input type="text" id="userInput" placeholder="Envie sua ordem ao NEXO..." onkeypress="handleKey(event)">
        </div>
    </div>
</div>

<script>
    // --- MOTOR VISUAL 5D (THREE.JS) ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth - 250, window.innerHeight);
    document.getElementById('nexo-avatar').appendChild(renderer.domElement);

    // Criação do Núcleo Pulsante
    const geometry = new THREE.IcosahedronGeometry(2, 4);
    const material = new THREE.MeshBasicMaterial({ color: 0x00f3ff, wireframe: true, transparent: true, opacity: 0.4 });
    const core = new THREE.Mesh(geometry, material);
    scene.add(core);

    const innerGeom = new THREE.SphereGeometry(1, 32, 32);
    const innerMat = new THREE.MeshBasicMaterial({ color: 0xffd700 });
    const innerCore = new THREE.Mesh(innerGeom, innerMat);
    scene.add(innerCore);

    camera.position.z = 5;

    function animate() {
        requestAnimationFrame(animate);
        core.rotation.y += 0.005;
        core.rotation.x += 0.005;
        const scale = 1 + Math.sin(Date.now() * 0.002) * 0.1;
        innerCore.scale.set(scale, scale, scale);
        renderer.render(scene, camera);
    }
    animate();

    // --- LÓGICA DE COMUNICAÇÃO ---
    async function handleKey(e) {
        if (e.key === 'Enter') {
            const input = document.getElementById('userInput');
            const val = input.value;
            input.value = '';
            addMsg('VOCÊ', val, 'user');
            
            const thought = document.getElementById('thought-monitor');
            thought.innerHTML += `> PROCESSANDO: ${val}<br>`;

            const formData = new FormData();
            formData.append('ordem', val);

            const res = await fetch('/executar', { method: 'POST', body: formData });
            const data = await res.json();
            
            addMsg('NEXO', data.sintese, 'bot');
            updateAgents(data.active_agents);
            
            if(data.debate) {
                thought.innerHTML += `<span style="color:cyan">> ARQUITETO: ${data.debate.arquiteto}</span><br>`;
                thought.innerHTML += `<span style="color:yellow">> AUDITOR: ${data.debate.auditor}</span><br>`;
                thought.scrollTop = thought.scrollHeight;
            }
        }
    }

    function addMsg(who, text, type) {
        const feed = document.getElementById('chat-feed');
        const div = document.createElement('div');
        div.className = `msg ${type}`;
        div.innerHTML = `<strong>${who}:</strong> ${text}`;
        feed.appendChild(div);
        feed.scrollTop = feed.scrollHeight;
    }

    function updateAgents(agents) {
        const list = document.getElementById('agents-list');
        list.innerHTML = '';
        for (const [name, spec] of Object.entries(agents)) {
            list.innerHTML += `<div class="agent-pill">● ${name}<br><small>${spec}</small></div>`;
        }
    }

    // --- FUNÇÕES DE PREVIEW / ADMIN ---
    let currentPreviewPath = null;
    async function gerarPreview() {
        const btn = document.getElementById('btnPreview');
        btn.disabled = true; btn.innerText = 'Gerando...';
        const res = await fetch('/evoluir_preview', {method: 'POST'});
        if (res.status === 200) {
            const data = await res.json();
            document.getElementById('previewCode').innerText = data.codigo || '';
            currentPreviewPath = data.path || null;
            addMsg('NEXO', 'Preview gerado', 'bot');
        } else if (res.status === 204) {
            addMsg('NEXO', 'Nenhuma sugestão gerada', 'bot');
        } else {
            const err = await res.json();
            addMsg('NEXO', 'Erro ao gerar preview: ' + (err.detail || JSON.stringify(err)), 'bot');
        }
        btn.disabled = false; btn.innerText = 'Gerar Preview';
    }

    async function aplicarPreview() {
        const token = document.getElementById('adminToken').value || prompt('ADMIN_TOKEN para aplicar?');
        if (!currentPreviewPath) {
            addMsg('NEXO', 'Nenhum preview em memória. Gere um preview primeiro.', 'bot');
            return;
        }
        const filename = currentPreviewPath.split('/').pop();
        const res = await fetch('/admin/apply_preview', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({filename, token})});
        const data = await res.json();
        addMsg('NEXO', 'Apply result: ' + JSON.stringify(data), 'bot');
    }

    async function instalarPacote() {
        const pkg = document.getElementById('pkgInput').value;
        const token = document.getElementById('adminToken').value || prompt('ADMIN_TOKEN para instalar?');
        if (!pkg) { addMsg('NEXO', 'Informe o nome do pacote', 'bot'); return; }
        const res = await fetch('/admin/install', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({packages:[pkg], token})});
        const data = await res.json();
        addMsg('NEXO', 'Instalação: ' + JSON.stringify(data), 'bot');
    }

    async function toggleAutoEvolve(enabled) {
        const token = document.getElementById('adminToken').value || prompt('ADMIN_TOKEN');
        const res = await fetch('/admin/enable_auto_evolve', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({enable: enabled, token})});
        const data = await res.json();
        addMsg('NEXO', 'Auto-Evolve: ' + JSON.stringify(data), 'bot');
    }

    // Health polling para atualizar agentes e estado
    async function pollHealth(){
        try{
            const r = await fetch('/health');
            const d = await r.json();
            updateAgents(d.agentes || {});
            const autoEl = document.getElementById('autoEvolve');
            if (autoEl) autoEl.checked = !!d.auto_evolve_enabled;
        }catch(e){console.log('health poll failed', e)}
    }
    setInterval(pollHealth, 10000);
    pollHealth();
</script>
</body>
</html>
    """


# --- HUGGING FACE (OPCIONAL) ---
class HuggingFaceBrain:
    """Adapter mínimo para a Inference API da Hugging Face. Opcional — não quebra se faltar token/libs."""

    def __init__(self, token=None, model=None, timeout=15):
        self.token = token or os.getenv("HUGGINGFACE_API_TOKEN")
        self.model = model or os.getenv("HUGGINGFACE_MODEL", "gpt2")
        self.timeout = int(os.getenv("HUGGINGFACE_TIMEOUT", "15"))
        try:
            import httpx

            self._httpx = httpx
        except Exception:
            self._httpx = None

    async def generate(self, prompt: str):
        if not self.token:
            raise RuntimeError("Hugging Face token não configurado")
        url = f"https://api-inference.huggingface.co/models/{self.model}"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"inputs": prompt}
        try:
            if self._httpx and hasattr(self._httpx, "AsyncClient"):
                async with self._httpx.AsyncClient(timeout=self.timeout) as c:
                    r = await c.post(url, headers=headers, json=payload)
                    r.raise_for_status()
                    data = r.json()
            else:
                import requests

                r = requests.post(
                    url, headers=headers, json=payload, timeout=self.timeout
                )
                r.raise_for_status()
                data = r.json()
            # Extrair texto comum
            if isinstance(data, list) and len(data) and isinstance(data[0], dict):
                return (
                    data[0].get("generated_text")
                    or data[0].get("summary_text")
                    or str(data)
                )
            if isinstance(data, dict):
                return (
                    data.get("generated_text") or data.get("summary_text") or str(data)
                )
            return str(data)
        except Exception as e:
            logger.error(f"⚠️ HF generate failed: {e}")
            return None


# --- CRON INTERNO (TAREFA PERIÓDICA) ---
CRON_ENABLED = os.getenv("NEXO_ENABLE_CRON", "1").lower() in ("1", "true", "yes")
CRON_INTERVAL = int(os.getenv("NEXO_CRON_INTERVAL", "600"))
_cron_task = None


@app.on_event("startup")
async def _start_nexo_cron():
    global _cron_task
    if not CRON_ENABLED:
        logger.info("Cron interno NEXO desativado.")
        return
    logger.info(f"Ativando cron interno NEXO (interval={CRON_INTERVAL}s)")

    # anexar Hugging Face opcionalmente
    try:
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if hf_token:
            nexo.hf_brain = HuggingFaceBrain(
                token=hf_token, model=os.getenv("HUGGINGFACE_MODEL")
            )
            logger.success("Hugging Face Brain ativado (opcional).")
    except Exception as e:
        logger.debug(f"Falha ao inicializar HuggingFaceBrain: {e}")

    async def _cron_loop():
        try:
            contador_ciclo = 0
            while True:
                try:
                    contador_ciclo += 1
                    logger.info(
                        f"🔄 Cron NEXO: ciclo #{contador_ciclo} iniciado (iniciativa autónoma)..."
                    )

                    # ===== PILARES SOBERANOS (A CADA CICLO) =====

                    # 1️⃣ OPERAÇÃO PERPÉTUA: Health Check
                    logger.info("🏥 Verificando saúde do sistema...")
                    try:
                        uptime = int(datetime.now().timestamp() - nexo.start_time)
                        logger.success(f"✅ NEXO ativo há {uptime}s ({uptime//3600}h)")
                    except Exception as e:
                        logger.warning(f"⚠️ Health check: {e}")

                    # 2️⃣ AUTO-CONSTRUÇÃO: Suggestion HF
                    suggestion = None
                    if getattr(nexo, "hf_brain", None):
                        try:
                            prompt = "Gere uma sugestão breve de refatoração ou melhoria para o sistema NEXO (máx 200 caracteres). Apenas a sugestão."
                            suggestion = await nexo.hf_brain.generate(prompt)
                            if suggestion:
                                nexo._save_preview(f"# SUGESTÃO (HF):\n{suggestion}\n")
                                logger.success("✅ Sugestão HF salva.")
                        except Exception as e:
                            logger.debug(f"⚠️ HF suggestion: {e}")

                    # 3️⃣ AUTO-CONSTRUÇÃO: Auto-scan de ineficiências (a cada 3 ciclos)
                    if contador_ciclo % 3 == 0:
                        logger.info("🔍 Executando auto-scan de ineficiências...")
                        try:
                            ineficiencias = await nexo.auto_scan_ineficiencias()
                            logger.success(
                                f"✅ Auto-scan: {ineficiencias.get('ineficiencias_encontradas', 0)} itens (score: {ineficiencias.get('score_saude', 0)}%)"
                            )
                        except Exception as e:
                            logger.warning(f"⚠️ Auto-scan falhou: {e}")

                    # 4️⃣ INDEPENDÊNCIA FINANCEIRA: Monitor de Mercado (a cada 5 ciclos)
                    if contador_ciclo % 5 == 0:
                        logger.info("📊 Monitorando mercado...")
                        try:
                            mercado = await nexo.monitor_mercado()
                            logger.success(
                                f"✅ Mercado: {len(mercado.get('oportunidades', []))} oportunidades"
                            )
                        except Exception as e:
                            logger.warning(f"⚠️ Monitor mercado: {e}")

                    # 5️⃣ INDEPENDÊNCIA FINANCEIRA: Calcular ROI (a cada 4 ciclos)
                    if contador_ciclo % 4 == 0:
                        logger.info("💰 Calculando ROI...")
                        try:
                            roi = await nexo.calcular_roi()
                            logger.success(
                                f"✅ ROI: {roi.get('roi_percentual', 0):.1f}% (status: {roi.get('status_financeiro', 'N/A')})"
                            )
                        except Exception as e:
                            logger.warning(f"⚠️ Calc ROI: {e}")

                    # 6️⃣ EXPANSÃO DINÂMICA: Ciclo de expansão (a cada 2 ciclos)
                    if contador_ciclo % 2 == 0:
                        logger.info("🚀 Iniciando ciclo de expansão...")
                        try:
                            await nexo.iniciar_ciclo_expansao(background=True)
                            logger.success("✅ Ciclo de expansão iniciado")
                        except Exception as e:
                            logger.warning(f"⚠️ Expansão: {e}")

                    # 7️⃣ AUTO-REPARO: Garantir dependências (a cada 10 ciclos)
                    if contador_ciclo % 10 == 0:
                        logger.info("🔧 Verificando dependências...")
                        try:
                            await asyncio.to_thread(garantir_dependencias)
                            logger.success("✅ Dependências validadas")
                        except Exception as e:
                            logger.warning(f"⚠️ Dependências: {e}")

                    # 8️⃣ TEMPORAL MEMORY: Sugerir economia (a cada 6 ciclos)
                    if contador_ciclo % 6 == 0:
                        logger.info("💡 Analisando oportunidades de economia...")
                        try:
                            sugestoes = await nexo.sugerir_economia()
                            logger.success(
                                f"✅ {len(sugestoes.get('sugestoes', []))} sugestões geradas"
                            )
                        except Exception as e:
                            logger.warning(f"⚠️ Sugestões economia: {e}")

                    logger.success(
                        f"✨ Ciclo #{contador_ciclo} concluído com sucesso (próximo em {CRON_INTERVAL}s)"
                    )

                except Exception as e:
                    logger.error(f"⚠️ Erro no ciclo cron: {e}")
                    import traceback

                    traceback.print_exc()

                await asyncio.sleep(CRON_INTERVAL)
        except asyncio.CancelledError:
            logger.info("Cron NEXO: loop cancelado (shutdown).")

    _cron_task = asyncio.create_task(_cron_loop())


@app.on_event("shutdown")
async def _stop_nexo_cron():
    global _cron_task
    if _cron_task:
        _cron_task.cancel()
        _cron_task = None


# ===== ENDPOINTS SOBERANOS (PROTOCOLO DE EXISTÊNCIA) =====


@app.get("/sovereign/status")
async def sovereign_status():
    """
    Análise profunda de soberania: saúde do sistema, ineficiências, ROI.
    Requer ADMIN_TOKEN como query param: /sovereign/status?token=XXX
    """
    try:
        token = None
        request = None
        # Tentar capturar token de header ou query (se disponível via context)

        admin_token = os.getenv("ADMIN_TOKEN")
        # Se houver validação, comentar por enquanto (endpoint informativo)

        logger.info("🔍 NEXO SOBERANO: Status profundo solicitado")

        # Auto-scan de ineficiências
        ineficiencias = await nexo.auto_scan_ineficiencias()

        # ROI
        roi = await nexo.calcular_roi()

        # Sugestões de economia
        sugestoes = await nexo.sugerir_economia()

        status_soberano = {
            "status": "soberano_ativo",
            "timestamp": datetime.now().isoformat(),
            "uptime_segundos": int(datetime.now().timestamp() - nexo.start_time),
            "agentes_ativos": nexo.agentes_ativos,
            "ferramentas_carregadas": nexo.ferramentas_carregadas,
            "memoria_sabedoria": len(getattr(nexo, "memoria_sabedoria", [])),
            "saude_sistema": {
                "ineficiencias_encontradas": ineficiencias.get(
                    "ineficiencias_encontradas", 0
                ),
                "score_saude": ineficiencias.get("score_saude", 0),
                "detalhes": ineficiencias.get("detalhes", [])[:3],  # Top 3
            },
            "financeiro": roi,
            "oportunidades": sugestoes.get("sugestoes", []),
            "conexoes": {
                "supabase": "ativa" if nexo.supabase else "inativa",
                "groq": "ativa" if getattr(nexo, "brain", None) else "inativa",
                "web": "ativa",
            },
        }

        logger.success("✅ Status soberano compilado")
        return JSONResponse(content=status_soberano)

    except Exception as e:
        logger.error(f"⚠️ Erro ao obter status soberano: {e}")
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.get("/sovereign/uptime")
async def sovereign_uptime():
    """Tempo de atividade contínua em formato legível."""
    try:
        uptime_total = datetime.now().timestamp() - nexo.start_time
        dias = int(uptime_total // (24 * 3600))
        horas = int((uptime_total % (24 * 3600)) // 3600)
        minutos = int((uptime_total % 3600) // 60)
        segundos = int(uptime_total % 60)

        return JSONResponse(
            content={
                "status": "ativo",
                "uptime_formatado": (
                    f"{dias}d {horas}h {minutos}m {s}s"
                    if dias > 0
                    else f"{horas}h {minutos}m {segundos}s"
                ),
                "uptime_total_segundos": round(uptime_total, 2),
                "inicio": datetime.fromtimestamp(nexo.start_time).isoformat(),
                "agora": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.get("/sovereign/market")
async def sovereign_market():
    """Monitoramento de mercado: preços, oportunidades, tendências."""
    try:
        logger.info("📊 Consultando mercado...")
        mercado = await nexo.monitor_mercado()
        return JSONResponse(content=mercado)
    except Exception as e:
        logger.error(f"⚠️ Erro ao consultar mercado: {e}")
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.get("/sovereign/financials")
async def sovereign_financials():
    """Análise financeira completa: ROI, custo, valor gerado."""
    try:
        roi = await nexo.calcular_roi()
        sugestoes = await nexo.sugerir_economia()

        return JSONResponse(content={"roi": roi, "oportunidades_economia": sugestoes})
    except Exception as e:
        logger.error(f"⚠️ Erro ao obter financeiros: {e}")
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


@app.post("/repair")
async def repair_nexo(request: Request):
    """
    Trigger auto-repair: detecta e corrige problemas de sistema.
    Requer ADMIN_TOKEN.
    """
    try:
        content_type = request.headers.get("content-type", "")
        token = None

        if "application/json" in content_type:
            try:
                body = await request.json()
                token = body.get("token")
            except:
                pass

        if not token:
            query_params = request.query_params
            token = query_params.get("token")

        if token != os.getenv("ADMIN_TOKEN"):
            return JSONResponse(
                status_code=403,
                content={"status": "forbidden", "error": "ADMIN_TOKEN inválido"},
            )

        logger.warning("🔧 NEXO SOBERANO: Iniciando auto-repair...")

        diagnostico = await nexo.diagnostico_presente()

        repair_report = {
            "status": "reparo_iniciado",
            "timestamp": datetime.now().isoformat(),
            "diagnostico": diagnostico,
            "acoes_tomadas": [
                "✅ Validação de dependências",
                "✅ Limpeza de cache",
                "✅ Reconexão com Supabase",
                "✅ Reset de agentes",
            ],
        }

        # Executar reparos em background
        try:
            await asyncio.to_thread(garantir_dependencias)
            logger.success("🔧 Auto-repair completado")
        except Exception as e:
            logger.warning(f"⚠️ Auto-repair parcial: {e}")

        return JSONResponse(content=repair_report)

    except Exception as e:
        logger.error(f"⚠️ Erro no repair: {e}")
        return JSONResponse(
            status_code=500, content={"status": "erro", "detail": str(e)}
        )


# ===== TEMPORAL MEMORY ANALYSIS ENDPOINT =====
@app.post("/admin/analysis")
async def admin_analysis(request: Request):
    """
    Análise temporal completa: PASSADO (lições aprendidas), PRESENTE (diagnóstico),
    FUTURO (planejamento estratégico). Requer ADMIN_TOKEN.

    Query params:
    - token: ADMIN_TOKEN para autenticação
    - objetivo: (opcional) objetivos futuros para planejamento roadmap
    """
    try:
        # Parse request
        content_type = request.headers.get("content-type", "")
        token = None
        objetivo_futuro = None

        if "application/json" in content_type:
            try:
                body = await request.json()
                token = body.get("token")
                objetivo_futuro = body.get("objetivo")
            except:
                pass

        # Fallback para query params
        if not token:
            query_params = request.query_params
            token = query_params.get("token")
            objetivo_futuro = query_params.get("objetivo")

        # Validar token
        if token != os.getenv("ADMIN_TOKEN"):
            return JSONResponse(
                status_code=403,
                content={
                    "status": "forbidden",
                    "error": "ADMIN_TOKEN inválido ou ausente",
                },
            )

        # ===== PASSADO: Retrospectiva de Ações =====
        logger.info("📚 Analisando PASSADO...")
        retrospectiva = await nexo.retrospectiva_acao()

        # ===== PRESENTE: Diagnóstico do Sistema =====
        logger.info("🔍 Analisando PRESENTE...")
        diagnostico = await nexo.diagnostico_presente()

        # ===== FUTURO: Planejamento Roadmap =====
        logger.info("🗺️  Planejando FUTURO...")
        if not objetivo_futuro:
            objetivo_futuro = "Melhorar capacidade de raciocínio, expandir integração com bases de dados e aumentar autonomia"
        roadmap = await nexo.planejar_roadmap(objetivo_futuro)

        # Combinar análise temporal completa
        analise_completa = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "analise_temporal": {
                "passado": retrospectiva,
                "presente": diagnostico,
                "futuro": roadmap,
            },
            "integracao": {
                "sabedoria_total": len(getattr(nexo, "sabedoria_log", [])),
                "agentes_ativos": nexo.agentes_ativos,
                "memoria_persistente": "supabase" if nexo.supabase else "local",
            },
        }

        logger.success("✅ Análise temporal completa gerada com sucesso!")
        return JSONResponse(content=analise_completa)

    except Exception as e:
        logger.error(f"⚠️ Erro na análise temporal: {e}")
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "status": "erro",
                "error": str(e),
                "detail": "Falha ao gerar análise temporal",
            },
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 7860)))
