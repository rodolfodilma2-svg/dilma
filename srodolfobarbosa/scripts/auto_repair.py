#!/usr/bin/env python3
"""Script simples de reparo automático (ferramenta de arquivo):
- roda ruff --fix e black
- executa pytest e coleta falhas
- tenta detectar ImportError simples e recomenda instalação

Use com cautela (executa pip install quando detectar pacotes faltando apenas se AUTO_INSTALL=true)
"""
import subprocess
import re

AUTO_INSTALL = (
    "true" == str(__import__("os").environ.get("AUTO_INSTALL", "true")).lower()
)


def run(cmd, check=False):
    print(f"> {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print(r.stderr)
    if check and r.returncode != 0:
        raise SystemExit(r.returncode)
    return r


def fix_style(unsafe=False):
    run("python -m pip install --no-cache-dir ruff black", check=False)
    if unsafe:
        # '--unsafe-fixes' may change semantics; use com cautela
        run("ruff check --fix --unsafe-fixes . || true")
    else:
        run("ruff check --fix . || true")
    run("black . || true")


import os
import time
import argparse


def run_tests_and_autofix_imports():
    r = run("pytest -q || true")
    out = (r.stdout or "") + (r.stderr or "")
    # procurar padrões de ImportError: No module named 'foo'
    missing = set(re.findall(r"No module named '([\w_\-]+)'", out))
    if missing:
        print("Pacotes possivelmente faltando detectados:", missing)
        if AUTO_INSTALL:
            for pkg in missing:
                print(f"Tentando instalar {pkg}...")
                run(f"python -m pip install --no-cache-dir {pkg}")
            print("Reexecutando testes...")
            run("pytest -q", check=False)
    return out


# ----------------------
# Funções de PR automático
# ----------------------

def git_has_changes():
    r = run("git status --porcelain")
    return bool(r.stdout.strip())


def create_branch_and_push(branch):
    print(f"Criando branch {branch} e empurrando as mudanças...")
    run(f"git checkout -b {branch}")
    run("git add -A")
    run("git commit -m \"chore(auto-repair): apply automatic fixes\" || true")
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if token and repo:
        remote = f"https://x-access-token:{token}@github.com/{repo}.git"
        run(f"git push -u {remote} HEAD:{branch}")
    else:
        # fallback: push to origin (requires push rights)
        run(f"git push -u origin {branch}")


def add_labels_and_assignees(owner, repo_name, issue_number, labels=None, assignees=None):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN não configurado — não é possível adicionar labels/assignees via API")
        return
    import json
    import urllib.request

    if labels:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}/labels"
        data = json.dumps({"labels": labels}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                print("Labels adicionadas:", labels)
        except Exception as e:
            print("Falha ao adicionar labels:", e)

    if assignees:
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}/assignees"
        data = json.dumps({"assignees": assignees}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                print("Assignees adicionados:", assignees)
        except Exception as e:
            print("Falha ao adicionar assignees:", e)


def create_pr_via_api(branch, title, body, labels=None, assignees=None, enable_auto_merge=False):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("GITHUB_TOKEN ou GITHUB_REPOSITORY não configurados — não consigo criar PR via API")
        return None
    owner, repo_name = repo.split("/")
    import json
    import urllib.request

    url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
    data = json.dumps({"title": title, "head": branch, "base": "main", "body": body}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            obj = json.loads(resp_body)
            print("PR criada:", obj.get("html_url"))

            number = obj.get("number")
            node_id = obj.get("node_id")
            # adicionar labels e assignees
            add_labels_and_assignees(owner, repo_name, number, labels=labels, assignees=assignees)

            # habilitar auto-merge via GraphQL (se solicitado)
            if enable_auto_merge and node_id:
                gql_url = "https://api.github.com/graphql"
                mutation = {
                    "query": "mutation enableAutoMerge($input: EnablePullRequestAutoMergeInput!){ enablePullRequestAutoMerge(input: $input){clientMutationId} }",
                    "variables": {"input": {"pullRequestId": node_id, "mergeMethod": "SQUASH"}}
                }
                req2 = urllib.request.Request(gql_url, data=json.dumps(mutation).encode("utf-8"), headers={"Authorization": f"bearer {token}", "Accept": "application/vnd.github+json"}, method="POST")
                try:
                    with urllib.request.urlopen(req2) as resp2:
                        print("Solicitado enable auto-merge para a PR")
                except Exception as e:
                    print("Falha ao habilitar auto-merge via GraphQL:", e)

            return obj
    except Exception as e:
        print("Falha ao criar PR via API:", e)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto repair and optional PR creation")
    parser.add_argument("--open-pr", action="store_true", help="Se verdadeiro, abre um PR com as mudanças detectadas")
    parser.add_argument("--branch-prefix", default="auto-repair", help="Prefixo para o branch automático")
    parser.add_argument("--commit-message", default="chore(auto-repair): apply automatic fixes", help="Mensagem de commit para as mudanças")
    parser.add_argument("--unsafe-fixes", action="store_true", help="Habilita 'ruff --unsafe-fixes' (pode alterar semântica) e é mais agressivo nas correções")
    parser.add_argument("--auto-merge", action="store_true", help="Tenta habilitar auto-merge na PR criada")
    parser.add_argument("--labels", default="auto-repair", help="Labels (vírgula separadas) para adicionar ao PR")
    parser.add_argument("--assignees", default=None, help="Assignees (vírgula separadas) para a PR")

    args = parser.parse_args()

    # Fase 0: Análise de logs via LLM (opcional, só se um arquivo for passado)
    llm_summary = None
    if args.log_file:
        try:
            from srodolfobarbosa.auto_repair.llm_log_analyst import LLMLogAnalyst

            log_text = open(args.log_file, 'r', encoding='utf-8').read()
            analyst = LLMLogAnalyst()
            llm_res = analyst.analyze(log_text)
            llm_summary = f"Causa raiz: {llm_res.causa_raiz}\nConfianca: {llm_res.confianca}\nExplicacao: {llm_res.explicacao}\nSugestao_patch: {llm_res.sugestao_patch}\nTests: {llm_res.comandos_de_teste}"
            print("LLM analysis result:\n", llm_summary)
        except Exception as e:
            print("LLM analysis failed:", e)

    fix_style(unsafe=args.unsafe_fixes)
    results = run_tests_and_autofix_imports()
    print("--- Resultado final ---")
    print(results)

    if args.open_pr and git_has_changes():
        ts = int(time.time())
        branch = f"{args.branch_prefix}/{ts}"
        create_branch_and_push(branch)
        title = "Auto repair: aplicar correções automáticas"
        body = "Este PR foi criado automaticamente pelo `scripts/auto_repair.py` para aplicar correções de formatação e dependências detectadas pelo CI."
        if llm_summary:
            body += "\n\nLLM analysis:\n" + llm_summary

        labels = [l.strip() for l in args.labels.split(",")] if args.labels else None
        assignees = [a.strip() for a in args.assignees.split(",")] if args.assignees else None

        create_pr_via_api(branch, title, body, labels=labels, assignees=assignees, enable_auto_merge=args.auto_merge)
    elif args.open_pr:
        print("Nenhuma mudança detectada — nenhum PR criado.")
