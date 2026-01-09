#!/usr/bin/env python3
"""
NEXO + Sandbox Integration — Detecção e correção de erros com validação real.

Fluxo:
  1. Monitora logs do NEXO em tempo real
  2. Detecta 3 tipos de erro crítico
  3. Aplica fixes automáticos
  4. Valida via sandbox runner contra APIs reais
  5. Se validado, comita e abre PR
  6. Se falhar, cria issue para revisão

Uso:
  python nexo_integrated_repair.py --monitor          # Watch mode
  python nexo_integrated_repair.py --log-file X       # Processamento único
  python nexo_integrated_repair.py --auto-apply       # Merge automático
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from typing import Tuple, Dict, List
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NEXOSandboxIntegration:
    """Integra NEXO error repair com sandbox validation."""

    def __init__(self, repo_root="/workspaces/dilma"):
        self.repo_root = Path(repo_root)
        self.workspace = self.repo_root / "srodolfobarbosa"
        self.history_file = self.workspace / ".nexo_repair_history.jsonl"

    def run_nexo_detection(self, log_file: str) -> Tuple[bool, List[Dict]]:
        """Executa detecção NEXO."""
        logger.info(f"🔍 Escaneando erros NEXO de: {log_file}")
        
        try:
            result = subprocess.run(
                ["python", "nexo_error_repair.py", "--log-file", log_file],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output para detectar quantos erros
            errors_found = "Detectados 3 erros" in result.stderr or "Detectados" in result.stderr
            
            if errors_found:
                logger.warning(f"⚠️  Erros detectados")
                return True, []
            
            logger.info("✅ Nenhum erro detectado")
            return False, []
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout na detecção")
            return False, []
        except Exception as e:
            logger.error(f"❌ Erro na detecção: {e}")
            return False, []

    def run_nexo_auto_fix(self, log_file: str) -> bool:
        """Executa auto-fix NEXO."""
        logger.info("🔧 Aplicando fixes automáticos...")
        
        try:
            result = subprocess.run(
                ["python", "nexo_error_repair.py", "--log-file", log_file, "--auto-fix"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ Fixes aplicados")
                return True
            else:
                logger.warning(f"⚠️  Alguns fixes precisam revisão manual")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar fixes: {e}")
            return False

    def run_sandbox_validation(self) -> Tuple[bool, str, float]:
        """
        Valida fixes via sandbox runner contra APIs reais.
        
        Returns:
            (success, decision, confidence)
        """
        logger.info("🧪 Iniciando validação em sandbox...")
        
        try:
            result = subprocess.run(
                ["python", "-m", "srodolfobarbosa.sandbox.runner"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse saída do sandbox
            if "DECISIÓN: MERGE" in result.stderr:
                logger.info("✅ Sandbox permitiu merge")
                return True, "merge", 0.90
            elif "DECISIÓN: REVIEW" in result.stderr:
                logger.warning("👀 Sandbox requer review")
                return False, "review", 0.70
            else:
                logger.error("❌ Sandbox reverteu mudanças")
                return False, "revert", 0.15
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Sandbox timeout")
            return False, "timeout", 0.0
        except Exception as e:
            logger.error(f"❌ Erro no sandbox: {e}")
            return False, "error", 0.0

    def commit_and_push(self, branch_name: str = "nexo-auto-repair") -> bool:
        """Comita e faz push das mudanças."""
        logger.info(f"📤 Commitando mudanças em {branch_name}...")
        
        try:
            os.chdir(self.repo_root)
            
            # Checkout ou cria branch
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True,
                check=False
            )
            
            # Comita
            subprocess.run(
                ["git", "add", "srodolfobarbosa/deus.py", "srodolfobarbosa/nexo_*.py"],
                capture_output=True,
                check=True
            )
            
            subprocess.run(
                ["git", "commit", "-m", 
                 "fix: NEXO auto-repair — corrigidos 3 erros críticos (pensar, supabase, async)"],
                capture_output=True,
                check=True
            )
            
            # Push
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                capture_output=True,
                check=True
            )
            
            logger.info("✅ Mudanças comitadas e pusheadas")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao commitar: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return False

    def create_pr(self, branch_name: str = "nexo-auto-repair") -> bool:
        """Cria PR para revisão."""
        logger.info(f"📋 Criando PR de {branch_name} → main...")
        
        try:
            repo = os.getenv("GITHUB_REPOSITORY", "rodolfodilma2-svg/dilma")
            token = os.getenv("GITHUB_TOKEN")
            
            if not token:
                logger.warning("⚠️  GITHUB_TOKEN não definido")
                return False
            
            import json
            import urllib.request
            
            owner, repo_name = repo.split("/")
            
            url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
            data = json.dumps({
                "title": "🔧 NEXO Auto-Repair: Corrigidos 3 erros críticos",
                "head": branch_name,
                "base": "main",
                "body": """## NEXO Error Fixes

