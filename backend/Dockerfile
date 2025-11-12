FROM python:3.11-slim

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg2 \
    unixodbc unixodbc-dev \
    libpq5 libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Microsoft ODBC Driver 18 (Debian 12 / bookworm)
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
      | tee /etc/apt/sources.list.d/mssql-release.list > /dev/null && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

EXPOSE 8001

# Geliştirme için --reload; prod’da kaldır
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
