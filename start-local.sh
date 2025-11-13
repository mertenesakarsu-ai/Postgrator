#!/bin/bash

echo "🚀 Postgrator Local Başlatılıyor..."

# Renk kodları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Hata durumunda çık
set -e

# Proje kök dizinine git
cd "$(dirname "$0")"

# Servislerin çalıştığını kontrol et
echo -e "${YELLOW}📊 Servisleri kontrol ediliyor...${NC}"

# MongoDB kontrolü
if ! pgrep -x "mongod" > /dev/null; then
    echo -e "${RED}❌ MongoDB çalışmıyor!${NC}"
    echo -e "${YELLOW}MongoDB'yi başlatmak için:${NC}"
    echo -e "   ${BLUE}brew services start mongodb-community@7.0${NC}"
    echo -e "${YELLOW}veya:${NC}"
    echo -e "   ${BLUE}mongod --config /opt/homebrew/etc/mongod.conf --fork${NC}"
    exit 1
fi
echo -e "${GREEN}✅ MongoDB çalışıyor${NC}"

# PostgreSQL kontrolü
if ! pg_isready > /dev/null 2>&1; then
    echo -e "${RED}❌ PostgreSQL çalışmıyor!${NC}"
    echo -e "${YELLOW}PostgreSQL'i başlatmak için:${NC}"
    echo -e "   ${BLUE}brew services start postgresql@16${NC}"
    echo -e "${YELLOW}Veritabanı oluşturmak için:${NC}"
    echo -e "   ${BLUE}psql postgres -c \"CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;\"${NC}"
    echo -e "   ${BLUE}psql postgres -c \"CREATE DATABASE target_db OWNER postgres;\"${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL çalışıyor${NC}"

# Veritabanı kontrolü
if ! psql -U postgres -d target_db -h localhost -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  target_db veritabanı bulunamadı, oluşturuluyor...${NC}"
    psql -U postgres -h localhost -c "CREATE DATABASE target_db OWNER postgres;" || true
fi

# .env dosyalarını kontrol et ve gerekirse oluştur
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}⚠️  backend/.env bulunamadı, .env.local'dan kopyalanıyor...${NC}"
    cp backend/.env.local backend/.env
fi

if [ ! -f frontend/.env ]; then
    echo -e "${YELLOW}⚠️  frontend/.env bulunamadı, .env.local'dan kopyalanıyor...${NC}"
    cp frontend/.env.local frontend/.env
fi

# Backend başlat (arka planda)
echo -e "${YELLOW}🔧 Backend başlatılıyor...${NC}"
cd backend

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment bulunamadı, oluşturuluyor...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Backend'i başlat
uvicorn server:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
echo -e "${GREEN}✅ Backend başlatıldı (PID: $BACKEND_PID)${NC}"
cd ..

# Backend'in hazır olmasını bekle
echo -e "${YELLOW}⏳ Backend'in hazır olması bekleniyor...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend hazır!${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${RED}❌ Backend başlatılamadı!${NC}"
        echo -e "${YELLOW}Loglara bakın:${NC}"
        echo -e "   ${BLUE}tail -f backend.log${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
done

# Frontend başlat (arka planda)
echo -e "${YELLOW}🎨 Frontend başlatılıyor...${NC}"
cd frontend

# node_modules kontrolü
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules bulunamadı, bağımlılıklar yükleniyor...${NC}"
    yarn install
fi

# Frontend'i başlat
BROWSER=none yarn start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo -e "${GREEN}✅ Frontend başlatıldı (PID: $FRONTEND_PID)${NC}"
cd ..

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Postgrator başarıyla başlatıldı!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📍 Erişim Adresleri:${NC}"
echo -e "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}📋 Loglar:${NC}"
echo -e "   Backend:  ${BLUE}tail -f backend.log${NC}"
echo -e "   Frontend: ${BLUE}tail -f frontend.log${NC}"
echo ""
echo -e "${YELLOW}🛑 Durdurmak için:${NC}"
echo -e "   ${BLUE}./stop-local.sh${NC}"
echo -e "   veya manuel: ${BLUE}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo ""
echo -e "${YELLOW}💡 İpucu:${NC}"
echo -e "   Demo modunu denemek için frontend'te 'Demo Modu İle Dene' butonuna tıklayın"
echo ""

# Tarayıcıyı aç (isteğe bağlı)
sleep 2
if command -v open > /dev/null; then
    open http://localhost:3000
elif command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
fi
