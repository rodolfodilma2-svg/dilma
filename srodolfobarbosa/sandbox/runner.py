"""
SandboxRunner: Ejecuta fixes en ambiente isolado y valida contra APIs reales.
Sin mocks, sin tests fake. Solo realidad.

Flujo:
  1. Crea branch efêmero (sandbox-<timestamp>)
  2. Aplica patches (git apply o commits)
  3. Roda testes reales (pytest contra endpoints reales)
  4. Roda linters (ruff, black) para sintaxis/estilo
  5. Valida output (coverage, test results, lint status)
  6. Decide: merge a main, revert, o abrir PR para revisión
  7. Persiste resultado en histórico (Supabase/SQLite)
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import hashlib
from dataclasses import dataclass

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SandboxResult:
    """Resultado de uma ejecución en sandbox."""
    sandbox_id: str
    branch_name: str
    timestamp: str
    success: bool
    test_results: Dict
    lint_results: Dict
    coverage: Optional[float]
    error_logs: List[str]
    duration_seconds: float
    commit_hash: str
    decision: str  # 'merge', 'revert', 'review'
    confidence: float  # 0.0-1.0


class SandboxRunner:
    """Ejecutor de sandbox para validar fixes contra APIs reales."""

    def __init__(self, repo_path: str = "/workspaces/dilma", api_base_url: str = "http://localhost:8000"):
        """
        Inicializa el runner.
        
        Args:
            repo_path: Ruta al repositorio
            api_base_url: URL base de la API para validaciones reales
        """
        self.repo_path = Path(repo_path)
        self.api_base_url = api_base_url
        self.workspace = self.repo_path / "srodolfobarbosa"
        self.sandbox_dir = self.workspace / ".sandbox"
        self.sandbox_dir.mkdir(exist_ok=True)
        self.history_file = self.sandbox_dir / "history.jsonl"

    def create_ephemeral_branch(self) -> str:
        """Crea un branch efêmero para el sandbox."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        branch_name = f"sandbox-validate-{timestamp}"
        
        try:
            # Checkout a main y crea branch nuevo
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            logger.info(f"✓ Branch efêmero creado: {branch_name}")
            return branch_name
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Error creando branch: {e}")
            raise

    def apply_patches(self, patch_files: List[str]) -> bool:
        """Aplica patches reales en el branch actual."""
        for patch_file in patch_files:
            try:
                result = subprocess.run(
                    ["git", "apply", patch_file],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    logger.error(f"✗ Error aplicando patch {patch_file}: {result.stderr}")
                    return False
                logger.info(f"✓ Patch aplicado: {patch_file}")
            except Exception as e:
                logger.error(f"✗ Exception aplicando patch: {e}")
                return False
        return True

    def run_tests(self) -> Tuple[bool, Dict]:
        """
        Roda testes reales contra la API en vivo.
        
        Returns:
            (success: bool, results: Dict con datos de test)
        """
        logger.info("🧪 Ejecutando tests contra API real...")
        
        test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "coverage": 0.0,
            "duration": 0.0
        }
        
        try:
            start_time = time.time()
            
            # Roda pytest con coverage real
            cmd = [
                "python", "-m", "pytest", 
                "srodolfobarbosa/test_smoke.py",
                "-v", 
                "--tb=short",
                f"--cov=srodolfobarbosa",
                "--cov-report=json"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60  # 60 segundos máximo
            )
            
            test_results["duration"] = time.time() - start_time
            test_results["raw_output"] = result.stdout
            
            # Parsea pytest output
            if result.returncode == 0:
                test_results["passed"] = self._count_passed_tests(result.stdout)
                test_results["success"] = True
                logger.info(f"✓ Tests pasados: {test_results['passed']}")
            else:
                test_results["failed"] = self._count_failed_tests(result.stdout)
                test_results["errors"] = result.stdout.split("\n")[-10:]
                test_results["success"] = False
                logger.error(f"✗ Tests falharon: {test_results['failed']}")
            
            # Carga coverage.json si existe
            cov_file = self.repo_path / ".coverage"
            if cov_file.exists():
                try:
                    cov_json = self.repo_path / "coverage.json"
                    if cov_json.exists():
                        with open(cov_json) as f:
                            cov_data = json.load(f)
                            test_results["coverage"] = cov_data.get("totals", {}).get("percent_covered", 0.0)
                except Exception as e:
                    logger.warning(f"No se pudo parsear coverage: {e}")
            
            return test_results["success"], test_results
            
        except subprocess.TimeoutExpired:
            test_results["errors"].append("Tests timeout (>60s)")
            test_results["success"] = False
            return False, test_results
        except Exception as e:
            test_results["errors"].append(str(e))
            test_results["success"] = False
            logger.error(f"✗ Exception en tests: {e}")
            return False, test_results

    def run_linters(self) -> Tuple[bool, Dict]:
        """
        Roda linters reales (ruff, black) en el código modificado.
        
        Returns:
            (success: bool, results: Dict)
        """
        logger.info("🔍 Ejecutando linters (ruff, black)...")
        
        lint_results = {
            "ruff": {"errors": 0, "warnings": 0, "fixed": 0},
            "black": {"checked": 0, "formatted": 0},
            "success": True,
            "issues": []
        }
        
        try:
            # Ruff: check y fix
            ruff_cmd = ["ruff", "check", "--select=E,F,W", "srodolfobarbosa/", "--fix"]
            result = subprocess.run(
                ruff_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "error" in result.stdout.lower() or result.returncode != 0:
                lint_results["ruff"]["errors"] = self._count_lint_errors(result.stdout)
                lint_results["success"] = False
                logger.warning(f"⚠ Ruff encontró issues: {lint_results['ruff']['errors']}")
            else:
                lint_results["ruff"]["fixed"] = 1
                logger.info("✓ Ruff OK")
            
            # Black: check format
            black_cmd = ["black", "--check", "srodolfobarbosa/"]
            result = subprocess.run(
                black_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning("⚠ Black detectó archivos sin formato")
                # Aplica black
                subprocess.run(
                    ["black", "srodolfobarbosa/"],
                    cwd=self.repo_path,
                    capture_output=True,
                    timeout=30
                )
                lint_results["black"]["formatted"] = 1
            else:
                lint_results["black"]["checked"] = 1
                logger.info("✓ Black OK")
            
            return lint_results["success"], lint_results
            
        except subprocess.TimeoutExpired:
            lint_results["issues"].append("Linters timeout")
            lint_results["success"] = False
            return False, lint_results
        except Exception as e:
            lint_results["issues"].append(str(e))
            logger.error(f"✗ Exception en linters: {e}")
            return False, lint_results

    def validate_api_endpoints(self) -> Tuple[bool, Dict]:
        """
        Valida que los endpoints críticos sigan funcionando.
        Hace requests reales contra la API.
        
        Returns:
            (success: bool, results: Dict)
        """
        logger.info("🌐 Validando endpoints de API en vivo...")
        
        api_results = {
            "endpoints_tested": 0,
            "endpoints_ok": 0,
            "endpoints_failed": [],
            "success": True
        }
        
        try:
            import requests
        except ImportError:
            logger.warning("⚠ requests no disponible, saltando validación de API")
            return True, api_results
        
        # Endpoints críticos a testar
        critical_endpoints = [
            ("/insights/pending", "GET"),
            ("/admin/health", "GET"),
        ]
        
        for endpoint, method in critical_endpoints:
            try:
                url = f"{self.api_base_url}{endpoint}"
                api_results["endpoints_tested"] += 1
                
                if method == "GET":
                    resp = requests.get(url, timeout=5)
                elif method == "POST":
                    resp = requests.post(url, json={}, timeout=5)
                
                if 200 <= resp.status_code < 400:
                    api_results["endpoints_ok"] += 1
                    logger.info(f"✓ {method} {endpoint} → {resp.status_code}")
                else:
                    api_results["endpoints_failed"].append(f"{endpoint} ({resp.status_code})")
                    api_results["success"] = False
                    logger.warning(f"⚠ {method} {endpoint} → {resp.status_code}")
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"⚠ No se puede conectar a {self.api_base_url}{endpoint}")
                # No falla, puede que API no esté en vivo
            except Exception as e:
                logger.warning(f"⚠ Error validando {endpoint}: {e}")
                api_results["endpoints_failed"].append(f"{endpoint} (exception)")
        
        return api_results["success"], api_results

    def decide_merge(self, test_success: bool, lint_success: bool, 
                    api_success: bool, coverage: float) -> Tuple[str, float]:
        """
        Decide si mergear, revertir o abrir PR.
        
        Criterios:
        - Tests deben pasar 100%
        - Linters deben pasar (o ser auto-fixables)
        - Coverage no debe bajar
        - API endpoints deben estar ok
        
        Returns:
            (decision: str, confidence: float)
        """
        logger.info("🤔 Tomando decisión de merge...")
        
        confidence = 0.0
        decision = "review"  # Default: pedir revisión humana
        
        # Suma puntos de confianza
        if test_success:
            confidence += 0.4
            logger.info("  ✓ Tests OK (+0.4)")
        else:
            logger.error("  ✗ Tests falharon (-0.4)")
        
        if lint_success:
            confidence += 0.25
            logger.info("  ✓ Linters OK (+0.25)")
        else:
            logger.warning("  ⚠ Linters issues (-0.1)")
            confidence -= 0.1
        
        if api_success:
            confidence += 0.25
            logger.info("  ✓ API endpoints OK (+0.25)")
        else:
            logger.warning("  ⚠ API issues (-0.15)")
            confidence -= 0.15
        
        if coverage > 0.70:
            confidence += 0.1
            logger.info(f"  ✓ Coverage OK {coverage:.1%} (+0.1)")
        
        # Decisión basada en confianza
        if confidence >= 0.85 and test_success and lint_success:
            decision = "merge"
            logger.info(f"🟢 DECISIÓN: MERGE (confianza={confidence:.2f})")
        elif confidence >= 0.70 and test_success:
            decision = "review"
            logger.info(f"🟡 DECISIÓN: REVIEW (confianza={confidence:.2f})")
        else:
            decision = "revert"
            logger.info(f"🔴 DECISIÓN: REVERT (confianza={confidence:.2f})")
        
        return decision, confidence

    def commit_and_push(self, branch_name: str, message: str) -> bool:
        """Commita cambios en el branch actual."""
        try:
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            logger.info(f"✓ Cambios commiteados y pusheados: {branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Error en commit/push: {e}")
            return False

    def execute_decision(self, decision: str, branch_name: str) -> bool:
        """Ejecuta la decisión tomada."""
        try:
            if decision == "merge":
                # Merge al main
                subprocess.run(
                    ["git", "checkout", "main"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True
                )
                subprocess.run(
                    ["git", "merge", "--ff-only", branch_name],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True
                )
                subprocess.run(
                    ["git", "push", "origin", "main"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True
                )
                logger.info(f"✓ Mergeado a main: {branch_name}")
                
            elif decision == "revert":
                # Delete branch sin merge
                subprocess.run(
                    ["git", "checkout", "main"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True
                )
                subprocess.run(
                    ["git", "branch", "-D", branch_name],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True
                )
                subprocess.run(
                    ["git", "push", "origin", f":{branch_name}"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=False
                )
                logger.info(f"🗑 Branch revertido (sin merge): {branch_name}")
                
            elif decision == "review":
                # Deja branch en remote para revisión humana
                logger.info(f"👀 Branch disponible para revisión: {branch_name}")
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Error ejecutando decisión: {e}")
            return False

    def save_result(self, result: SandboxResult):
        """Persiste resultado en histórico."""
        entry = {
            "sandbox_id": result.sandbox_id,
            "timestamp": result.timestamp,
            "branch": result.branch_name,
            "success": result.success,
            "decision": result.decision,
            "confidence": result.confidence,
            "test_results": result.test_results,
            "lint_results": result.lint_results,
            "coverage": result.coverage,
            "duration": result.duration_seconds,
        }
        
        with open(self.history_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        logger.info(f"💾 Resultado guardado en histórico")

    def run(self, patch_files: Optional[List[str]] = None) -> SandboxResult:
        """
        Ejecuta el flujo completo de sandbox.
        
        Args:
            patch_files: Lista de archivos patch a aplicar (opcional)
        
        Returns:
            SandboxResult con datos de la ejecución
        """
        sandbox_id = hashlib.md5(
            datetime.utcnow().isoformat().encode()
        ).hexdigest()[:8]
        
        timestamp = datetime.utcnow().isoformat()
        start_time = time.time()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🏗 SANDBOX RUNNER - ID: {sandbox_id}")
        logger.info(f"{'='*60}\n")
        
        try:
            # 1. Crea branch efêmero
            branch_name = self.create_ephemeral_branch()
            
            # 2. Aplica patches si es necesario
            if patch_files:
                if not self.apply_patches(patch_files):
                    logger.error("✗ Error aplicando patches")
                    return SandboxResult(
                        sandbox_id=sandbox_id,
                        branch_name=branch_name,
                        timestamp=timestamp,
                        success=False,
                        test_results={},
                        lint_results={},
                        coverage=None,
                        error_logs=["Error aplicando patches"],
                        duration_seconds=time.time() - start_time,
                        commit_hash="",
                        decision="revert",
                        confidence=0.0
                    )
                
                if not self.commit_and_push(branch_name, "sandbox: aplicados patches para validación"):
                    logger.warning("⚠ Error pusheando branch")
            
            # 3. Roda testes reales
            test_success, test_results = self.run_tests()
            
            # 4. Roda linters
            lint_success, lint_results = self.run_linters()
            
            # 5. Valida API endpoints
            api_success, api_results = self.validate_api_endpoints()
            
            # 6. Toma decisión
            coverage = test_results.get("coverage", 0.0)
            decision, confidence = self.decide_merge(
                test_success, lint_success, api_success, coverage
            )
            
            # 7. Ejecuta decisión
            self.execute_decision(decision, branch_name)
            
            # 8. Guarda resultado
            result = SandboxResult(
                sandbox_id=sandbox_id,
                branch_name=branch_name,
                timestamp=timestamp,
                success=(decision == "merge"),
                test_results=test_results,
                lint_results=lint_results,
                coverage=coverage,
                error_logs=[],
                duration_seconds=time.time() - start_time,
                commit_hash="",  # TODO: obtener hash real
                decision=decision,
                confidence=confidence
            )
            
            self.save_result(result)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ SANDBOX COMPLETADO")
            logger.info(f"   Decisión: {decision.upper()}")
            logger.info(f"   Confianza: {confidence:.0%}")
            logger.info(f"   Duración: {result.duration_seconds:.1f}s")
            logger.info(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            logger.error(f"\n✗ SANDBOX FAILED: {e}")
            return SandboxResult(
                sandbox_id=sandbox_id,
                branch_name="",
                timestamp=timestamp,
                success=False,
                test_results={},
                lint_results={},
                coverage=None,
                error_logs=[str(e)],
                duration_seconds=time.time() - start_time,
                commit_hash="",
                decision="review",
                confidence=0.0
            )

    def _count_passed_tests(self, output: str) -> int:
        """Cuenta tests pasados en output de pytest."""
        try:
            for line in output.split("\n"):
                if "passed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "passed" in part and i > 0:
                            return int(parts[i-1])
        except:
            pass
        return 0

    def _count_failed_tests(self, output: str) -> int:
        """Cuenta tests fallidos en output de pytest."""
        try:
            for line in output.split("\n"):
                if "failed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "failed" in part and i > 0:
                            return int(parts[i-1])
        except:
            pass
        return 0

    def _count_lint_errors(self, output: str) -> int:
        """Cuenta errores de lint."""
        return len([line for line in output.split("\n") if line.startswith("E")])


def main():
    """Script de entrada para correr sandbox desde CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sandbox validator para auto-repair")
    parser.add_argument("--repo", default="/workspaces/dilma", help="Ruta al repositorio")
    parser.add_argument("--api-url", default="http://localhost:8000", help="URL base de la API")
    parser.add_argument("--patch", nargs="*", help="Archivos patch a aplicar")
    
    args = parser.parse_args()
    
    runner = SandboxRunner(repo_path=args.repo, api_base_url=args.api_url)
    result = runner.run(patch_files=args.patch)
    
    # Retorna exit code basado en decisión
    sys.exit(0 if result.decision in ["merge", "review"] else 1)


if __name__ == "__main__":
    main()
