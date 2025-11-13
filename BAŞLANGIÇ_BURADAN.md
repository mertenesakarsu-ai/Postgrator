# 🎯 BAŞLANGIÇ BURADAN - Docker Olmadan Local Çalıştırma

## 📌 Sorunuz Ne İdi?

**Hata**: `nodename nor servname provided, or not known`  
**Sebep**: Docker container hostname'leri (`mongodb:27017`, `postgres:5432`) local sistemde çalışmıyor  
**Çözüm**: ✅ Tüm bağlantılar `localhost` kullanacak şekilde yapılandırıldı

---

## ✅ Yapılan Değişiklikler

### 1. Environment Dosyaları Güncellendi
- ✅ Backend: MongoDB, MSSQL ve PostgreSQL local hostname'lere ayarlandı
- ✅ Frontend: Backend URL `localhost:8000` olarak ayarlandı

### 2. Başlatma Script'leri Eklendi
- ✅ `start-local.sh`: Tek komutla tüm servisleri başlatır
- ✅ `stop-local.sh`: Tek komutla tüm servisleri durdurur

### 3. Detaylı Dokümantasyon Hazırlandı
- ✅ macOS PostgreSQL kurulum kılavuzu
- ✅ Komple local kurulum kılavuzu
- ✅ Hızlı başlangıç (5 dakika)

---

## 🚀 Hemen Başlayın

### Seçenek 1: En Hızlı Yol (5 Dakika) ⚡

```bash
# 1. Gerekli yazılımları tek komutla kurun
brew install python@3.11 node mongodb-community@7.0 postgresql@16
npm install -g yarn

# 2. PATH ayarı
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 3. Veritabanlarını başlatın
brew services start mongodb-community@7.0
brew services start postgresql@16

# 4. PostgreSQL kullanıcı ve veritabanı oluşturun
psql postgres << EOF
CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;
CREATE DATABASE target_db OWNER postgres;
\q
EOF

# 5. Projeyi başlatın
cd /app
./start-local.sh

# Tarayıcıda açılacak: http://localhost:3000
```

---

### Seçenek 2: Adım Adım Kurulum 📚

**Bölüm 1: PostgreSQL Kurulumu**
👉 [MACOS_POSTGRESQL_KURULUM.md](./MACOS_POSTGRESQL_KURULUM.md) dosyasını okuyun

**Bölüm 2: Proje Kurulumu**
👉 [LOCAL_KURULUM_KILAVUZU.md](./LOCAL_KURULUM_KILAVUZU.md) dosyasını okuyun

**Bölüm 3: Hızlı Başlangıç**
👉 [HIZLI_BASLANGIÇ.md](./HIZLI_BASLANGIÇ.md) dosyasını okuyun

---

## 📋 Hangi Dosyaya Bakmalıyım?

### 1. İlk Kurulum İçin
```
HIZLI_BASLANGIÇ.md        → En hızlı başlangıç (5 dk)
```

### 2. PostgreSQL Kurulum Sorunları İçin
```
MACOS_POSTGRESQL_KURULUM.md → Detaylı PostgreSQL kurulum
                               + Sorun giderme
                               + Güvenlik ayarları
```

### 3. Komple Kurulum İçin
```
LOCAL_KURULUM_KILAVUZU.md   → Tüm adımlar
                               + Backend/Frontend kurulumu
                               + Test prosedürleri
                               + 10 farklı sorun giderme
```

### 4. Yapılan Değişiklikleri Görmek İçin
```
DOCKER_OLMADAN_CALISTIRMA.md → Özet değişiklikler
YAPILAN_DEGISIKLIKLER_LOCAL.md → Detaylı değişiklik raporu
```

---

## ⚙️ Temel Komutlar

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

### Test
```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
open http://localhost:3000

# Demo modu
# Frontend'te "Demo Modu İle Dene" butonuna tıkla
```

### Loglar
```bash
# Backend
tail -f /app/backend.log

# Frontend
tail -f /app/frontend.log
```

---

## 🔧 Hızlı Sorun Giderme

### ❌ MongoDB Çalışmıyor
```bash
brew services start mongodb-community@7.0
```

### ❌ PostgreSQL Çalışmıyor
```bash
brew services start postgresql@16
# Veritabanı yoksa:
psql postgres -c "CREATE DATABASE target_db OWNER postgres;"
```

### ❌ Port Kullanımda
```bash
# Backend port (8000)
lsof -ti:8000 | xargs kill -9

# Frontend port (3000)
lsof -ti:3000 | xargs kill -9
```

### ❌ Bağlantı Hatası Alıyorum
**.env dosyalarını kontrol edin:**
```bash
# Backend
cat /app/backend/.env | grep MONGO_URL
# Beklenen: mongodb://localhost:27017

# Frontend
cat /app/frontend/.env | grep REACT_APP_BACKEND_URL
# Beklenen: http://localhost:8000
```

