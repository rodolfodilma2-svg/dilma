import os
from huggingface_hub import HfApi, HfFileSystem


def executar(acao, repo_id=None, caminho_local=None, caminho_repo=None):
    """
    Sincroniza código e modelos com o Hugging Face.
    """
    token = os.getenv("HF_TOKEN")
    if not token:
        return "Erro: HF_TOKEN não configurado."

    api = HfApi(token=token)
    fs = HfFileSystem(token=token)

    try:
        if acao == "upload":
            api.upload_file(
                path_or_fileobj=caminho_local,
                path_in_repo=caminho_repo,
                repo_id=repo_id,
                repo_type="space",  # Ou "model"/"dataset"
            )
            return f"Upload de {caminho_local} para {repo_id} concluído."

        elif acao == "download":
            # Exemplo de leitura direta
            with fs.open(f"{repo_id}/{caminho_repo}", "r") as f:
                content = f.read()
            return content

        return "Ação HF inválida."
    except Exception as e:
        return f"Erro no Hugging Face: {e}"
