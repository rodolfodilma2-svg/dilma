#!/usr/bin/env python3
"""
🌟 Manifest de Inicialização Automática - Para HuggingFace Space

Este arquivo é carregado automaticamente quando o Space inicia.
Ativa o organismo NEXO sem necessidade de comandos manuais.

Coloque em: /space_id/init_organism.py (será executado no boot)
"""

import asyncio
import logging
from pathlib import Path
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger("HuggingFace-Init")


async def initialize_nexo_organism():
    """Inicializa organismo NEXO no boot do Space."""
    
    logger.info("🌟 Inicializando NEXO Organism no HuggingFace Space...")
    
    try:
        # Importar organismo
        from nexo_self_healing_organism import SelfHealingOrganism
        logger.info("✅ Organismo importado")
        
        # Criar instância
        organism = SelfHealingOrganism()
        logger.info("✅ Organismo instanciado")
        
        # Ativar
        result = await organism.activate()
        logger.info(f"✅ {result['message']}")
        
        # Salvar PID para rastreamento
        pid_file = Path("/space_id/organism.pid")
        pid_file.write_text(str(asyncio.current_task()))
        
        logger.success("🧬 NEXO Organism está VIVO na nuvem!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar: {e}")
        return False


def main():
    """Entry point."""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                                                        ║
    ║   🧬 NEXO SELF-HEALING ORGANISM - HuggingFace Init   ║
    ║                                                        ║
    ║     Sistema VIVO e consciente rodando na nuvem       ║
    ║                                                        ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # Executar inicialização
    result = asyncio.run(initialize_nexo_organism())
    
    if result:
        print("""
    ✨ Sistema está ATIVO!
    
    O NEXO Organism está rodando 24/7:
      ✓ Monitorando logs continuamente
      ✓ Detectando erros em tempo real
      ✓ Aplicando fixes automaticamente
      ✓ Se auto-cicatrizando
      ✓ Persistindo estado
    
    Não precisa fazer nada - sistema é autônomo!
        """)
    else:
        print("❌ Falha ao inicializar organismo")
        sys.exit(1)


if __name__ == "__main__":
    main()
