# Postgrator Test Instructions

## Test Ortamı

Bu uygulama şu anda development ortamında çalışmaktadır. Gerçek bir .bak dosyası ile test etmek için aşağıdaki adımları izleyin.

## Ön Hazırlık

### 1. Docker Servislerini Başlat

```bash
docker-compose up -d
```

Bu komut şunları başlatır:
- MSSQL Server (localhost:1433)
- PostgreSQL (localhost:5432)

### 2. Servislerin Hazır Olmasını Bekle

```bash
# MSSQL health check
docker-compose ps

# PostgreSQL bağlantı testi
docker exec -it postgres_target psql -U postgres -c "SELECT version();"
```

## Test Senaryosu

### Senaryo 1: Küçük Test Database

1. **Küçük bir SQL Server veritabanı oluştur**

```sql
USE master;
CREATE DATABASE TestDB;
GO

USE TestDB;

-- Test tablosu
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY IDENTITY(1,1),
    Name NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100),
    CreatedAt DATETIME DEFAULT GETDATE()
);

CREATE TABLE Orders (
    OrderID INT PRIMARY KEY IDENTITY(1,1),
    CustomerID INT NOT NULL,
    OrderDate DATETIME DEFAULT GETDATE(),
    TotalAmount DECIMAL(10,2),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- Test verisi
INSERT INTO Customers (Name, Email) VALUES 
    ('Ali Yılmaz', 'ali@example.com'),
    ('Ayşe Demir', 'ayse@example.com'),
    ('Mehmet Kaya', 'mehmet@example.com');

INSERT INTO Orders (CustomerID, OrderDate, TotalAmount) VALUES
    (1, GETDATE(), 150.50),
    (1, GETDATE(), 200.00),
    (2, GETDATE(), 75.25),
    (3, GETDATE(), 300.00);
```

2. **Backup Oluştur**

```sql
BACKUP DATABASE TestDB 
TO DISK = '/var/opt/mssql/backup/testdb.bak'
WITH FORMAT, INIT;
```

3. **Web Arayüzünde Test Et**

- https://pgsql-debugger.preview.emergentagent.com adresine git
- `testdb.bak` dosyasını yükle
- PostgreSQL URI: `postgresql://postgres:postgres@localhost:5432/target_db`
- "Migrasyonu Başlat"a tıkla
- İlerlemeyi izle

4. **Sonuçları Doğrula**

PostgreSQL'de kontrol:
```bash
docker exec -it postgres_target psql -U postgres target_db

# Tabloları listele
\dt public.*

# Verileri kontrol et
SELECT * FROM public.customers;
SELECT * FROM public.orders;

# Foreign key kontrolü
\d public.orders
```

## Beklenen Sonuçlar

✅ 2 tablo (customers, orders)
✅ 3 müşteri, 4 sipariş
✅ Primary key'ler kurulu
✅ Foreign key ilişkisi kurulu
✅ Veri tipleri doğru eşlenmiş

## Manuel Fonksiyon Testleri

### 1. Upload Formu
- ✓ File input çalışıyor
- ✓ PostgreSQL URI validation
- ✓ Schema input (default: public)
- ✓ Submit butonu disabled state

### 2. Progress View
- ✓ WebSocket bağlantısı
- ✓ Stage progression
- ✓ Real-time log streaming
- ✓ Table progress updates

### 3. Results View
- ✓ Özet istatistikler (tablo/satır/süre)
- ✓ Artifact indirme (schema.sql, rowcount.csv, errors.log)
- ✓ Tablo listesi
- ✓ Paginated veri görüntüleme

## Known Limitations

1. **Dosya Boyutu**: 50 GB limit (config ile değiştirilebilir)
2. **Concurrent Jobs**: Tek job (production için queue eklenebilir)
3. **Complex Types**: XML, GEOMETRY gibi özel tipler basit mapping
4. **Computed Columns**: Kopyalanmaz (manual eklenmeli)
5. **Triggers/Procedures**: Kopyalanmaz (manual migration gerekli)

## Troubleshooting

### Problem: "ODBC Driver not found"
**Çözüm:**
```bash
apt-get install msodbcsql18 unixodbc-dev
```

### Problem: "PostgreSQL connection failed"
**Çözüm:**
- URI formatını kontrol et
- PostgreSQL servisinin çalıştığından emin ol
- Firewall kurallarını kontrol et

### Problem: "Disk space error"
**Çözüm:**
```bash
df -h
rm -rf /app/backups/*
rm -rf /app/artifacts/*
```

## Production Deployment Checklist

- [ ] Environment variables güvenli şekilde saklanıyor
- [ ] File upload size limit production'a uygun
- [ ] Database backup stratejisi var
- [ ] Monitoring ve logging kurulu
- [ ] Error handling ve retry mekanizması test edildi
- [ ] WebSocket reconnection logic test edildi
- [ ] Large file handling test edildi (>10GB)
- [ ] Concurrent user scenarios test edildi

---

**Not**: Bu doküman test ve development amaçlıdır. Production kullanımı için ek güvenlik ve performans optimizasyonları gerekebilir.
