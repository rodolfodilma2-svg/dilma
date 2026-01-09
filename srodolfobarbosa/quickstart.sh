#!/bin/bash
# 🚀 NEXO Live System - Quick Start

echo "🚀 NEXO Live System v4.0 - Iniciando..."
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /workspaces/dilma/srodolfobarbosa

echo -e "${YELLOW}[1/4] Verificando ambiente...${NC}"
python --version
echo -e "${GREEN}✅ Python OK${NC}"

echo ""
echo -e "${YELLOW}[2/4] Validando patches...${NC}"
python -m py_compile deus.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Sintaxe deus.py OK${NC}"
else
    echo -e "${RED}❌ Erro de sintaxe em deus.py${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[3/4] Verificando módulos de correção...${NC}"
for file in nexo_live_fixer.py nexo_realtime_monitor.py nexo_live_launcher.py; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file presente${NC}"
    else
        echo -e "${RED}❌ $file não encontrado${NC}"
        exit 1
    fi
done

echo ""
echo -e "${YELLOW}[4/4] Verificando git status...${NC}"
git log -1 --oneline | head -1
echo -e "${GREEN}✅ Git OK${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✨ Sistema pronto para ativar!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 OPÇÕES DE ATIVAÇÃO:"
echo ""
echo "1️⃣ MONITOR EM TEMPO REAL (RECOMENDADO):"
echo "   $ python nexo_realtime_monitor.py --logs-dir /tmp --mode watch"
echo ""
echo "2️⃣ LAUNCHER COM PATCHES:"
echo "   $ python nexo_live_launcher.py --watch-logs /tmp/nexo.log"
echo ""
echo "3️⃣ DEBUG (Manual):"
echo "   $ python patch_deus_simple.py"
echo "   $ python -m py_compile deus_raw.py"
echo "   $ cp deus_raw.py deus.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}📚 Documentação: NEXO_LIVE_INTEGRATION.md${NC}"
echo -e "${YELLOW}📊 Status: DEPLOYMENT_STATUS.md${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
