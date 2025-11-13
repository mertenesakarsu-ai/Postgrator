# .bak Dosyası Migration Sorunu Çözümü

## Sorun Neydi?

Kullanıcı local'de çalıştırırken .bak dosyası yükleyip migration başlattığında:
- Migration %0'da kalıyordu
- WebSocket bağlantısı kesiliyor ve hata veriyordu:
  ```
  WebSocket error: received 1001 (going away); then sent 1001 (going away)
  ```

## Kök Neden

Local setup'ta backend local filesystem'de çalışırken, MSSQL Docker container içinde çalışıyor.

**Sorun:** Upload edilen .bak dosyası backend'in local filesystem'ine kaydediliyordu (`/app/backend/backups/`), ancak Docker container içindeki MSSQL bu dosyayı göremiyordu!

MSSQL `RESTORE DATABASE FROM DISK = '/app/backend/backups/xxx.bak'` komutunu çalıştırdığında, Docker container içinde o yol mevcut olmadığı için hata veriyordu.

## Çözüm

### 1. Otomatik Docker Kopyalama (`upload_service.py`)

.bak dosyası upload edildikten sonra otomatik olarak Docker container'a kopyalanıyor:

```python
# Local'e kaydet
await save_to_local(file_path)

# Docker container'a kopyala
docker cp /app/backend/backups/xxx.bak postgrator_mssql:/var/opt/mssql/backup/xxx.bak
```

### 2. Docker Yolu Kullanımı (`migration_service.py`)

Migration işlemi Docker içindeki yolu kullanıyor:

```python
# Eskisi: /app/backend/backups/xxx.bak
# Yenisi: /var/opt/mssql/backup/xxx.bak
docker_bak_path = upload_service.get_docker_backup_path(job_id)
await mssql_service.verify_backup(docker_bak_path)
await mssql_service.restore_database(docker_bak_path, logical_files)
```

### 3. Container Kontrolü

Docker container'ın çalıştığını kontrol eden mekanizma eklendi:

```python
# Container çalışıyor mu kontrol et
docker ps --filter name=postgrator_mssql

# Çalışmıyorsa açık hata mesajı ver
if not running:
    raise Exception("MSSQL Docker container çalışmıyor. Lütfen 'docker ps' ile kontrol edin.")
```

### 4. Daha İyi Error Handling

- Migration sırasında oluşan hatalar artık düzgün yakalanıyor
- WebSocket üzerinden kullanıcıya iletiliyor
- Backend loglarına detaylı kayıt düşülüyor

## Test Etmek İçin

### 1. MSSQL Docker Container'ını Başlatın

```bash
# Docker Compose ile
docker-compose up -d mssql

# Veya manuel
docker run -d \
  --name postgrator_mssql \
  -e 'ACCEPT_EULA=Y' \
  -e 'SA_PASSWORD=YourStrong!Passw0rd' \
  -e 'MSSQL_PID=Developer' \
  -p 1433:1433 \
  -v $(pwd)/backups:/var/opt/mssql/backup \
  mcr.microsoft.com/mssql/server:2022-latest
```

### 2. Container'ın Çalıştığını Doğrulayın

```bash
docker ps | grep postgrator_mssql
```

Çıktı:
```
CONTAINER ID   IMAGE                                        STATUS
xxxxxxxxxxxxx  mcr.microsoft.com/mssql/server:2022-latest   Up 2 minutes
```

### 3. Backend ve Frontend'i Başlatın

```bash
./start-local.sh
```

### 4. .bak Dosyası Yükleyin

1. Tarayıcıda http://localhost:3000 açın
2. .bak dosyasını seçin
3. PostgreSQL connection string girin
4. "Import" butonuna tıklayın

### 5. Logları İzleyin

Terminal 1 - Backend logs:
```bash
tail -f backend.log
```

Terminal 2 - Docker logs:
```bash
docker logs -f postgrator_mssql
```

## Başarı Göstergeleri

✅ .bak dosyası upload ediliyor
✅ Docker container'a otomatik kopyalanıyor
✅ Migration %0'dan ilerliyor
✅ WebSocket bağlantısı açık kalıyor
✅ Progress güncellemeleri geliyor
✅ Tablolar başarıyla migrate ediliyor

## Hata Senaryoları ve Çözümleri

### "MSSQL Docker container çalışmıyor" Hatası

**Çözüm:**
```bash
docker start postgrator_mssql
```

### "Docker komutu bulunamadı" Hatası

**Çözüm:** Docker'ı yükleyin veya başlatın:
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

### "Permission denied" Hatası

**Çözüm:** Docker'a erişim izni ekleyin:
```bash
# Linux
sudo usermod -aG docker $USER
# Logout/login gerekebilir
```

## Detaylı Dokümanlar

- [LOCAL_MSSQL_DOCKER.md](./LOCAL_MSSQL_DOCKER.md) - MSSQL Docker kurulum detayları
- [start-local.sh](./start-local.sh) - Local başlatma scripti
- [stop-local.sh](./stop-local.sh) - Local durdurma scripti

## Özet

Sorun çözüldü! Artık local setup'ta .bak dosyaları yüklenip migration yapılabilir. Sistem otomatik olarak:
1. Dosyayı local'e kaydeder
2. Docker container'a kopyalar
3. Docker içindeki yolu kullanarak migration yapar
4. Progress güncellemelerini WebSocket üzerinden iletir
