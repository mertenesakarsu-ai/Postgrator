# 🔧 Localhost Yapılandırma Detayları

Bu doküman, projenin localhost'ta nasıl yapılandırıldığını açıklar.

## 📁 Yapılandırma Dosyaları

### 1. Docker Compose Dosyaları

#### `docker-compose.yml` (Tam Stack)
Tüm servisleri içerir:
- ✅ MongoDB (Job tracking)
- ✅ MSSQL 2022 (Kaynak DB - .bak restore için)
- ✅ PostgreSQL 16 (Hedef DB)
- ✅ Backend (FastAPI + WebSocket)
- ✅ Frontend (React)

**Kullanım:**
```bash
docker-compose up -d
```

#### `docker-compose.demo.yml` (Hafif)
Sadece demo için gerekli servisler:
- ✅ MongoDB
- ✅ PostgreSQL (alpine - hafif)
- ✅ Backend
- ✅ Frontend
- ❌ MSSQL (demo'da gerekmez)

**Kullanım:**
```bash
docker-compose -f docker-compose.demo.yml up -d
```

### 2. Dockerfile'lar

#### `backend/Dockerfile`
- Base: Python 3.11 slim
- ODBC Driver 18 for SQL Server
- Hot-reload aktif (--reload flag)
- Port: 8000

#### `frontend/Dockerfile`
- Base: Node 18 alpine
- Yarn package manager
- Hot-reload aktif
- Port: 3000

### 3. Environment Dosyaları

#### `backend/.env`
```env
MONGO_URL="mongodb://mongodb:27017"     # Docker servis ismi
DB_NAME="postgrator_db"
MSSQL_HOST="mssql"                      # Docker servis ismi
MSSQL_PORT="1433"
POSTGRES_TARGET="postgres"              # Docker servis ismi
```

#### `frontend/.env`
```env
REACT_APP_BACKEND_URL=http://localhost:8000  # Host'tan erişim
WDS_SOCKET_PORT=3000
```

## 🌐 Network Yapılandırması

### Docker Network: `postgrator_network`
Tüm container'lar bridge network'te haberleşir.

### Servis İsimleri (Container'lar arası)
```
mongodb:27017       → MongoDB
mssql:1433          → MSSQL Server
postgres:5432       → PostgreSQL
backend:8001        → Backend API
```

### Port Mapping (Host → Container)
```
localhost:27017  → mongodb:27017
localhost:1433   → mssql:1433
localhost:5432   → postgres:5432
localhost:8001   → backend:8001
localhost:3000   → frontend:3000
```

## 🔄 WebSocket Yapılandırması

Frontend'de otomatik protokol dönüşümü:
```javascript
const WS_URL = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://');
// http://localhost:8001 → ws://localhost:8001
```

WebSocket endpoint:
```
ws://localhost:8001/api/jobs/{job_id}/stream
```

## 📦 Volume Mapping

### Kod (Hot-reload için)
```yaml
volumes:
  - ./backend:/app          # Backend kodu
  - ./frontend:/app         # Frontend kodu
  - /app/node_modules       # Node modules ayrı volume
```

### Veri (Persistence)
```yaml
volumes:
  - mongodb_data:/data/db
  - mssql_data:/var/opt/mssql/data
  - postgres_data:/var/lib/postgresql/data
  - backend_uploads:/app/uploads
  - ./backups:/app/backups
```

## 🔐 Varsayılan Şifreler

**⚠️ Sadece development için! Production'da değiştirin!**

| Servis | Kullanıcı | Şifre |
|--------|-----------|-------|
| MSSQL | sa | YourStrong!Passw0rd |
| PostgreSQL | postgres | postgres |
| MongoDB | - | (şifresiz) |

## 🚦 Health Check'ler

Tüm veritabanı servisleri health check içerir:
- **MongoDB**: `mongosh ping` komutu
- **MSSQL**: `sqlcmd SELECT 1` sorgusu
- **PostgreSQL**: `pg_isready` komutu

Backend bu servisler healthy olana kadar bekler (`depends_on`).

## 🔄 Restart Policy

Tüm servisler `restart: unless-stopped` kullanır:
- Docker başladığında otomatik başlar
- Crash durumunda yeniden başlar
- Manuel durdurma haricinde her zaman çalışır

## 🛠️ Development Mode

### Hot Reload
- **Backend**: uvicorn `--reload` flag'i ile
- **Frontend**: React development server ile
- Kod değişikliği → Otomatik yenileme

### Debug
Container'lara bağlanma:
```bash
docker exec -it postgrator_backend bash    # Backend
docker exec -it postgrator_frontend sh     # Frontend
```

### Logs
```bash
docker-compose logs -f backend    # Backend logs
docker-compose logs -f frontend   # Frontend logs
docker-compose logs -f           # Tüm logs
```

## 📊 API Base URLs

### Frontend'den Backend'e
```javascript
const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
// http://localhost:8001/api
```

### Backend'den MongoDB'ye
```python
MONGO_URL = os.environ.get('MONGO_URL')
# mongodb://mongodb:27017
```

### Backend'den MSSQL'e
```python
MSSQL_HOST = os.environ.get('MSSQL_HOST')
# mssql (Docker servis ismi)
```

## 🎯 Demo Mode

Demo modu için **hiçbir gerçek veritabanı bağlantısı** gerekmez:
- `.bak` dosyası yüklenmez
- MSSQL restore yapılmaz
- PostgreSQL'e yazılmaz
- Tüm veriler simüle edilir (in-memory)

Demo job'lar `is_demo=True` flag'i ile işaretlenir.

## 🔍 Troubleshooting

### Port çakışması
`docker-compose.yml`'deki port mapping'i değiştirin:
```yaml
ports:
  - "3001:3000"  # 3000 yerine 3001
```

### Container başlamıyor
```bash
docker-compose logs [service_name]
docker-compose restart [service_name]
```

### Disk doldu
```bash
# Kullanılmayan volume'ları temizle
docker volume prune

# Tüm container'ları ve volume'ları sil
docker-compose down -v
```

### Hot-reload çalışmıyor
```bash
# Container'ı yeniden build et
docker-compose build [service_name]
docker-compose up -d [service_name]
```

## 📚 İlgili Dokümanlar

- [QUICKSTART.md](./QUICKSTART.md) - Hızlı başlangıç
- [LOCALHOST_SETUP.md](./LOCALHOST_SETUP.md) - Detaylı kurulum
- [README.md](./README.md) - Uygulama özellikleri

---

**Not:** Bu yapılandırma development environment içindir. Production deployment için farklı yapılandırma gerekir.
