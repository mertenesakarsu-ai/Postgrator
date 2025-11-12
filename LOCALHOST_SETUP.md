# 🏠 Localhost Kurulum Kılavuzu

Bu doküman, Postgrator uygulamasını localhost'ta Docker ile çalıştırmanız için gerekli tüm adımları içerir.

## 📋 Gereksinimler

Sisteminizde şunların yüklü olması gerekir:
- **Docker Desktop** (v20.10+)
- **Docker Compose** (v2.0+)
- En az **8GB RAM** (tüm container'lar için)
- En az **20GB Disk** (veritabanları ve yüklemeler için)

## 🚀 Hızlı Başlangıç

### 1. Projeyi Klonlayın (veya indirin)
```bash
cd /path/to/postgrator
```

### 2. Tüm Servisleri Başlatın
```bash
docker-compose up -d
```

Bu komut şu servisleri başlatacak:
- ✅ **MongoDB** (port 27017) - Job takibi ve metadata
- ✅ **MSSQL** (port 1433) - Kaynak veritabanı (geçici restore için)
- ✅ **PostgreSQL** (port 5432) - Hedef veritabanı
- ✅ **Backend** (port 8000) - FastAPI + WebSocket
- ✅ **Frontend** (port 3000) - React UI

### 3. Servislerin Durumunu Kontrol Edin
```bash
docker-compose ps
```

Tüm servisler "Up" ve "healthy" durumda olmalı.

### 4. Tarayıcıda Açın
```
http://localhost:3000
```

## 🎮 Kullanım

### Demo Modu (Önerilen - İlk Test)
1. Ana sayfada **"Demo Modu İle Dene"** butonuna tıklayın
2. Simüle edilmiş Northwind migration'ını izleyin
3. Demo modu gerçek veritabanı bağlantısı gerektirmez

### Gerçek Migration
1. `.bak` dosyanızı yükleyin
2. PostgreSQL bağlantı bilgilerini girin:
   ```
   postgresql://postgres:postgres@postgres:5432/target_db
   ```
3. Migration'ı başlatın ve real-time takip edin

## 🔧 Servisler ve Portlar

| Servis | Port | URL | Açıklama |
|--------|------|-----|----------|
| Frontend | 3000 | http://localhost:3000 | React UI |
| Backend | 8000 | http://localhost:8000 | FastAPI + WebSocket |
| MongoDB | 27017 | mongodb://localhost:27017 | Job veritabanı |
| PostgreSQL | 5432 | postgresql://localhost:5432 | Hedef DB |
| MSSQL | 1433 | mssql://localhost:1433 | Kaynak DB |

## 📝 Yaygın Komutlar

### Tüm Servisleri Başlat
```bash
docker-compose up -d
```

### Logları İzle
```bash
# Tüm servisler
docker-compose logs -f

# Sadece backend
docker-compose logs -f backend

# Sadece frontend
docker-compose logs -f frontend
```

### Servisleri Yeniden Başlat
```bash
# Tüm servisler
docker-compose restart

# Tek bir servis
docker-compose restart backend
```

### Servisleri Durdur
```bash
docker-compose down
```

### Servisleri Durdur ve Verileri Sil
```bash
docker-compose down -v
```

### Container'a Bağlan (Debug için)
```bash
# Backend
docker exec -it postgrator_backend bash

# Frontend
docker exec -it postgrator_frontend sh

# MongoDB
docker exec -it postgrator_mongodb mongosh
```

## 🐛 Sorun Giderme

### Frontend Açılmıyor
```bash
# Logları kontrol edin
docker-compose logs frontend

# Container'ı yeniden başlatın
docker-compose restart frontend
```

### Backend API Çalışmıyor
```bash
# Backend loglarını kontrol edin
docker-compose logs backend

# Bağlantı testi
curl http://localhost:8000/api
```

### Port Çakışması
Eğer bir port kullanımda ise, `docker-compose.yml` dosyasında port numarasını değiştirebilirsiniz:
```yaml
ports:
  - "3001:3000"  # 3000 yerine 3001 kullan
```

### MongoDB Bağlantı Hatası
```bash
# MongoDB'nin çalıştığından emin olun
docker-compose ps mongodb

# MongoDB loglarını kontrol edin
docker-compose logs mongodb

# Healthcheck durumunu test edin
docker exec postgrator_mongodb mongosh --eval "db.runCommand('ping')"
```

### Container Build Hatası
```bash
# Cache'i temizleyip yeniden build edin
docker-compose build --no-cache
docker-compose up -d
```

## 🔄 Kod Değişikliklerinde

### Backend Değişiklikleri
- Backend kodu **hot-reload** ile çalışır
- Python dosyalarını düzenleyin, otomatik yeniden yüklenir
- Yeni dependency eklerseniz:
  ```bash
  docker-compose restart backend
  ```

### Frontend Değişiklikleri
- Frontend kodu **hot-reload** ile çalışır
- React dosyalarını düzenleyin, tarayıcı otomatik yenilenir
- Yeni npm paketi eklerseniz:
  ```bash
  docker-compose restart frontend
  ```

## 📊 Veritabanı Erişimi

### MongoDB
```bash
docker exec -it postgrator_mongodb mongosh

# Veritabanı seç
use postgrator_db

# Job'ları listele
db.jobs.find()
```

### PostgreSQL
```bash
docker exec -it postgrator_postgres psql -U postgres -d target_db

# Tabloları listele
\dt

# Şemaları listele
\dn
```

### MSSQL
```bash
docker exec -it postgrator_mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd'

# Veritabanlarını listele
SELECT name FROM sys.databases;
GO
```

## 🔐 Varsayılan Şifreler

**⚠️ Üretim ortamında mutlaka değiştirin!**

- **MSSQL SA**: `YourStrong!Passw0rd`
- **PostgreSQL**: `postgres` / `postgres`
- **MongoDB**: Şifre yok (localhost only)

## 📚 Ek Kaynaklar

- [Ana README](./README.md) - Uygulama özellikleri
- [Test Talimatları](./TEST_INSTRUCTIONS.md) - Test senaryoları
- [Docker Compose Referansı](https://docs.docker.com/compose/)

## 💡 İpuçları

1. **İlk Başlatma**: İlk `docker-compose up` komutu image'ları indireceği için 5-10 dakika sürebilir
2. **Disk Alanı**: Migration sırasında .bak dosyaları ve veritabanları disk alanı kullanır
3. **Performance**: Docker Desktop'a en az 4GB RAM ayırın (Settings → Resources)
4. **Development**: Hot-reload aktif, kod değişiklikleri anında yansır

## 🆘 Yardım

Sorun yaşıyorsanız:
1. Logları kontrol edin: `docker-compose logs -f`
2. Servislerin durumunu kontrol edin: `docker-compose ps`
3. Container'ları yeniden başlatın: `docker-compose restart`
4. Tamamen temiz başlatın: `docker-compose down -v && docker-compose up -d`

---

**Başarılar! 🚀** Sorularınız için issue açabilirsiniz.
