# 🎯 Docker Olmadan Local Çalıştırma - Özet

## 📋 Yapılan Değişiklikler

Projenizi Docker olmadan macOS'ta local çalıştırmak için aşağıdaki değişiklikler yapıldı:

### 1. ✅ Environment Dosyaları Güncellendi

#### Backend (.env)
```diff
- MONGO_URL="mongodb://mongodb:27017"        # Docker hostname
+ MONGO_URL="mongodb://localhost:27017"      # Local hostname

- MSSQL_HOST="mssql"                         # Docker hostname
+ MSSQL_HOST="localhost"                      # Local hostname

+ # PostgreSQL Configuration (Yeni Eklendi)
+ POSTGRES_HOST="localhost"
+ POSTGRES_PORT="5432"
+ POSTGRES_USER="postgres"
+ POSTGRES_PASSWORD="postgres"
+ POSTGRES_DB="target_db"
```

#### Frontend (.env)
```diff
- REACT_APP_BACKEND_URL=https://psql-config-guide.preview.emergentagent.com
+ REACT_APP_BACKEND_URL=http://localhost:8000

- WATCHPACK_POLLING=true                     # Docker için gerekli
+ WATCHPACK_POLLING=false                    # Local'de gereksiz

- CHOKIDAR_USEPOLLING=true
+ CHOKIDAR_USEPOLLING=false
```

### 2. ✅ Başlatma Script'leri Eklendi

#### `/app/start-local.sh`
- Servislerin çalıştığını kontrol eder
- Backend'i uvicorn ile başlatır (port 8000)
- Frontend'i yarn ile başlatır (port 3000)
- Health check yapar
- Detaylı durum bilgisi gösterir

#### `/app/stop-local.sh`
- Backend ve frontend process'lerini güvenli şekilde durdurur
- Port'ları temizler
- Zombie process'leri temizler

### 3. ✅ Dokümantasyon Eklendi

- **MACOS_POSTGRESQL_KURULUM.md**: Detaylı PostgreSQL kurulum kılavuzu
- **LOCAL_KURULUM_KILAVUZU.md**: Komple local çalıştırma kılavuzu
- **HIZLI_BASLANGIÇ.md**: 5 dakikalık hızlı başlangıç
- **.env.local** dosyaları: Template'ler

---

## 🔑 Anahtar Nokta: Bağlantı String Hatası Düzeltildi

### ❌ Eski (Hatalı)
```
mongodb://mongodb:27017
postgresql://postgres:postgres@postgres:5432/target_db
```

Bu Docker container hostname'leri local ortamda çalışmaz ve şu hatayı verir:
```
nodename nor servname provided, or not known
```

### ✅ Yeni (Doğru)
```
mongodb://localhost:27017
postgresql://postgres:postgres@localhost:5432/target_db
```

---

## 🚀 Kullanım

### Başlatma
```bash
cd /app
./start-local.sh
```

### Durdurma
```bash
cd /app
./stop-local.sh
```

### Manuel Başlatma
```bash
# Backend
cd /app/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Frontend (yeni terminal)
cd /app/frontend
yarn start
```

---

## 📦 Gerekli Yazılımlar

Sisteminizde kurulu olması gerekenler:

1. **Python 3.10+**: Backend için
2. **Node.js 18+**: Frontend için
3. **Yarn**: Package manager
4. **MongoDB**: Job tracking için
5. **PostgreSQL**: Migration hedef DB için

### Hepsi Tek Komutta:
```bash
brew install python@3.11 node mongodb-community@7.0 postgresql@16
npm install -g yarn
```

---

## ⚙️ Veritabanı Kurulumu

### MongoDB
```bash
brew services start mongodb-community@7.0
```

### PostgreSQL
```bash
# Başlat
brew services start postgresql@16

# PATH ekle
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Kullanıcı ve veritabanı oluştur
psql postgres << EOF
CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;
CREATE DATABASE target_db OWNER postgres;
\q
EOF
```

---

## 🧪 Test

### 1. Servis Testleri
```bash
# MongoDB
mongosh mongodb://localhost:27017/postgrator_db --eval "db.runCommand({ ping: 1 })"

# PostgreSQL
psql -U postgres -d target_db -h localhost -c "SELECT version();"

# Backend
curl http://localhost:8000/health

# Frontend
open http://localhost:3000
```

### 2. Demo Modu Testi
1. http://localhost:3000 adresini aç
2. "Demo Modu İle Dene" butonuna tıkla
3. 8 simüle edilmiş tablo görüntülenecek
4. Tablolardan birini seç ve verileri incele

---

## 🔧 Sorun Giderme

### Port Kullanımda
```bash
# Port 8000 (Backend)
lsof -ti:8000 | xargs kill -9

# Port 3000 (Frontend)
lsof -ti:3000 | xargs kill -9
```

### Servis Çalışmıyor
```bash
# Durum kontrol
brew services list

# MongoDB başlat
brew services start mongodb-community@7.0

# PostgreSQL başlat
brew services start postgresql@16
```

### Veritabanı Bulunamadı
```bash
# PostgreSQL veritabanını oluştur
psql postgres -c "CREATE DATABASE target_db OWNER postgres;"

# Kullanıcı oluştur
psql postgres -c "CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;"
```

### Log Kontrol
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

---

## 📁 Dosya Yapısı

```
/app/
├── backend/
│   ├── .env                    # ✅ Local ayarlar (güncellendi)
│   ├── .env.local              # Template
│   ├── server.py
│   └── requirements.txt
│
├── frontend/
│   ├── .env                    # ✅ Local ayarlar (güncellendi)
│   ├── .env.local              # Template
│   └── package.json
│
├── start-local.sh              # ✅ Başlatma script'i
├── stop-local.sh               # ✅ Durdurma script'i
│
├── MACOS_POSTGRESQL_KURULUM.md # ✅ PostgreSQL kılavuzu
├── LOCAL_KURULUM_KILAVUZU.md   # ✅ Komple kılavuz
├── HIZLI_BASLANGIÇ.md          # ✅ Hızlı başlangıç
└── README.md                    # ✅ Güncellendi
```

---

## 🎯 Sonuç

✅ **Çözülen Sorun**: "nodename nor servname provided" hatası  
✅ **Sebep**: Docker hostname'leri (`mongodb:27017`) yerine `localhost` kullanılması gerekiyordu  
✅ **Çözüm**: Tüm .env dosyaları local hostlar için güncellendi  
✅ **Ek**: Otomatik başlatma/durdurma script'leri ve detaylı dokümantasyon eklendi

Artık projeniz Docker olmadan macOS'ta sorunsuz çalışıyor! 🎉

---

## 📚 İlgili Dokümantasyon

- [HIZLI_BASLANGIÇ.md](./HIZLI_BASLANGIÇ.md) - En hızlı başlangıç (5 dk)
- [LOCAL_KURULUM_KILAVUZU.md](./LOCAL_KURULUM_KILAVUZU.md) - Detaylı kılavuz
- [MACOS_POSTGRESQL_KURULUM.md](./MACOS_POSTGRESQL_KURULUM.md) - PostgreSQL kurulum
- [README.md](./README.md) - Proje genel bakış
