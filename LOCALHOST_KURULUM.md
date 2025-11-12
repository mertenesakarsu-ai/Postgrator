# 🏠 Localhost Kurulum - Kısa Rehber

## 🎯 Sistem Gereksinimleri

- **Docker Desktop** 20.10+ yüklü olmalı
- **Docker Compose** 2.0+ yüklü olmalı
- En az **8GB RAM** 
- En az **20GB boş disk alanı**

## ⚡ Hızlı Kurulum (3 Adım)

### 1️⃣ Projeyi Hazırla
```bash
cd /path/to/postgrator
```

### 2️⃣ Docker Container'ları Başlat

**Otomatik Kurulum (Önerilen):**
```bash
chmod +x start-local.sh
./start-local.sh
```

**Manuel Kurulum:**
```bash
# Tam Stack (tüm servisler)
docker-compose up -d

# VEYA

# Demo Modu (hafif - sadece demo için)
docker-compose -f docker-compose.demo.yml up -d
```

### 3️⃣ Tarayıcıda Aç
```
http://localhost:3000
```

## 🔍 Kurulum Kontrolü

### Container'ları Kontrol Et
```bash
docker-compose ps
```

Tüm servisler **"Up"** ve **"healthy"** durumda olmalı.

### Port Kontrolü
```bash
# Linux/Mac
lsof -i :3000
lsof -i :8000
lsof -i :27017

# Windows PowerShell
netstat -an | findstr "3000"
netstat -an | findstr "8000"
netstat -an | findstr "27017"
```

### Backend API Kontrolü
```bash
curl http://localhost:8000/api
# Yanıt: {"message":"BAK to PostgreSQL Migration API"}
```

### Frontend Kontrolü
Tarayıcıda açın: http://localhost:3000

## 📦 Servis Detayları

| Servis | Port | Container İsmi | Açıklama |
|--------|------|----------------|----------|
| **Frontend** | 3000 | postgrator_frontend | React UI |
| **Backend** | 8000 | postgrator_backend | FastAPI + WebSocket |
| **MongoDB** | 27017 | postgrator_mongodb | Job veritabanı |
| **PostgreSQL** | 5432 | postgrator_postgres | Hedef veritabanı |
| **MSSQL** | 1433 | postgrator_mssql | Kaynak veritabanı |

## 🎮 İlk Kullanım - Demo Modu

1. http://localhost:3000 adresini açın
2. **"Demo Modu İle Dene"** butonuna tıklayın
3. Migration işlemini gerçek zamanlı izleyin
4. Tamamlandıktan sonra tabloları görüntüleyin

**Demo Modu Özellikleri:**
- ✅ .bak dosyası gerektirmez
- ✅ Gerçek veritabanı bağlantısı gerektirmez
- ✅ 8 demo tablo ile Northwind migration simülasyonu
- ✅ Tüm özellikler çalışır (WebSocket, veri görüntüleme, ilerleme takibi)

## 🛠️ Yaygın Komutlar

### Logları İzle
```bash
# Tüm servisler
docker-compose logs -f

# Sadece backend
docker-compose logs -f backend

# Sadece frontend
docker-compose logs -f frontend

# Son 100 satır
docker-compose logs --tail=100 backend
```

### Servisleri Yönet
```bash
# Yeniden başlat
docker-compose restart

# Durdur
docker-compose down

# Durdur ve verileri sil
docker-compose down -v

# Tek servis yeniden başlat
docker-compose restart backend
```

### Container'a Bağlan (Debug)
```bash
# Backend
docker exec -it postgrator_backend bash

# Frontend
docker exec -it postgrator_frontend sh

# MongoDB
docker exec -it postgrator_mongodb mongosh
```

### Image'ları Yeniden Build Et
```bash
# Tüm servisler
docker-compose build

# Tek servis
docker-compose build backend

# No-cache ile
docker-compose build --no-cache
```

## 🔧 Yapılandırma

### Environment Değişkenleri

**Backend (.env):**
```env
MONGO_URL=mongodb://mongodb:27017
DB_NAME=postgrator_db
MSSQL_HOST=mssql
MSSQL_PORT=1433
MSSQL_SA_PWD=YourStrong!Passw0rd
```

**Frontend (.env):**
```env
REACT_APP_BACKEND_URL=http://localhost:8000
WDS_SOCKET_PORT=3000
```

### Port Değiştirme

