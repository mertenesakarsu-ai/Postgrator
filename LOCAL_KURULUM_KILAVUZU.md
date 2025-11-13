# 🚀 Projeyi Docker Olmadan Local Çalıştırma Kılavuzu

## 📋 Gereksinimler

Projeyi local olarak çalıştırmak için aşağıdaki yazılımların sisteminizde kurulu olması gerekir:

### Zorunlu:
- ✅ **Python 3.10+**: Backend için
- ✅ **Node.js 18+** ve **Yarn**: Frontend için
- ✅ **MongoDB**: Job tracking ve metadata için
- ✅ **PostgreSQL**: Migration hedef veritabanı

### Opsiyonel:
- 🔵 **Microsoft SQL Server**: Sadece gerçek .bak dosyası migration'ı için (Demo modu için gerekli değil)

---

## 📦 1. Adım: Gerekli Yazılımları Kurun

### macOS için:

#### Python (Homebrew ile)
```bash
brew install python@3.11
python3 --version
```

#### Node.js ve Yarn
```bash
# Node.js kurulumu
brew install node
node --version

# Yarn kurulumu
npm install -g yarn
yarn --version
```

#### MongoDB
```bash
# MongoDB Community Edition kurulumu
brew tap mongodb/brew
brew install mongodb-community@7.0

# MongoDB'yi başlat
brew services start mongodb-community@7.0

# Durum kontrolü
brew services list | grep mongodb
```

#### PostgreSQL
```bash
# PostgreSQL 16 kurulumu
brew install postgresql@16

# PATH'e ekle
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# PostgreSQL'i başlat
brew services start postgresql@16

# Veritabanı oluştur
psql postgres << EOF
CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;
CREATE DATABASE target_db OWNER postgres;
\\q
EOF
```

**🔗 Detaylı PostgreSQL kurulum kılavuzu için:** [MACOS_POSTGRESQL_KURULUM.md](./MACOS_POSTGRESQL_KURULUM.md)

---

## ⚙️ 2. Adım: Environment Dosyalarını Yapılandırın

### Backend (.env)

Dosya konumu: `/app/backend/.env`

```bash
# MongoDB Configuration (Local)
MONGO_URL="mongodb://localhost:27017"
DB_NAME="postgrator_db"

# CORS Configuration
CORS_ORIGINS="*"

# MSSQL Configuration (Opsiyonel - sadece gerçek migration için)
MSSQL_HOST="localhost"
MSSQL_PORT="1433"
MSSQL_SA_PWD="YourStrong!Passw0rd"
TEMP_DB="TempFromBak"

# PostgreSQL Configuration (Target database)
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
POSTGRES_DB="target_db"
```

### Frontend (.env)

Dosya konumu: `/app/frontend/.env`

```bash
# Backend API URL (Local)
REACT_APP_BACKEND_URL=http://localhost:8000

# WebSocket Port
WDS_SOCKET_PORT=3000

# Feature Flags
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false

# Hot Reload Configuration
WATCHPACK_POLLING=false
CHOKIDAR_USEPOLLING=false
```

---

## 🔧 3. Adım: Backend Kurulumu

```bash
# Backend dizinine gidin
cd /app/backend

# Python sanal ortamı oluşturun (önerilen)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# veya Windows için: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install --upgrade pip
pip install -r requirements.txt

# Bağımlılıkların yüklendiğini doğrulayın
pip list | grep -E "fastapi|motor|psycopg"
```

### Backend'i Başlatma

```bash
# Backend dizininde (/app/backend)
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**✅ Başarılı başlatma çıktısı:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test:**
```bash
curl http://localhost:8000/health
# Beklenen: {"status":"healthy"}
```

---

## 🎨 4. Adım: Frontend Kurulumu

```bash
# Frontend dizinine gidin
cd /app/frontend

# Bağımlılıkları yükleyin
yarn install

# Alternatif olarak cache temizleyerek:
# yarn cache clean
# yarn install
```

### Frontend'i Başlatma

```bash
# Frontend dizininde (/app/frontend)
yarn start
```

**✅ Başarılı başlatma:**
- Tarayıcınız otomatik olarak açılacak: http://localhost:3000
- Hot reload aktif olacak (kod değişikliklerini anında yansıtır)

---

## 🚀 5. Adım: Projeyi Çalıştırma

### Hızlı Başlatma Script'i

Dosya konumu: `/app/start-local.sh`

```bash
#!/bin/bash

echo "🚀 Postgrator Local Başlatılıyor..."

# Renk kodları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Servislerin çalıştığını kontrol et
echo -e "${YELLOW}📊 Servisleri kontrol ediliyor...${NC}"

# MongoDB kontrolü
if ! pgrep -x "mongod" > /dev/null; then
    echo -e "${RED}❌ MongoDB çalışmıyor!${NC}"
    echo -e "${YELLOW}MongoDB'yi başlatmak için: brew services start mongodb-community@7.0${NC}"
    exit 1
fi
echo -e "${GREEN}✅ MongoDB çalışıyor${NC}"

# PostgreSQL kontrolü
if ! pg_isready > /dev/null 2>&1; then
    echo -e "${RED}❌ PostgreSQL çalışmıyor!${NC}"
    echo -e "${YELLOW}PostgreSQL'i başlatmak için: brew services start postgresql@16${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL çalışıyor${NC}"

# Backend başlat (arka planda)
echo -e "${YELLOW}🔧 Backend başlatılıyor...${NC}"
cd backend
source venv/bin/activate 2>/dev/null || true
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
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend başlatılamadı!${NC}"
        echo -e "${YELLOW}Loglara bakın: tail -f backend.log${NC}"
        exit 1
    fi