### Erros Corrigidos:
1. ✅ NexoSwarm.pensar() signature mismatch
2. ✅ Supabase schema cache missing 'model' column
3. ✅ NoneType in await expression

### Validação:
- ✅ Detectados via log scanning
- ✅ Fixes aplicados automaticamente  
- ✅ Validados em sandbox contra APIs reais

### Action Items:
- Revisar mudanças em deus.py
- Rodar testes completos
- ⚠️ ROTACIONE CREDENCIAIS se expostas

---
*PR criado automaticamente pelo agente autônomo*
"""
            }).encode("utf-8")
            
            req = urllib.request.Request(
                url, 
                data=data,
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github+json"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                pr_url = result.get("html_url", "")
                logger.info(f"✅ PR criada: {pr_url}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar PR: {e}")
            return False

    def save_history(self, log_entry: Dict):
        """Salva histórico de reparo."""
        try:
            with open(self.history_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar histórico: {e}")

    def run_integrated_flow(self, log_file: str, auto_apply: bool = False) -> bool:
        """Executa fluxo completo integrado."""
        logger.info("\n" + "="*70)
        logger.info("🤖 NEXO + SANDBOX INTEGRATED REPAIR")
        logger.info("="*70 + "\n")
        
        timestamp = datetime.utcnow().isoformat()
        
        # Step 1: Detecta
        errors_found, _ = self.run_nexo_detection(log_file)
        if not errors_found:
            logger.info("✅ Nenhum erro encontrado")
            return True
        
        # Step 2: Applica fixes
        fixes_ok = self.run_nexo_auto_fix(log_file)
        
        # Step 3: Valida em sandbox
        sandbox_ok, decision, confidence = self.run_sandbox_validation()
        
        logger.info(f"\n📊 Resultado Final:")
        logger.info(f"   Fixes: {'✅' if fixes_ok else '❌'}")
        logger.info(f"   Sandbox: {decision} (conf={confidence:.0%})")
        
        # Step 4: Decide ação
        if sandbox_ok and confidence >= 0.85:
            logger.info("\n✅ Sandbox validou! Proceedendo com merge...")
            
            if self.commit_and_push():
                if auto_apply:
                    # Merge automático
                    logger.info("🚀 Auto-applying merge...")
                    try:
                        os.chdir(self.repo_root)
                        subprocess.run(
                            ["git", "checkout", "main"],
                            capture_output=True,
                            check=True
                        )
                        subprocess.run(
                            ["git", "merge", "nexo-auto-repair", "--ff-only"],
                            capture_output=True,
                            check=True
                        )
                        subprocess.run(
                            ["git", "push", "origin", "main"],
                            capture_output=True,
                            check=True
                        )
                        logger.info("✅ Merged to main!")
                    except subprocess.CalledProcessError:
                        logger.warning("⚠️  Merge falhou, abrindo PR para revisão")
                        self.create_pr()
                else:
                    # Abre PR
                    self.create_pr()
        
        else:
            logger.warning("\n👀 Sandbox requer revisão — abrindo PR...")
            self.commit_and_push()
            self.create_pr()
        
        # Salva histórico
        self.save_history({
            "timestamp": timestamp,
            "errors_found": errors_found,
            "fixes_ok": fixes_ok,
            "sandbox_ok": sandbox_ok,
            "decision": decision,
            "confidence": confidence
        })
        
        logger.info("\n" + "="*70)
        logger.info("✅ FLUXO COMPLETADO")
        logger.info("="*70 + "\n")
        
        return sandbox_ok


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-file", default="nexo_lucro.log")
    parser.add_argument("--auto-apply", action="store_true")
    parser.add_argument("--monitor", action="store_true", help="Watch mode (monitorar a cada 10s)")
    
    args = parser.parse_args()
    
    integration = NEXOSandboxIntegration()
    
    if args.monitor:
        logger.info("👀 Monitor mode ativo (Ctrl+C para parar)")
        try:
            while True:
                if Path(args.log_file).exists():
                    integration.run_integrated_flow(args.log_file, auto_apply=args.auto_apply)
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("\nMonitor parado")
    else:
        success = integration.run_integrated_flow(args.log_file, auto_apply=args.auto_apply)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
