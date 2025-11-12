#!/bin/bash

echo "🚀 Postgrator Localhost Kurulumu Başlatılıyor..."
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Docker kontrolü
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker bulunamadı. Lütfen Docker'ı yükleyin.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose bulunamadı. Lütfen Docker Compose'u yükleyin.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker ve Docker Compose bulundu${NC}"
echo ""

# Port kontrolü
echo "🔍 Port kullanımı kontrol ediliyor..."
ports=(3000 8000 27017 5432 1433)
port_in_use=false

for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an | grep -q ":$port.*LISTEN" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Port $port kullanımda${NC}"
        port_in_use=true
    fi
done

if [ "$port_in_use" = true ]; then
    echo ""
    read -p "Devam etmek istiyor musunuz? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🐳 Docker container'ları başlatılıyor..."
echo ""

# Hangi modu kullanacağını sor
echo "Hangi modu başlatmak istersiniz?"
echo "1) Tam Stack (MSSQL + PostgreSQL + MongoDB + Backend + Frontend)"
echo "2) Demo Modu (Sadece gerekli servisler - hafif)"
echo ""
read -p "Seçiminiz (1 veya 2): " mode

if [ "$mode" = "2" ]; then
    echo ""
    echo -e "${YELLOW}📦 Demo modu başlatılıyor...${NC}"
    docker-compose -f docker-compose.demo.yml up -d
else
    echo ""
    echo -e "${YELLOW}📦 Tam stack başlatılıyor...${NC}"
    docker-compose up -d
fi

echo ""
echo "⏳ Container'ların hazır olması bekleniyor..."
sleep 5

# Container durumunu kontrol et
echo ""
echo "📊 Container Durumu:"
docker-compose ps

echo ""
echo -e "${GREEN}✨ Kurulum tamamlandı!${NC}"
echo ""
echo "🌐 Uygulamaya erişim:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📝 Yararlı komutlar:"
echo "   Logları izle:        docker-compose logs -f"
echo "   Backend logları:     docker-compose logs -f backend"
echo "   Frontend logları:    docker-compose logs -f frontend"
echo "   Durdur:              docker-compose down"
echo "   Yeniden başlat:      docker-compose restart"
echo ""
echo "💡 İlk kullanım için 'Demo Modu İle Dene' butonuna tıklayın!"
echo ""