Eğer portlar çakışıyorsa `docker-compose.yml` dosyasını düzenleyin:

```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Host:Container
  backend:
    ports:
      - "8001:8000"  # Host:Container
```

**Not:** Port değiştirirseniz `frontend/.env` dosyasındaki `REACT_APP_BACKEND_URL`'yi de güncelleyin.

## 🐛 Sorun Giderme

### Frontend Açılmıyor
```bash
# Logları kontrol et
docker-compose logs frontend

# Yeniden başlat
docker-compose restart frontend

# Yeniden build et
docker-compose build frontend && docker-compose up -d frontend
```

### Backend API Çalışmıyor
```bash
# Logları kontrol et
docker-compose logs backend

# Health check
curl http://localhost:8000/api

# Container'a gir ve kontrol et
docker exec -it postgrator_backend bash
curl localhost:8000/api
```

### MongoDB Bağlantı Hatası
```bash
# MongoDB'nin çalıştığını kontrol et
docker-compose ps mongodb

# MongoDB logları
docker-compose logs mongodb

# MongoDB'ye bağlan
docker exec -it postgrator_mongodb mongosh
```

### Port Çakışması
```bash
# Hangi process kullanıyor bul
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kullanımda olan portları serbest bırak veya docker-compose.yml'de değiştir
```

### Container Başlamıyor (Health Check Failed)
```bash
# Container durumunu kontrol et
docker-compose ps

# Health check loglarını gör
docker inspect postgrator_backend | grep -A 10 Health

# Manuel health check
docker exec postgrator_backend curl localhost:8000/api
```

### Disk Dolu
```bash
# Docker disk kullanımı
docker system df

# Kullanılmayan image'ları temizle
docker image prune -a

# Kullanılmayan volume'ları temizle
docker volume prune

# Tüm kullanılmayanları temizle
docker system prune -a --volumes
```

## 🔄 Hot Reload

Her iki servis de hot reload destekler:

**Backend:**
- `/app/backend` klasöründeki değişiklikler otomatik yansır
- Uvicorn `--reload` flag'i ile çalışır

**Frontend:**
- `/app/frontend/src` klasöründeki değişiklikler otomatik yansır
- React development server ile çalışır

**Not:** `node_modules` ve `__pycache__` değişiklikleri yansımaz, rebuild gerektirir.

## 📊 WebSocket Yapılandırması

WebSocket bağlantısı otomatik olarak backend URL'den türetilir:

```javascript
// Frontend'de otomatik dönüşüm
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
// http://localhost:8000

const WS_URL = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://');
// ws://localhost:8000

// WebSocket endpoint
ws://localhost:8000/api/jobs/{job_id}/stream
```

## 🎯 Production Deployment

**⚠️ Uyarı:** Bu yapılandırma **sadece development** içindir.

Production için:
- Şifreleri değiştirin
- CORS ayarlarını daraltın
- HTTPS kullanın
- Volume backup'ları alın
- Resource limit'leri ayarlayın
- Health check'leri optimize edin

## 📚 Ek Kaynaklar

- **README.md** - Genel özellikler ve mimari
- **LOCALHOST_CONFIG.md** - Detaylı yapılandırma açıklamaları
- **LOCALHOST_SETUP.md** - Genişletilmiş kurulum kılavuzu
- **TEST_INSTRUCTIONS.md** - Test senaryoları
- **YAPILAN_DEGISIKLIKLER.md** - Değişiklik geçmişi

## 🆘 Destek

Sorun yaşıyorsanız:

1. **Logları kontrol edin**: `docker-compose logs -f`
2. **Sorun giderme bölümünü okuyun** (yukarıda)
3. **Container'ları yeniden başlatın**: `docker-compose restart`
4. **Temiz kurulum yapın**: `docker-compose down -v && docker-compose up -d`

## ✅ Başarılı Kurulum Kontrol Listesi

- [ ] Docker ve Docker Compose yüklü
- [ ] Portlar (3000, 8000, 27017, 5432, 1433) boş veya çakışmalar çözüldü
- [ ] `docker-compose up -d` başarılı
- [ ] Tüm container'lar "Up" ve "healthy"
- [ ] http://localhost:3000 açılıyor
- [ ] http://localhost:8000/api yanıt veriyor
- [ ] Demo modu test edildi ve çalışıyor
- [ ] WebSocket bağlantısı kurulabiliyor

---

**🎉 Kurulum tamamlandı! İyi migrasyonlar!**
