# 🔌 PostgreSQL Bağlantı Kılavuzu

## ⚡ Hızlı Başlangıç

### Docker İçinde (Localhost)
Docker Compose ile çalıştırırken kullanın:
```
postgresql://postgres:postgres@localhost:5432/target_db
```

**Not:** Backend otomatik olarak `localhost`'u `postgres` container adına dönüştürür.

## 🎯 Bağlantı URI Formatı

```
postgresql://[kullanıcı]:[şifre]@[host]:[port]/[veritabanı]
```

### Parametreler

| Parametre | Açıklama | Örnek |
|-----------|----------|-------|
| **kullanıcı** | PostgreSQL kullanıcı adı | `postgres` |
| **şifre** | Kullanıcı şifresi | `postgres` |
| **host** | Sunucu adresi | `localhost` veya `postgres` |
| **port** | Port numarası | `5432` |
| **veritabanı** | Hedef veritabanı adı | `target_db` |

## 📋 Farklı Senaryolar

### 1️⃣ Docker Compose ile Localhost
```bash
postgresql://postgres:postgres@localhost:5432/target_db
```
**Veya:**
```bash
postgresql://postgres:postgres@postgres:5432/target_db
```

### 2️⃣ Harici PostgreSQL Sunucusu
```bash
postgresql://myuser:mypassword@192.168.1.100:5432/production_db
```

### 3️⃣ Cloud PostgreSQL (AWS RDS, Azure, etc.)
```bash
postgresql://admin:SecurePass123@mydb.abcdef.us-east-1.rds.amazonaws.com:5432/maindb
```

### 4️⃣ SSL Bağlantısı
```bash
postgresql://user:pass@host:5432/db?sslmode=require
```

## ✅ Bağlantı Kontrolü

### Docker Container İçinden Test
```bash
# Backend container'a gir
docker exec -it postgrator_backend bash

# PostgreSQL'e bağlan
psql postgresql://postgres:postgres@postgres:5432/target_db

# Veya Python ile test
python3 -c "import psycopg; conn = psycopg.connect('postgresql://postgres:postgres@postgres:5432/target_db'); print('OK')"
```

### Host'tan Test (Docker Compose çalışırken)
```bash
# psql kurulu ise
psql postgresql://postgres:postgres@localhost:5432/target_db

# veya Python ile
python3 -c "import psycopg; conn = psycopg.connect('postgresql://postgres:postgres@localhost:5432/target_db'); print('OK')"
```

## 🚨 Yaygın Hatalar ve Çözümleri

### 1. "password authentication failed"

**Sebep:** Yanlış kullanıcı adı veya şifre

**Çözüm:**
```bash
# Docker Compose'daki şifreyi kontrol edin
docker-compose exec postgres psql -U postgres -c "SELECT 1"

# Şifre değiştirme (gerekirse)
docker-compose exec postgres psql -U postgres -c "ALTER USER postgres PASSWORD 'yeni_sifre';"
```

### 2. "connection refused" veya "could not translate host name"

**Sebep:** Yanlış host adı

**Çözüm:**
- Docker içinden: `postgres` (servis adı)
- Host'tan: `localhost` veya `127.0.0.1`

### 3. "FATAL: database does not exist"

**Sebep:** Belirtilen veritabanı yok

**Çözüm:**
```bash
# Veritabanı oluştur
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE target_db;"

# Mevcut veritabanlarını listele
docker-compose exec postgres psql -U postgres -c "\l"
```

### 4. "connection timeout"

**Sebep:** PostgreSQL servisi çalışmıyor veya ulaşılamıyor

**Çözüm:**
```bash
# Container durumunu kontrol et
docker-compose ps postgres

# PostgreSQL loglarını kontrol et
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

## 🔧 Docker Compose Yapılandırması

### Varsayılan PostgreSQL Ayarları

`docker-compose.yml` içinde:
```yaml
postgres:
  image: postgres:16
  environment:
    - POSTGRES_USER=postgres        # Kullanıcı
    - POSTGRES_PASSWORD=postgres    # Şifre
    - POSTGRES_DB=target_db         # Varsayılan DB
  ports:
    - "5432:5432"                   # Port mapping
```

### Özel Ayarlar

Farklı kullanıcı/şifre kullanmak için `docker-compose.yml`'i düzenleyin:
```yaml
postgres:
  environment:
    - POSTGRES_USER=myuser
    - POSTGRES_PASSWORD=mypassword
    - POSTGRES_DB=mydb
```

**Sonra URI'yi güncelleyin:**
```
postgresql://myuser:mypassword@localhost:5432/mydb
```

## 🔒 Güvenlik Notları

### Development (Localhost)
✅ Basit şifreler kullanılabilir (`postgres:postgres`)
✅ Port 5432 açık olabilir

### Production
❌ Güçlü şifreler kullanın
❌ Portları sınırlandırın
✅ SSL kullanın (`sslmode=require`)
✅ Firewall kuralları uygulayın
✅ Veritabanı şifrelerini environment variable'larda saklayın

## 📚 PostgreSQL URI Seçenekleri

Gelişmiş parametreler ekleyebilirsiniz:

```bash
postgresql://user:pass@host:5432/db?sslmode=require&connect_timeout=10&application_name=postgrator
```

| Parametre | Açıklama | Değerler |
|-----------|----------|----------|
| `sslmode` | SSL bağlantı modu | `disable`, `allow`, `prefer`, `require` |
| `connect_timeout` | Bağlantı timeout (saniye) | `10`, `30` |
| `application_name` | Uygulama adı | Herhangi bir string |

## ✨ Best Practices

1. **Test Edilmiş URI Kullanın**
   ```bash
   # Önce test edin
   psql postgresql://user:pass@host:5432/db -c "SELECT 1"
   ```

2. **Doğru Veritabanını Seçin**
   - Migration için boş veya test DB kullanın
   - Production DB'ye dikkatli olun

3. **Yedekleme**
   - Hedef veritabanını yedekleyin
   ```bash
   pg_dump -U postgres target_db > backup.sql
   ```

4. **Şema Kontrolü**
   - Hedef şemanın boş olduğundan emin olun
   - Tablo isim çakışmaları kontrol edin

## 🆘 Yardım

Bağlantı sorunları yaşıyorsanız:

1. **Container'ları kontrol edin:**
   ```bash
   docker-compose ps
   ```

2. **PostgreSQL loglarını inceleyin:**
   ```bash
   docker-compose logs postgres
   ```

3. **Network bağlantısını test edin:**
   ```bash
   docker-compose exec backend ping postgres
   ```

4. **Manuel bağlantı deneyin:**
   ```bash
   docker-compose exec backend psql postgresql://postgres:postgres@postgres:5432/target_db
   ```

Sorun devam ederse `LOCALHOST_KURULUM.md` dosyasındaki sorun giderme bölümüne bakın.
