# 🚀 Hızlı Başlangıç - Docker Olmadan Local Çalıştırma

Bu kılavuz projenizi macOS'ta Docker olmadan çalıştırmak için gereken minimum adımları içerir.

---

## ⚡ 5 Dakikada Kurulum

### 1️⃣ Homebrew Kurulumu (varsa atla)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2️⃣ Gerekli Yazılımları Kur
```bash
# Python, Node.js, MongoDB ve PostgreSQL'i tek komutta kur
brew install python@3.11 node mongodb-community@7.0 postgresql@16

# Yarn'ı kur
npm install -g yarn

# PostgreSQL PATH ayarı
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 3️⃣ Veritabanlarını Başlat
```bash
# MongoDB'yi başlat
brew services start mongodb-community@7.0

# PostgreSQL'i başlat
brew services start postgresql@16

# PostgreSQL kullanıcı ve veritabanı oluştur
psql postgres << EOF
CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;
CREATE DATABASE target_db OWNER postgres;
\q
EOF
```

### 4️⃣ Projeyi Başlat
```bash
cd /app

# Otomatik başlatma script'i
./start-local.sh

# Veya manuel başlatma:
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000 --reload &

# Frontend
cd ../frontend
yarn install
yarn start &
```

---

## 🎯 Hızlı Test

### Tarayıcıda Aç
```bash
open http://localhost:3000
```

### Demo Modunu Dene
1. Frontend'te **"Demo Modu İle Dene"** butonuna tıkla
2. 8 simüle edilmiş tablo görüntülenecek (Northwind DB)
3. Herhangi bir tabloyu seçip verilerini incele

### API Testi
```bash
# Health check
curl http://localhost:8000/health

# API dokümantasyonu
open http://localhost:8000/docs
```

---

## 🛑 Durdurma

```bash
cd /app
./stop-local.sh

# Veya manuel:
pkill -f "uvicorn server:app"
pkill -f "craco start"
```

---

## 🔧 Sorun Giderme

### ❌ Bağlantı Hatası: "nodename nor servname provided"
Bu hatayı aldıysanız, .env dosyaları doğru ayarlanmıştır. Ancak servislerin çalıştığından emin olun:

```bash
# MongoDB kontrol
pgrep -x mongod
# Yoksa: brew services start mongodb-community@7.0

# PostgreSQL kontrol
pg_isready
# Yoksa: brew services start postgresql@16
```

### ❌ Port Kullanımda
```bash
# Port 8000 (Backend)
lsof -ti:8000 | xargs kill -9

# Port 3000 (Frontend)
lsof -ti:3000 | xargs kill -9
```

### ❌ PostgreSQL Bağlantı Hatası
```bash
# Bağlantıyı test et
psql -U postgres -d target_db -h localhost -p 5432

# Çalışmıyorsa:
brew services restart postgresql@16

# Veritabanı yoksa:
psql postgres -c "CREATE DATABASE target_db OWNER postgres;"
```

---

## 📚 Detaylı Dokümantasyon

- **PostgreSQL Kurulum**: [MACOS_POSTGRESQL_KURULUM.md](./MACOS_POSTGRESQL_KURULUM.md)
- **Komple Kılavuz**: [LOCAL_KURULUM_KILAVUZU.md](./LOCAL_KURULUM_KILAVUZU.md)

---

## ✅ Bağlantı String'leri

Doğru bağlantı formatları (artık .env dosyalarında ayarlandı):

```bash
# MongoDB (Local)
mongodb://localhost:27017

# PostgreSQL (Local)
postgresql://postgres:postgres@localhost:5432/target_db
```

❌ **Kullanmayın**: `mongodb://mongodb:27017` (Docker hostname)
✅ **Kullanın**: `mongodb://localhost:27017` (Local)

---

## 🎉 Hazırsınız!

Artık projeniz Docker olmadan local olarak çalışıyor. Sorularınız için detaylı kılavuzlara bakabilirsiniz.
