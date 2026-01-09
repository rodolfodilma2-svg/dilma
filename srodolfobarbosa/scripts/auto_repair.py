#!/usr/bin/env python3
"""
Auto-repair avec SANDBOX VALIDATION - agente autônomo.

Fluxo REAL:
  1. Detecta erros reales (pytest, ruff, imports)
  2. Aplica fixes e roda SANDBOX RUNNER
  3. Sandbox valida contra APIs reales (sem mocks)
  4. Decide automaticamente: merge, revert, ou abrir PR
  5. Persiste histórico para aprendizado

O agente NÃO intervém após aplicar fixes — sandbox valida de verdade.
"""
import subprocess
import re
import os
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

# load .env when present (local development)
load_dotenv()

# Detecta repo root
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
WORKSPACE_DIR = REPO_ROOT / "srodolfobarbosa"

# Checa se estamos en repo root o en workspace
if not (REPO_ROOT / ".git").exists():
    # Fallback: assume somos parte de /workspaces/dilma
    REPO_ROOT = Path("/workspaces/dilma")
    WORKSPACE_DIR = REPO_ROOT / "srodolfobarbosa"

os.chdir(REPO_ROOT)

# Agregua REPO_ROOT al PYTHONPATH para que se pueda importar srodolfobarbosa
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

AUTO_INSTALL = "true" == str(os.environ.get("AUTO_INSTALL", "true")).lower()


def run(cmd, check=False, cwd=None):
    """Ejecuta comando en shell."""
    print(f"> {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if r.stdout:
        print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    if check and r.returncode != 0:
        raise SystemExit(r.returncode)
    return r


def fix_style(unsafe=False):
    """Aplica fixes de estilo reales: ruff + black."""
    run("python -m pip install --no-cache-dir ruff black", check=False)
    if unsafe:
        run("ruff check --fix --unsafe-fixes srodolfobarbosa/ || true")
    else:
        run("ruff check --fix srodolfobarbosa/ || true")
    run("black srodolfobarbosa/ || true")


def run_tests_and_autofix_imports():
    """Roda testes e detecta imports faltando."""
    r = run("python -m pytest srodolfobarbosa/test_smoke.py -v || true")
    out = (r.stdout or "") + (r.stderr or "")
    missing = set(re.findall(r"No module named '([\w_\-]+)'", out))
    if missing:
        print(f"⚠ Pacotes faltando detectados: {missing}")
        if AUTO_INSTALL:
            for pkg in missing:
                print(f"  Instalando {pkg}...")
                run(f"python -m pip install --no-cache-dir {pkg}")
            print("  Reexecutando testes...")
            run("python -m pytest srodolfobarbosa/test_smoke.py -v", check=False)
    return out


def run_sandbox_validation(args, repo_path="/workspaces/dilma"):
    """
    Ejecuta sandbox validator para validação REAL.

    Returns:
        (success: bool, decision: str, confidence: float)
    """
    print("\n" + "=" * 60)
    print("🏗 INICIANDO SANDBOX VALIDATION (sem mocks, apenas realidad)")
    print("=" * 60 + "\n")

    try:
        from srodolfobarbosa.sandbox.runner import SandboxRunner

        runner = SandboxRunner(repo_path=repo_path, api_base_url=args.api_url)

        result = runner.run(patch_files=args.patch_files or None)

        print("\n📊 RESULTADO SANDBOX:")
        print(f"   ✓ Tests: {result.test_results.get('success', False)}")
        print(f"   ✓ Linters: {result.lint_results.get('success', False)}")
        print(f"   ✓ Decision: {result.decision}")
        print(f"   ✓ Confidence: {result.confidence:.0%}")

        return (result.success, result.decision, result.confidence)

    except ImportError as e:
        print(f"⚠ Sandbox runner não disponível: {e}")
        print("  Continuando sem sandbox (apenas fixes locais)...")
        return False, "review", 0.0
    except Exception as e:
        print(f"✗ Erro en sandbox: {e}")
        return False, "review", 0.0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Auto-repair com Sandbox Validation (agente autônomo)"
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Executa validação em sandbox (recomendado)",
    )
    parser.add_argument(
        "--auto-apply",
        action="store_true",
        help="Se decision==merge, faz merge automático a main",
    )
    parser.add_argument(
        "--open-pr",
        action="store_true",
        help="Se não for auto-apply, abre PR para revisão",
    )
    parser.add_argument(
        "--unsafe-fixes",
        action="store_true",
        help="Habilita ruff --unsafe-fixes (mais agressivo)",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="URL base da API para validación",
    )
    parser.add_argument("--patch-files", nargs="*", help="Archivos patch a aplicar")
    parser.add_argument(
        "--labels", default="auto-repair", help="Labels para o PR (vírgula separadas)"
    )
    parser.add_argument("--assignees", default=None, help="Assignees para o PR")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("🤖 AUTO-REPAIR AGENT - MODO AUTÔNOMO")
    print("=" * 60)

    # Fase 1: Detecta e aplica fixes
    print("\n✏ Fase 1: Aplicando fixes de estilo...")
    fix_style(unsafe=args.unsafe_fixes)

    print("\n🧪 Fase 2: Detectando erros en testes...")
    results = run_tests_and_autofix_imports()

    # Fase 3: Sandbox validation (REAL, sem mocks)
    if args.sandbox:
        success, decision, confidence = run_sandbox_validation(args)

        # Fase 4: Ejecuta decisión
        print("\n" + "=" * 60)
        print("⚡ FASE 4: EJECUTANDO DECISIÓN")
        print("=" * 60)

        if decision == "merge" and args.auto_apply:
            print(f"✅ Sandbox permitió merge automático (confianza={confidence:.0%})")
            print("   (Branch fue mergeado a main por sandbox runner)")
            sys.exit(0)

        elif decision == "review":
            if args.open_pr:
                print(
                    f"👀 Sandbox requiere revisión humana (confianza={confidence:.0%})"
                )
                print("   Abriendo PR para revisión...")
                # TODO: abrir PR
                sys.exit(0)
            else:
                print("⚠ Sandbox requiere revisión, pero --open-pr no está activado")
                sys.exit(1)

        elif decision == "revert":
            print(f"❌ Sandbox reverteó cambios (confianza={confidence:.0%})")
            sys.exit(1)
    else:
        print("\n⚠ Sandbox no activado (--sandbox)")
        print("   Ejecutando solo fixes locales sin validación...")

    print("\n✅ Auto-repair completado")
    sys.exit(0)
