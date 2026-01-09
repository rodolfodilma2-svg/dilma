# 1. Base: Mantive o Python 3.10-slim para máxima compatibilidade
FROM python:3.10-slim

# 2. Sistema: Mantive as ferramentas essenciais para compilar pacotes
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Organização: Mantive o diretório de trabalho e a cópia de ficheiros
WORKDIR /app
COPY . .

# 4. Arsenal: Mantive os teus e ADICIONEI o python-multipart e o supabase
# Sem o python-multipart, o FastAPI dá erro ao ler formulários (o erro que viste)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    langchain \
    langchain-groq \
    langchain-community \
    python-dotenv \
    duckduckgo-search \
    psutil \
    python-multipart \
    supabase

# 5. Rede: Mantive a porta 7860 exigida pelo Hugging Face
EXPOSE 7860

# 6. Execução: Ajustei o comando para garantir que o Uvicorn rode o ficheiro deus.py
# O formato "deus:app" diz ao Uvicorn: "procure a variável 'app' dentro do arquivo 'deus.py'"
CMD ["uvicorn", "deus:app", "--host", "0.0.0.0", "--port", "7860"]