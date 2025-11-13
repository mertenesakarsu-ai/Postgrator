#!/bin/bash

echo "🛑 Postgrator durduruluyor..."

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Proje kök dizinine git
cd "$(dirname "$0")"

# Backend'i durdur
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        echo -e "${GREEN}✅ Backend durduruldu (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend process bulunamadı (PID: $BACKEND_PID)${NC}"
    fi
    rm backend.pid
else
    echo -e "${YELLOW}⚠️  backend.pid dosyası bulunamadı${NC}"
fi

# Frontend'i durdur
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✅ Frontend durduruldu (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend process bulunamadı (PID: $FRONTEND_PID)${NC}"
    fi
    rm frontend.pid
else
    echo -e "${YELLOW}⚠️  frontend.pid dosyası bulunamadı${NC}"
fi

# Alternatif: Port'a göre durdur (pid dosyaları yoksa veya process hala çalışıyorsa)
echo -e "${YELLOW}🔍 Kalan process'leri kontrol ediliyor...${NC}"

if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8000'de hala process çalışıyor, durduruluyor...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Port 8000 temizlendi${NC}"
fi

if lsof -ti:3000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 3000'de hala process çalışıyor, durduruluyor...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Port 3000 temizlendi${NC}"
fi

# Uvicorn ve Node process'lerini temizle
pkill -f "uvicorn server:app" 2>/dev/null && echo -e "${GREEN}✅ Uvicorn process'leri temizlendi${NC}" || true
pkill -f "react-scripts start" 2>/dev/null && echo -e "${GREEN}✅ React scripts process'leri temizlendi${NC}" || true
pkill -f "craco start" 2>/dev/null && echo -e "${GREEN}✅ Craco process'leri temizlendi${NC}" || true

echo ""
echo -e "${GREEN}✅ Tüm servisler durduruldu${NC}"
echo ""
echo -e "${YELLOW}💡 İpucu:${NC}"
echo -e "   Servisleri tekrar başlatmak için: ${GREEN}./start-local.sh${NC}"
echo ""