done

# Frontend başlat (arka planda)
echo -e "${YELLOW}🎨 Frontend başlatılıyor...${NC}"
cd frontend
yarn start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo -e "${GREEN}✅ Frontend başlatıldı (PID: $FRONTEND_PID)${NC}"
cd ..

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Postgrator başarıyla başlatıldı!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📍 Erişim Adresleri:${NC}"
echo -e "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}📋 Loglar:${NC}"
echo -e "   Backend:  ${GREEN}tail -f backend.log${NC}"
echo -e "   Frontend: ${GREEN}tail -f frontend.log${NC}"
echo ""
echo -e "${YELLOW}🛑 Durdurmak için:${NC}"
echo -e "   ${GREEN}./stop-local.sh${NC}"
echo -e "   veya manuel: ${GREEN}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo ""
```

### Durdurma Script'i

Dosya konumu: `/app/stop-local.sh`

```bash
#!/bin/bash

echo "🛑 Postgrator durduruluyor..."

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Backend'i durdur
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo -e "${GREEN}✅ Backend durduruldu (PID: $BACKEND_PID)${NC}"
    fi
    rm backend.pid
fi

# Frontend'i durdur
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✅ Frontend durduruldu (PID: $FRONTEND_PID)${NC}"
    fi
    rm frontend.pid
fi

# Alternatif: Port'a göre durdur
pkill -f "uvicorn server:app" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null
pkill -f "craco start" 2>/dev/null

echo -e "${GREEN}✅ Tüm servisler durduruldu${NC}"
```

### Script'leri çalıştırılabilir yapın:
```bash
chmod +x /app/start-local.sh
chmod +x /app/stop-local.sh
```

---

## ✅ 6. Adım: Bağlantı Testleri

### MongoDB Testi
```bash
mongosh mongodb://localhost:27017/postgrator_db << EOF
db.runCommand({ ping: 1 })
exit
EOF
```

### PostgreSQL Testi
```bash
psql -U postgres -d target_db -h localhost -p 5432 -c "SELECT version();"
```

### Backend API Testi
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

### Frontend Testi
```bash
# Tarayıcıda açın
open http://localhost:3000
```

---

## 🎯 7. Demo Modu ile Test

**Demo modu** PostgreSQL/MSSQL bağlantısı gerektirmeden migration işlemini simüle eder:

1. Frontend'i açın: http://localhost:3000
2. "Demo Modu İle Dene" butonuna tıklayın
3. 8 simüle edilmiş tablo (Northwind DB) göreceksiniz
4. Herhangi bir tabloyu seçip verilerini inceleyebilirsiniz

---

## 🔧 Sorun Giderme

### ❌ "nodename nor servname provided"
**Neden:** .env dosyasında Docker hostname'leri kullanılıyor

**Çözüm:**
```bash
# backend/.env dosyasını düzenleyin
MONGO_URL="mongodb://localhost:27017"  # mongodb:27017 değil!
```

### ❌ "Connection refused" (MongoDB)
```bash
# MongoDB'nin çalıştığını kontrol edin
brew services list | grep mongodb

# Çalışmıyorsa başlatın
brew services start mongodb-community@7.0

# Log'ları kontrol edin
tail -f /opt/homebrew/var/log/mongodb/mongo.log
```

### ❌ "psycopg.OperationalError"
```bash
# PostgreSQL'in çalıştığını kontrol edin
pg_isready

# Çalışmıyorsa başlatın
brew services start postgresql@16

# Bağlantı testi
psql -U postgres -d target_db -h localhost
```

### ❌ Port zaten kullanımda
```bash
# Port 8000 (Backend)
lsof -ti:8000 | xargs kill -9

# Port 3000 (Frontend)
lsof -ti:3000 | xargs kill -9
```

### ❌ Python modül bulunamadı
```bash
# Virtual environment'ı aktif edin
source backend/venv/bin/activate

# Bağımlılıkları tekrar yükleyin
pip install -r backend/requirements.txt
```

---

## 📊 Sistem Gereksinimleri

### Minimum:
- **CPU**: 2 çekirdek
- **RAM**: 4 GB
- **Disk**: 2 GB boş alan
- **OS**: macOS 11+ (Big Sur)

### Önerilen:
- **CPU**: 4+ çekirdek
- **RAM**: 8+ GB
- **Disk**: 5+ GB boş alan (SSD)
- **OS**: macOS 13+ (Ventura)

---

## 🆘 Yardım ve Destek

### Log Dosyaları:
```bash
# Backend logları
tail -f /app/backend.log

# Frontend logları
tail -f /app/frontend.log

# MongoDB logları
tail -f /opt/homebrew/var/log/mongodb/mongo.log

# PostgreSQL logları
tail -f /opt/homebrew/var/log/postgresql@16.log
```

### Veritabanı Sıfırlama:
```bash
# MongoDB'yi temizle
mongosh mongodb://localhost:27017/postgrator_db --eval "db.dropDatabase()"

# PostgreSQL'i temizle
psql -U postgres -c "DROP DATABASE IF EXISTS target_db;"
psql -U postgres -c "CREATE DATABASE target_db OWNER postgres;"
```

---

## ✨ Hızlı Başlangıç Özeti

```bash
# 1. Servisleri başlat
brew services start mongodb-community@7.0
brew services start postgresql@16

# 2. Projeyi başlat
cd /app
./start-local.sh

# 3. Tarayıcıda aç
open http://localhost:3000

# 4. Demo modunu dene
# Frontend'te "Demo Modu İle Dene" butonuna tıkla
```

**🎉 Başarılar! Artık projenizi Docker olmadan local olarak çalıştırabilirsiniz.**
