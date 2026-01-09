# Contribuindo

Para manter a qualidade do código, seguimos estas convenções:

- Formatação: `black`
- Lint: `ruff`
- Ordenação de imports: `isort`

Instalação (local):

1. `python -m pip install --upgrade pip`
2. `python -m pip install pre-commit`
3. `pre-commit install`

Também pode rodar manualmente antes de commitar:

`pre-commit run --all-files`

CI: O workflow `.github/workflows/ci.yml` executa os mesmos checks automaticamente em pushes/PRs.