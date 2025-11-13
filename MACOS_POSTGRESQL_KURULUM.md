# macOS'ta PostgreSQL Kurulumu ve Yapılandırma Kılavuzu

## 📋 İçindekler
1. [Homebrew ile PostgreSQL Kurulumu](#homebrew-ile-postgresql-kurulumu)
2. [PostgreSQL Başlatma ve Durdurma](#postgresql-başlatma-ve-durdurma)
3. [Veritabanı Oluşturma](#veritabanı-oluşturma)
4. [Bağlantı Testi](#bağlantı-testi)
5. [Sık Karşılaşılan Sorunlar](#sık-karşılaşılan-sorunlar)

---

## 🍺 Homebrew ile PostgreSQL Kurulumu

### 1. Homebrew'un Kurulu Olduğundan Emin Olun
```bash
# Homebrew versiyonunu kontrol edin
brew --version

# Eğer kurulu değilse, Homebrew'u kurun:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. PostgreSQL'i Kurun
```bash
# PostgreSQL 16 kurulumu (en son sürüm)
brew install postgresql@16

# veya sadece:
brew install postgresql
```

### 3. PostgreSQL'i PATH'e Ekleyin
```bash
# .zshrc veya .bash_profile dosyanıza ekleyin:
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc

# Intel Mac kullanıyorsanız:
echo 'export PATH="/usr/local/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc

# Değişiklikleri uygulayın
source ~/.zshrc
```

---

## 🚀 PostgreSQL Başlatma ve Durdurma

### Otomatik Başlatma (Önerilen)
```bash
# PostgreSQL'i sistem açılışında otomatik başlat
brew services start postgresql@16

# veya:
brew services start postgresql
```

### Manuel Başlatma
```bash
# Foreground'da başlat (terminal kapanınca durur)
pg_ctl -D /opt/homebrew/var/postgresql@16 start

# Intel Mac için:
pg_ctl -D /usr/local/var/postgresql@16 start
```

### PostgreSQL Durumunu Kontrol Etme
```bash
# Servis durumunu kontrol et
brew services info postgresql@16

# veya
pg_isready
```

### PostgreSQL'i Durdurma
```bash
# Servisi durdur
brew services stop postgresql@16

# veya manuel durdurma
pg_ctl -D /opt/homebrew/var/postgresql@16 stop
```

---

## 💾 Veritabanı Oluşturma

### 1. PostgreSQL Shell'e Bağlanın
```bash
# Varsayılan postgres kullanıcısı ile bağlan
psql postgres
```

### 2. Kullanıcı ve Veritabanı Oluşturun
```sql
-- Yeni bir kullanıcı oluştur (şifre ile)
CREATE USER postgres WITH PASSWORD 'postgres';

-- Kullanıcıya superuser yetkisi ver
ALTER USER postgres WITH SUPERUSER;

-- Proje için veritabanı oluştur
CREATE DATABASE target_db;

-- Veritabanı sahibini ayarla
ALTER DATABASE target_db OWNER TO postgres;

-- Bağlantıları kontrol et
\l

-- Çıkış
\q
```

### 3. Alternatif: Komut Satırından Oluşturma
```bash
# Kullanıcı oluştur
createuser -s postgres

# Veritabanı oluştur
createdb -U postgres target_db
```

---

## ✅ Bağlantı Testi

### 1. psql ile Test
```bash
# Yeni oluşturduğunuz veritabanına bağlanın
psql -U postgres -d target_db -h localhost -p 5432

# Şifre istendiğinde: postgres
```

### 2. Python ile Test
```bash
# Python psycopg kütüphanesini kullanarak test
python3 << EOF
import psycopg

try:
    conn = psycopg.connect(
        "postgresql://postgres:postgres@localhost:5432/target_db"
    )
    print("✅ PostgreSQL bağlantısı başarılı!")
    conn.close()
except Exception as e:
    print(f"❌ Bağlantı hatası: {e}")
EOF
```

### 3. Bağlantı Bilgileri
Projenizde kullanılacak bağlantı string'i:
```
postgresql://postgres:postgres@localhost:5432/target_db
```

Parametreler:
- **Host**: `localhost` (127.0.0.1)
- **Port**: `5432` (PostgreSQL varsayılan port)
- **Kullanıcı**: `postgres`
- **Şifre**: `postgres`
- **Veritabanı**: `target_db`

---

## 🔧 Sık Karşılaşılan Sorunlar

### ❌ Sorun 1: "psql: command not found"
**Çözüm:**
```bash
# PATH'i kontrol edin
echo $PATH

# PostgreSQL PATH'i tekrar ekleyin
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

# Kalıcı yapmak için .zshrc'ye ekleyin
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### ❌ Sorun 2: "could not connect to server"
**Çözüm:**
```bash
# PostgreSQL çalışıyor mu kontrol edin
brew services list | grep postgresql

# Çalışmıyorsa başlatın
brew services start postgresql@16

# Port'un kullanımda olup olmadığını kontrol edin
lsof -i :5432
```

### ❌ Sorun 3: "authentication failed"
**Çözüm:**
```bash
# pg_hba.conf dosyasını bulun
locate pg_hba.conf

# veya
find /opt/homebrew/var/postgresql* -name pg_hba.conf

# Dosyayı düzenleyin (trust veya md5 kullanın)
# local   all   all   trust
# host    all   all   127.0.0.1/32   md5

# PostgreSQL'i yeniden başlatın
brew services restart postgresql@16
```

### ❌ Sorun 4: "Port 5432 already in use"
**Çözüm:**
```bash
# Hangi process port'u kullanıyor?
lsof -i :5432

# Process'i sonlandırın
kill -9 <PID>

# veya farklı bir port kullanın (postgresql.conf)
# port = 5433
```

### ❌ Sorun 5: "FATAL: database does not exist"
**Çözüm:**
```bash
# Veritabanını oluşturun
createdb -U postgres target_db

# veya psql ile
psql postgres -c "CREATE DATABASE target_db;"
```

---

## 📊 PostgreSQL Yönetimi

### Veritabanlarını Listeleme
```bash
psql postgres -c "\l"
```

### Kullanıcıları Listeleme
```bash
psql postgres -c "\du"
```

### Veritabanı Silme (Dikkatli!)
```bash
dropdb target_db
```

### Veritabanı Yedekleme
```bash
pg_dump -U postgres target_db > backup.sql
```

### Veritabanı Geri Yükleme
```bash
psql -U postgres target_db < backup.sql
```

---

## 🎯 Proje İçin Dikkat Edilecekler

### 1. ✅ Bağlantı String Formatı
```python
# Doğru format
postgresql://postgres:postgres@localhost:5432/target_db

# Yanlış formatlar (Docker hostname'leri)
postgresql://postgres:postgres@postgres:5432/target_db  # ❌
mongodb://mongodb:27017  # ❌
```

### 2. ✅ .env Dosyası Ayarları
```bash
# backend/.env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="postgrator_db"
```

### 3. ✅ Firewall ve Güvenlik
- PostgreSQL sadece localhost'tan erişime açık olmalı
- Güçlü şifreler kullanın (production'da)
- pg_hba.conf'u güvenlik için yapılandırın

### 4. ✅ Performans
```bash
# PostgreSQL yapılandırmasını optimize edin
# /opt/homebrew/var/postgresql@16/postgresql.conf

shared_buffers = 256MB          # RAM'in %25'i
effective_cache_size = 1GB       # RAM'in %50-75'i
work_mem = 16MB
maintenance_work_mem = 128MB
```

---

## 📚 Faydalı Komutlar

```bash
# PostgreSQL versiyonu
psql --version
postgres --version

# Aktif bağlantıları görüntüleme
psql postgres -c "SELECT * FROM pg_stat_activity;"

# Veritabanı boyutu
psql postgres -c "SELECT pg_size_pretty(pg_database_size('target_db'));"

# Cache temizleme
psql postgres -c "SELECT pg_stat_reset();"
```

---

## 🆘 Yardım ve Dokümantasyon

- **PostgreSQL Resmi Dokümantasyon**: https://www.postgresql.org/docs/
- **Homebrew PostgreSQL**: `brew info postgresql@16`
- **psql Yardım**: `\?` (psql içinde)
- **SQL Yardım**: `\h` (psql içinde)

---

## ✨ Özet Kurulum Komutları

```bash
# 1. PostgreSQL Kurulumu
brew install postgresql@16

# 2. PATH Ayarı
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 3. PostgreSQL Başlatma
brew services start postgresql@16

# 4. Veritabanı Oluşturma
psql postgres << EOF
CREATE USER postgres WITH PASSWORD 'postgres' SUPERUSER;
CREATE DATABASE target_db OWNER postgres;
EOF

# 5. Bağlantı Testi
psql -U postgres -d target_db -h localhost -p 5432
```

**✅ Kurulum Tamamlandı!** Artık projenizi local olarak çalıştırabilirsiniz.
