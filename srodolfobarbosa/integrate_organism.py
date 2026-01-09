#!/usr/bin/env python3
"""
🚀 Integrador Automático - Injeta self-healing direto no deus.py

Este script:
  1. Lê deus.py
  2. Injeta imports do organismo
  3. Ativa organismo no __init__
  4. Cria endpoint para ativar com ordem
  
Resultado: deus.py totalmente integrado rodando na nuvem 24/7
"""

import re
from pathlib import Path
import sys


def inject_organism_integration(deus_file: str) -> bool:
    """Injeta integração do organismo em deus.py."""
    
    file_path = Path(deus_file)
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {deus_file}")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    print(f"📄 Lendo {deus_file} ({len(content)} bytes)...")
    
    # ========== STEP 1: Injetar imports ==========
    print("\n🔧 [1/3] Injetando imports...")
    
    import_section = """# === NEXO SELF-HEALING ORGANISM ===
from nexo_self_healing_organism import SelfHealingOrganism, integrate_with_nexoswarm
# ====================================
"""
    
    # Procura a primeira linha de import
    first_import_idx = content.find("import ")
    if first_import_idx > 0 and import_section not in content:
        # Insere após a primeira linha de comentário ou docstring
        insert_idx = 0
        for line in content[:first_import_idx].split('\n'):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                insert_idx = content.find('\n', first_import_idx + 100) + 1
                break
        
        # Simplemente adiciona no início dos imports
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'import ' in line and not line.strip().startswith('#'):
                lines.insert(i, import_section)
                content = '\n'.join(lines)
                print("  ✅ Imports injetados")
                break
    
    # ========== STEP 2: Injetar inicialização do organismo ==========
    print("\n🔧 [2/3] Injetando inicialização do organismo...")
    
    init_injection = """        
        # === ATIVAÇÃO DO ORGANISMO SELF-HEALING ===
        self._organism = SelfHealingOrganism(self)
        print("🧬 NEXO Organism integrado!")
        # ==========================================
"""
    
    # Procura __init__ da classe NexoSwarm
    init_pattern = r'(class NexoSwarm.*?:\s*def __init__\(self[^)]*\):)'
    
    match = re.search(init_pattern, content)
    if match and init_injection not in content:
        # Encontra a primeira atribuição dentro do __init__
        init_start = match.end()
        
        # Procura a primeira atribuição self.xxx
        next_self = content.find('self.', init_start)
        if next_self > 0:
            # Insere antes da primeira atribuição
            content = content[:next_self] + init_injection + '\n        ' + content[next_self:]
            print("  ✅ Inicialização injetada")
    
    # ========== STEP 3: Injetar método de ativação por ordem ==========
    print("\n🔧 [3/3] Injetando método de ativação automática...")
    
    # Adiciona método para ativar via ordem
    activation_method = '''
    async def _process_activation_command(self, ordem: str) -> dict:
        """
        Processa comando de ativação do organismo.
        
        Ordem: "NEXO ativa o self-healing" ou similar
        """
        if "self-heal" in ordem.lower() or "organismo" in ordem.lower():
            result = await self._organism.activate()
            return {
                "status": "activated",
                "message": "🧬 Organismo NEXO está VIVO! Monitorando e se auto-corrigindo 24/7",
                "details": result
            }
        
        return {"status": "not_activated", "message": "Comando não reconhecido"}
'''
    
    # Procura método pensar() para adicionar após ele
    if 'async def pensar(' in content and activation_method not in content:
        # Encontra o fim do método pensar
        pensar_idx = content.find('async def pensar(')
        if pensar_idx > 0:
            # Procura próximo método async def
            next_method = content.find('\n    async def ', pensar_idx + 1)
            if next_method > 0:
                content = content[:next_method] + activation_method + content[next_method:]
                print("  ✅ Método de ativação injetado")
    
    # ========== Salvar arquivo ==========
    print("\n💾 Salvando arquivo modificado...")
    
    # Criar backup
    backup_path = file_path.with_suffix('.py.pre-organism')
    file_path.rename(backup_path)
    print(f"  ✓ Backup criado: {backup_path}")
    
    # Salvar versão integrada
    file_path.write_text(content, encoding='utf-8')
    print(f"  ✓ Arquivo salvo: {file_path} ({len(content)} bytes)")
    
    # ========== Validar ==========
    print("\n✔️ Validando sintaxe...")
    import subprocess
    result = subprocess.run(
        [sys.executable, '-m', 'py_compile', str(file_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  ✅ Sintaxe válida!")
        return True
    else:
        print(f"  ❌ Erro de sintaxe: {result.stderr}")
        # Restaurar backup
        backup_path.rename(file_path)
        print(f"  Restaurado: {file_path}")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Integra Self-Healing Organism ao deus.py"
    )
    parser.add_argument(
        'deus_file',
        type=str,
        help='Caminho para deus.py'
    )
    
    args = parser.parse_args()
    
    print("🚀 Integrador Automático - Self-Healing Organism")
    print("=" * 60)
    
    success = inject_organism_integration(args.deus_file)
    
    print("\n" + "=" * 60)
    if success:
        print("✨ INTEGRAÇÃO COMPLETA COM SUCESSO!")
        print("\n📝 Próximos passos:")
        print("  1. Fazer push do deus.py para HuggingFace Space")
        print("  2. Na nuvem, enviar ordem: 'NEXO ativa o self-healing'")
        print("  3. Sistema rodará 24/7 monitorando e se auto-corrigindo!")
    else:
        print("❌ Integração falhou")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
