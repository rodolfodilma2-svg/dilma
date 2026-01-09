import os
import supabase
from groq import Groq

# Configurações do Ambiente Cloud (Hugging Face)
GROQ_CLIENT = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Pastas no padrão Linux/Docker
BASE_DIR = "/home/user/app"
SANDBOX_DIR = os.path.join(BASE_DIR, "sandbox")


def nexo_auto_evolucao():
    # 1. Buscar objetivo no Supabase (Em vez de manual)
    res = (
        supabase_client.table("kernel_goals")
        .select("*")
        .eq("status", "pending")
        .limit(1)
        .execute()
    )

    if not res.data:
        print("💤 [NEXO] Nenhuma ordem de evolução encontrada no Supabase.")
        return

    tarefa = res.data[0]
    instrucao = tarefa["goal_description"]
    id_tarefa = tarefa["id"]

    print(f"🧬 [DNA-EVOLUTION] Ordem recebida: {instrucao}")

    # 2. Motor de Construção (Groq)
    prompt = f"Você é o Nexo v6.0. Escreva um script Python profissional para: {instrucao}. Use caminhos relativos. Retorne APENAS o código puro."

    try:
        completion = GROQ_CLIENT.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        codigo = completion.choices[0].message.content
        # Limpeza de Markdown
        if "```python" in codigo:
            codigo = codigo.split("```python")[1].split("```")[0].strip()

        # 3. Guardar na Sandbox para o Guardião validar
        if not os.path.exists(SANDBOX_DIR):
            os.makedirs(SANDBOX_DIR)
        nome_ficheiro = f"evolucao_{id_tarefa}.py"
        caminho_final = os.path.join(SANDBOX_DIR, nome_ficheiro)

        with open(caminho_final, "w", encoding="utf-8") as f:
            f.write(codigo)

        print(
            f"✅ [SUCESSO] Módulo construído em {caminho_final}. Aguardando Guardião..."
        )

        # Aqui o NEXO atualizaria o status no Supabase para 'validating'
        supabase_client.table("kernel_goals").update({"status": "validating"}).eq(
            "id", id_tarefa
        ).execute()

    except Exception as e:
        print(f"❌ [ERRO] Falha na auto-construção: {e}")


if __name__ == "__main__":
    nexo_auto_evolucao()
