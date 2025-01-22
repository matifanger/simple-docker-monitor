FROM python:3.9-slim

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    sysstat \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Instalar docker CLI
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli

# Instalar dependencias de Python
RUN pip install psutil docker flask apscheduler python-dotenv

# Crear directorio de trabajo y templates
WORKDIR /app
RUN mkdir -p /app/templates

# Copiar archivos de la aplicación
COPY app.py /app/
COPY templates/index.html /app/templates/
COPY .env /app/

# Exponer el puerto
EXPOSE 3000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]