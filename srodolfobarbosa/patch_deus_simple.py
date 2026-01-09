#!/usr/bin/env python3
"""Patch simples e direto para deus.py"""

import re
from pathlib import Path

file_path = Path("deus_raw.py")
content = file_path.read_text(encoding='utf-8')
print(f"Arquivo original: {len(content)} bytes")

# Fix 1: Aumentar MAX_PROMPT_SIZE
print("\n🔧 Fix 1: Aumentar MAX_PROMPT_SIZE...")
old = "        MAX_PROMPT_SIZE = 8000"
new = "        MAX_PROMPT_SIZE = 12000"
if old in content:
    content = content.replace(old, new, 1)  # Apenas primeira ocorrência
    print("  ✅ MAX_PROMPT_SIZE: 8000 → 12000")

# Fix 2: Corrigir extração de content
print("\n🔧 Fix 2: Corrigir extração de content...")

# Procura o bloco IF problemático (linhas 1087-1094)
old_block = """            elif hasattr(res, 'content'):
                json_str = str(res.content) if res.content else "{}"
            else:
                json_str = str(res)"""

new_block = """            elif hasattr(res, 'content'):
                json_str = str(res.content) if res.content else "{}"
            elif hasattr(res, 'text'):
                json_str = str(res.text)
            elif hasattr(res, 'output'):
                json_str = str(res.output)
            else:
                json_str = str(res)"""

if old_block in content:
    content = content.replace(old_block, new_block, 1)
    print("  ✅ Adicionados fallbacks para .text e .output")

# Fix 3: Simplificar prompt se muito grande
print("\n🔧 Fix 3: Adicionar resumo agressivo...")

# Encontra a seção onde monta o prompt
marker = "            lista_tools = str(self.ferramentas_carregadas)"
if marker in content:
    poda = """            lista_tools = str(self.ferramentas_carregadas)
        
            # PODA AGRESSIVA: Se contexto muito grande, resumir
            if len(str(lista_agentes) + str(lista_tools)) > 4000:
                agentes_resumo = dict(list(self.agentes_ativos.items())[:3])
                lista_agentes = json.dumps(agentes_resumo, indent=2)
                lista_tools = f"[{len(self.ferramentas_carregadas)} ferramentas disponíveis]"
"""
    content = content.replace(marker, poda, 1)
    print("  ✅ Poda agressiva adicionada")

# Salvar
file_path.write_text(content, encoding='utf-8')
print(f"\n✅ Patches aplicados!")
print(f"Arquivo novo: {len(content)} bytes")

# Validar sintaxe
import subprocess
result = subprocess.run(['python', '-m', 'py_compile', str(file_path)], capture_output=True)
if result.returncode == 0:
    print("✅ Sintaxe Python válida!")
else:
    print(f"❌ Erro de sintaxe: {result.stderr.decode()}")
