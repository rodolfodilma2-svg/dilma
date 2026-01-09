import subprocess
from pathlib import Path


def executar(comando, linguagem="shell", codigo=None, nome_extensao=None):
    """
    Gerencia e executa extensões em diferentes linguagens.
    """
    EXTENSOES_DIR = Path(__file__).parent.parent / "extensoes"
    EXTENSOES_DIR.mkdir(exist_ok=True)

    if codigo and nome_extensao:
        ext_path = EXTENSOES_DIR / nome_extensao
        with open(ext_path, "w", encoding="utf-8") as f:
            f.write(codigo)
        return f"Extensão {nome_extensao} salva em {ext_path}"

    try:
        if linguagem == "shell":
            result = subprocess.run(comando, shell=True, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else result.stderr
        elif linguagem == "node":
            result = subprocess.run(
                ["node", "-e", comando], capture_output=True, text=True
            )
            return result.stdout
        elif linguagem == "python":
            result = subprocess.run(
                ["python3", "-c", comando], capture_output=True, text=True
            )
            return result.stdout
        return "Linguagem não suportada."
    except Exception as e:
        return f"Erro ao executar extensão: {e}"
