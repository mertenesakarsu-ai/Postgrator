# Local MSSQL Docker Kurulumu

Bu kılavuz, sadece MSSQL için Docker kullanırken nasıl kurulum yapılacağını açıklar.

## 1. MSSQL Docker Container'ını Başlatma

### Manuel Başlatma:

```bash
docker run -d \
  --name postgrator_mssql \
  -e 'ACCEPT_EULA=Y' \
  -e 'SA_PASSWORD=YourStrong!Passw0rd' \
  -e 'MSSQL_PID=Developer' \
  -p 1433:1433 \
  -v $(pwd)/backups:/var/opt/mssql/backup \
  mcr.microsoft.com/mssql/server:2022-latest
```

### Docker Compose ile Sadece MSSQL:

```bash
docker-compose up -d mssql
```

## 2. Container'ın Çalıştığını Kontrol Edin

```bash
docker ps | grep postgrator_mssql
```

Çıktı şöyle olmalı:
```
CONTAINER ID   IMAGE                                        COMMAND                  STATUS        PORTS
xxxxxxxxxxxxx  mcr.microsoft.com/mssql/server:2022-latest  "/opt/mssql/bin/perm…"  Up 2 minutes  0.0.0.0:1433->1433/tcp
```

## 3. MSSQL Bağlantısını Test Edin

### SQLCmd ile (Container içinde):

```bash
docker exec -it postgrator_mssql /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong!Passw0rd' -C -Q 'SELECT @@VERSION'
```

### Python ile (Backend'den):

```python
import pyodbc
conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost,1433;DATABASE=master;UID=sa;PWD=YourStrong!Passw0rd;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)
print("Bağlantı başarılı!")
conn.close()
```

## 4. Backend ve Frontend'i Başlatın

```bash
./start-local.sh
```

## Önemli Notlar

1. **Port**: MSSQL Docker container'ı `1433` portundan erişilebilir olmalı
2. **Şifre**: SA şifresi `YourStrong!Passw0rd` (veya backend/.env'deki değer)
3. **Backup Dizini**: Upload edilen .bak dosyaları otomatik olarak Docker container'a kopyalanır
4. **Container İsmi**: Container ismi `postgrator_mssql` olmalı (farklıysa backend/.env'de `MSSQL_CONTAINER` değişkenini ayarlayın)

## Sorun Giderme

### "MSSQL Docker container çalışmıyor" Hatası

Container'ı başlatın:
```bash
docker start postgrator_mssql
```

Veya yeniden oluşturun:
```bash
docker rm postgrator_mssql
# Yukarıdaki docker run komutunu tekrar çalıştırın
```

### "Docker'a kopyalama başarısız" Hatası

1. Docker servisinin çalıştığından emin olun:
   ```bash
   docker ps
   ```

2. Container isminin doğru olduğunu kontrol edin:
   ```bash
   docker ps --filter "name=postgrator"
   ```

3. Backend/.env dosyasında `MSSQL_CONTAINER` değişkenini doğru container ismine ayarlayın

### Container Çalışmıyor

Logları kontrol edin:
```bash
docker logs postgrator_mssql
```

Health check yapın:
```bash
docker exec postgrator_mssql /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong!Passw0rd' -C -Q 'SELECT 1'
```

## Container'ı Durdurmak

```bash
docker stop postgrator_mssql
```

## Container'ı Kaldırmak

```bash
docker stop postgrator_mssql
docker rm postgrator_mssql
```

---

**Not**: Bu yapılandırma development/test ortamları içindir. Production kullanımı için ek güvenlik önlemleri alınmalıdır.
