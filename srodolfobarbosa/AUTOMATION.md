# CI & Auto-repair 🔧

Este repositório inclui um workflow GitHub Actions (`.github/workflows/ci.yml`) que instala dependências, executa testes (`pytest`) e roda linter/formatter (`ruff`, `black`).

Também há um script utilitário `scripts/auto_repair.py` que aplica correções básicas de estilo e tenta detectar erros de importação simples para sugerir/instalar dependências quando `AUTO_INSTALL=true`.

Use com cautela: o script pode instalar pacotes automaticamente se a variável `AUTO_INSTALL` estiver habilitada.