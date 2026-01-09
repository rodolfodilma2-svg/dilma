import requests
from bs4 import BeautifulSoup


def executar(query):
    """
    Realiza uma busca simples na web e extrai títulos e links.
    """
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        resultados = []
        for g in soup.find_all("div", class_="tF2Cxc"):
            title = g.find("h3").text if g.find("h3") else "Sem título"
            link = g.find("a")["href"] if g.find("a") else "Sem link"
            resultados.append(f"{title}: {link}")

        if not resultados:
            # Fallback para busca simplificada se a estrutura do Google mudar
            return f"Busca realizada para: {query}. Verifique manualmente em {url}"

        return "\n".join(resultados[:5])
    except Exception as e:
        return f"Erro na busca: {e}"
