# CI & Auto-repair 🔧

Este repositório inclui um workflow GitHub Actions (`.github/workflows/ci.yml`) que instala dependências, executa testes (`pytest`) e roda linter/formatter (`ruff`, `black`).

Também há um script utilitário `scripts/auto_repair.py` que aplica correções básicas de estilo e tenta detectar erros de importação simples para sugerir/instalar dependências quando `AUTO_INSTALL=true`.

Use com cautela: o script pode instalar pacotes automaticamente se a variável `AUTO_INSTALL` estiver habilitada.

## PR automático e workflow de reparo

- Existe um workflow (`.github/workflows/auto_repair.yml`) que é acionado quando o workflow `CI` termina com falha. Ele executa `scripts/auto_repair.py --open-pr` com `AUTO_INSTALL=true` e tentará abrir um PR com as correções automáticas.
- Para que o script consiga criar PRs via API ele usa o `GITHUB_TOKEN` disponível no runner (`secrets.GITHUB_TOKEN`). Se precisar executar localmente e abrir PRs, exponha `GITHUB_TOKEN` (com permissões adequadas) ou use o `gh` CLI autenticado.
- O script também aceita `--open-pr` para abrir PRs localmente (ou no CI) e tem os parâmetros `--branch-prefix` e `--commit-message` para customizar o branch e a mensagem do commit.

## Proteção de branch e revisões (observações)

- Tentei aplicar regras de proteção na branch `main` (exigir revisões e code owner reviews) via API, mas recebi um erro de permissão (403). Isso requer permissões administrativas no repositório. Se quiser que eu aplique as regras via API, forneça um token com escopo adequado ou aplique manualmente: *Settings → Branches → Add rule* e marque **Require pull request reviews** e **Require review from Code Owners**.
- Como mitigação parcial, adicionei um `CODEOWNERS` em `.github/CODEOWNERS` para solicitar automaticamente revisão de maintainers em mudanças no diretório `srodolfobarbosa/`.

## Auto-merge e rotulagem

- O fluxo `Auto Repair` agora adiciona label(s) configuráveis (`AUTO_REPAIR_LABELS`, padrão `auto-repair`) e pode atribuir reviewers (`AUTO_REPAIR_ASSIGNEES`).
- Há um workflow `Auto-merge Auto-Repair PRs` que faz merge automático (`squash`) quando a label `auto-repair` é aplicada e todos os checks requeridos passam. Isso dá controle seletivo (apenas PRs rotulados serão mesclados automaticamente).