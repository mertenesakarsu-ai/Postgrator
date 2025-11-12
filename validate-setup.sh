#!/bin/bash

# Renk kodları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔍 Postgrator Kurulum Doğrulama"
echo "================================"
echo ""

# Test sonuçları
tests_passed=0
tests_failed=0

# Test fonksiyonu
run_test() {
    test_name=$1
    test_command=$2
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((tests_passed++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((tests_failed++))
        return 1
    fi
}

# 1. Docker kontrolü
echo -e "${BLUE}📦 Docker Kontrolleri${NC}"
run_test "Docker yüklü mü" "command -v docker"
run_test "Docker Compose yüklü mü" "command -v docker-compose"
run_test "Docker daemon çalışıyor mu" "docker info"
echo ""

# 2. Container kontrolü
echo -e "${BLUE}🐳 Container Durumları${NC}"
run_test "MongoDB container çalışıyor mu" "docker ps --filter name=postgrator_mongodb --filter status=running --format '{{.Names}}' | grep -q mongodb"
run_test "Backend container çalışıyor mu" "docker ps --filter name=postgrator_backend --filter status=running --format '{{.Names}}' | grep -q backend"
run_test "Frontend container çalışıyor mu" "docker ps --filter name=postgrator_frontend --filter status=running --format '{{.Names}}' | grep -q frontend"
echo ""

# 3. Port kontrolü
echo -e "${BLUE}🔌 Port Kontrolleri${NC}"
run_test "Port 3000 dinleniyor mu" "docker exec postgrator_frontend sh -c 'netstat -tln 2>/dev/null | grep -q :3000 || ss -tln 2>/dev/null | grep -q :3000'"
run_test "Port 8000 dinleniyor mu" "docker exec postgrator_backend sh -c 'netstat -tln 2>/dev/null | grep -q :8000 || ss -tln 2>/dev/null | grep -q :8000'"
run_test "Port 27017 dinleniyor mu" "docker exec postgrator_mongodb sh -c 'netstat -tln 2>/dev/null | grep -q :27017 || ss -tln 2>/dev/null | grep -q :27017'"
echo ""

# 4. Health check'ler
echo -e "${BLUE}❤️  Health Check'ler${NC}"
run_test "Backend API yanıt veriyor mu" "curl -s http://localhost:8000/api | grep -q 'message'"
run_test "Frontend çalışıyor mu" "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 | grep -q '^[23]'"
run_test "MongoDB bağlantısı OK mu" "docker exec postgrator_mongodb mongosh --eval 'db.runCommand({ping:1})' --quiet | grep -q 'ok.*1'"
echo ""

# 5. Environment değişkenleri
echo -e "${BLUE}🔧 Environment Kontrolleri${NC}"
run_test "Backend .env dosyası var mı" "[ -f /app/backend/.env ]"
run_test "Frontend .env dosyası var mı" "[ -f /app/frontend/.env ]"

if [ -f /app/frontend/.env ]; then
    backend_url=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d'=' -f2)
    if [[ "$backend_url" == *"8000"* ]]; then
        echo -e "Testing: Backend URL port 8000 kullanıyor mu... ${GREEN}✓ PASSED${NC}"
        ((tests_passed++))
    else
        echo -e "Testing: Backend URL port 8000 kullanıyor mu... ${RED}✗ FAILED${NC} (Bulunan: $backend_url)"
        ((tests_failed++))
    fi
fi
echo ""

# 6. Volume kontrolü
echo -e "${BLUE}💾 Volume Kontrolleri${NC}"
run_test "MongoDB data volume var mı" "docker volume ls | grep -q mongodb_data"
run_test "Backend uploads volume var mı" "docker volume ls | grep -q backend_uploads"
echo ""

# 7. Network kontrolü
echo -e "${BLUE}🌐 Network Kontrolleri${NC}"
run_test "Docker network var mı" "docker network ls | grep -q postgrator_network"
run_test "Backend MongoDB'ye erişebiliyor mu" "docker exec postgrator_backend sh -c 'curl -s mongodb:27017 || nc -zv mongodb 27017' 2>&1 | grep -qE 'succeeded|open'"
echo ""

# Sonuç
echo "================================"
echo -e "${BLUE}📊 Test Sonuçları${NC}"
echo "================================"
echo -e "Başarılı: ${GREEN}$tests_passed${NC}"
echo -e "Başarısız: ${RED}$tests_failed${NC}"
echo ""

if [ $tests_failed -eq 0 ]; then
    echo -e "${GREEN}🎉 Tüm testler başarılı! Kurulum tamam.${NC}"
    echo ""
    echo "🌐 Uygulamaya erişim:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    exit 0
else
    echo -e "${YELLOW}⚠️  Bazı testler başarısız oldu.${NC}"
    echo ""
    echo "🔍 Sorun giderme önerileri:"
    echo "   1. Container'ların durumunu kontrol edin: docker-compose ps"
    echo "   2. Logları kontrol edin: docker-compose logs"
    echo "   3. Yeniden başlatın: docker-compose restart"
    echo "   4. Temiz kurulum: docker-compose down -v && docker-compose up -d"
    exit 1
fi