---

## 📦 Gerekli Yazılımlar

| Yazılım | Amaç | Kurulum |
|---------|------|---------|
| Python 3.11+ | Backend | `brew install python@3.11` |
| Node.js 18+ | Frontend | `brew install node` |
| Yarn | Package manager | `npm install -g yarn` |
| MongoDB 7.0 | Job tracking | `brew install mongodb-community@7.0` |
| PostgreSQL 16 | Target DB | `brew install postgresql@16` |

**Hepsini Tek Komutla:**
```bash
brew install python@3.11 node mongodb-community@7.0 postgresql@16 && npm install -g yarn
```

---

## 🎯 Bağlantı String'leri

### ✅ Doğru (Local)
```bash
# MongoDB
mongodb://localhost:27017

# PostgreSQL
postgresql://postgres:postgres@localhost:5432/target_db
```

### ❌ Yanlış (Docker)
```bash
# Bunlar artık kullanılmıyor
mongodb://mongodb:27017
postgresql://postgres@postgres:5432/target_db
```

---

## 🧪 Demo Modu

PostgreSQL veya MSSQL kurulumu yapmadan test etmek için:

1. Projeyi başlatın: `./start-local.sh`
2. Tarayıcıda açın: http://localhost:3000
3. **"Demo Modu İle Dene"** butonuna tıklayın
4. 8 simüle edilmiş tablo görüntülenecek (Northwind DB)
5. Tablolardan birini seçip örnek verileri inceleyin

Demo modu gerçek veritabanı bağlantısı gerektirmez!

---

## 📂 Proje Yapısı

```
/app/
├── backend/
│   ├── .env              ✅ Local ayarlar (güncellendi)
│   ├── .env.local        Template
│   └── server.py
│
├── frontend/
│   ├── .env              ✅ Local ayarlar (güncellendi)
│   ├── .env.local        Template
│   └── package.json
│
├── start-local.sh        ✅ Başlatma script'i
├── stop-local.sh         ✅ Durdurma script'i
│
└── Dokümantasyon:
    ├── BAŞLANGIÇ_BURADAN.md              ← ŞU ANDA BURADASINIZ
    ├── HIZLI_BASLANGIÇ.md                Hızlı başlangıç
    ├── LOCAL_KURULUM_KILAVUZU.md         Komple kılavuz
    ├── MACOS_POSTGRESQL_KURULUM.md       PostgreSQL kılavuzu
    └── DOCKER_OLMADAN_CALISTIRMA.md      Özet değişiklikler
```

---

## ✅ Checklist

Kurulumunuzu kontrol edin:

- [ ] Homebrew kurulu mu? → `brew --version`
- [ ] Python kurulu mu? → `python3 --version`
- [ ] Node.js kurulu mu? → `node --version`
- [ ] Yarn kurulu mu? → `yarn --version`
- [ ] MongoDB çalışıyor mu? → `pgrep -x mongod`
- [ ] PostgreSQL çalışıyor mu? → `pg_isready`
- [ ] target_db oluşturuldu mu? → `psql -U postgres -d target_db -c "\q"`
- [ ] Backend başladı mı? → `curl http://localhost:8000/health`
- [ ] Frontend açılıyor mu? → `open http://localhost:3000`

---

## 🎉 Başarılı Kurulum

Eğer tüm adımlar başarılı olduysa:

✅ Backend çalışıyor: http://localhost:8000  
✅ Frontend çalışıyor: http://localhost:3000  
✅ API Docs: http://localhost:8000/docs  
✅ MongoDB: mongodb://localhost:27017  
✅ PostgreSQL: localhost:5432

**Tebrikler! Projeniz artık Docker olmadan macOS'ta çalışıyor.** 🎉

---

## 🆘 Yardım

Hala sorun mu yaşıyorsunuz?

1. **Logları kontrol edin:**
   ```bash
   tail -f /app/backend.log
   tail -f /app/frontend.log
   ```

2. **Servisleri kontrol edin:**
   ```bash
   brew services list
   ```

3. **Port'ları kontrol edin:**
   ```bash
   lsof -i :8000
   lsof -i :3000
   lsof -i :27017
   lsof -i :5432
   ```

4. **Dokümantasyona bakın:**
   - Hızlı sorunlar → [HIZLI_BASLANGIÇ.md](./HIZLI_BASLANGIÇ.md)
   - PostgreSQL sorunları → [MACOS_POSTGRESQL_KURULUM.md](./MACOS_POSTGRESQL_KURULUM.md)
   - Genel sorunlar → [LOCAL_KURULUM_KILAVUZU.md](./LOCAL_KURULUM_KILAVUZU.md)

---

**Son Güncelleme**: 2025  
**Hedef Platform**: macOS 11+ (Big Sur ve üzeri)  
**Test Edildi**: macOS Ventura (M1/M2) ve Intel Mac
