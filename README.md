# Postgrator - SQL Server to PostgreSQL Migration Tool

## 🎯 Genel Bakış

Postgrator, SQL Server .bak yedeklerini PostgreSQL'e hızlı, güvenli ve kayıpsız aktaran modern bir migration aracıdır.

### ✨ Özellikler

- **Tek Tık Migrasyon**: .bak dosyası yükle, PostgreSQL bilgilerini gir, başlat
- **Şema Koruması**: Tablolar, kolonlar, primary key'ler, foreign key'ler, index'ler bozulmadan aktarılır
- **Hızlı Veri Transferi**: PostgreSQL COPY protokolü ile yüksek performans
- **Gerçek Zamanlı İzleme**: WebSocket ile canlı ilerleme takibi
- **Detaylı Raporlama**: Schema DDL, satır sayıları, hata logları
- **Veri Görüntüleme**: Migrated tabloları sayfalı olarak görüntüleme

## 🏗️ Mimari

### Tech Stack
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Python 3.11
- **Veritabanları**: 
  - MSSQL 2022 (geçici restore için)
  - PostgreSQL 16 (hedef)
- **Real-time**: WebSockets
- **Docker**: Full stack containerization

## 🚀 Kurulum

### 💻 Local Çalıştırma (Docker Olmadan) - **YENİ!**

macOS'ta Docker olmadan local çalıştırmak için:

#### ⚡ Hızlı Başlangıç (5 dakika)
```bash
# 1. Gerekli yazılımları kur
brew install python@3.11 node mongodb-community@7.0 postgresql@16
npm install -g yarn

# 2. Veritabanlarını başlat
brew services start mongodb-community@7.0
brew services start postgresql@16

# 3. PostgreSQL veritabanı oluştur
psql postgres -c "CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;"
psql postgres -c "CREATE DATABASE target_db OWNER postgres;"

# 4. Projeyi başlat
cd /app
./start-local.sh

# Tarayıcıda aç: http://localhost:3000
```

#### 📖 Local Dokümantasyon
- **🚀 Hızlı Başlangıç**: [HIZLI_BASLANGIÇ.md](./HIZLI_BASLANGIÇ.md) - 5 dakikada çalıştır
- **📚 Komple Kılavuz**: [LOCAL_KURULUM_KILAVUZU.md](./LOCAL_KURULUM_KILAVUZU.md) - Tüm detaylar
- **🐘 PostgreSQL Kurulum**: [MACOS_POSTGRESQL_KURULUM.md](./MACOS_POSTGRESQL_KURULUM.md) - macOS'ta PostgreSQL

---

### 🐳 Docker ile Çalıştırma

#### ⚡ Hızlı Başlangıç (2 dakika)
```bash
# Tüm servisleri başlat
docker-compose up -d

# Tarayıcıda aç
# http://localhost:3000
```

#### 🎮 Sadece Demo İçin (Hafif)
MSSQL olmadan sadece demo modu için:
```bash
docker-compose -f docker-compose.demo.yml up -d
```

#### 📖 Docker Dokümanlar
- **Hızlı Başlangıç**: [QUICKSTART.md](./QUICKSTART.md) - 2 dakikada çalıştır
- **Detaylı Kurulum**: [LOCALHOST_SETUP.md](./LOCALHOST_SETUP.md) - Tüm detaylar ve sorun giderme
- **Test Talimatları**: [TEST_INSTRUCTIONS.md](./TEST_INSTRUCTIONS.md)

#### 🌐 Servisler ve Portlar
| Servis | Port | URL |
|--------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| MongoDB | 27017 | mongodb://localhost:27017 |
| PostgreSQL | 5432 | postgresql://localhost:5432 |
| MSSQL | 1433 | mssql://localhost:1433 |

## 📝 Kullanım

### 🎮 Demo Modu (Önerilen - Test İçin)
Demo modu ile gerçek veritabanı bağlantısı olmadan migration işlemini deneyebilirsiniz:

1. Ana sayfada **"Demo Modu İle Dene"** butonuna tıklayın
2. Simüle edilmiş bir Northwind veritabanı migration'ını izleyin
3. Tüm aşamaları ve özellikleri gerçek zamanlı olarak görün

**Demo Modda:**
- Gerçek .bak dosyası gerekmez
- PostgreSQL bağlantısı gerekmez
- MSSQL sunucusu gerekmez
- Tüm migration süreci simüle edilir

### 📤 Gerçek Migration Modu

#### 1. Dosya Yükleme
- **.bak Dosyası**: Maksimum 50 GB
- **PostgreSQL URI**: `postgresql://user:pass@host:5432/database`
- **Hedef Şema**: Varsayılan `public`

#### 2. İlerleme Takibi
Real-time aşamalar: Doğrulama → Restore → Şema Analizi → Tablo Oluşturma → Veri Kopyalama → Kısıtlamalar → Doğrulama

#### 3. Sonuçlar
**Artifaktlar**: schema.sql, rowcount.csv, errors.log
**Veri Görüntüleme**: Sayfalı tablo görüntüleme

## 🔧 Type Mapping

| MSSQL | PostgreSQL |
|-------|------------|
| INT | INTEGER |
| BIGINT | BIGINT |
| BIT | BOOLEAN |
| NVARCHAR(n) | VARCHAR(n) |
| DATETIME | TIMESTAMP |
| UNIQUEIDENTIFIER | UUID |

---

**MertEnes-Ai** tarafından geliştirilmiştir.
