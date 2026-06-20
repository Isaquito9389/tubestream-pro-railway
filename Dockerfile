# ============================================================
# TubeStream Pro — Dockerfile pour Railway / Render
# ============================================================
# Stratégie anti-erreur "invalid port number" sur Railway :
#   - Pas de Procfile (Railway le scanne statiquement).
#   - Pas de variable dans EXPOSE (utiliser un nombre littéral).
#   - Pas de variable dans la ligne CMD (Railway peut aussi la scanner).
#   - Toute la logique de résolution du port est cachée dans
#     /app/start.sh, exécutée par le shell à runtime.
# ============================================================
FROM python:3.11-slim

# System dependencies + ffmpeg for audio extraction
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get install -y --no-install-recommends curl unzip && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deno.land/install.sh | sh && \
    mv /root/.deno/bin/deno /usr/local/bin/deno
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /app

# Install Python dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code + startup script
COPY . .

# Make startup script executable
RUN chmod +x /app/start.sh

# Create required directories
RUN mkdir -p templates downloads static

# Runtime env (port is injected by Railway at runtime — do NOT hardcode it)
ENV DOWNLOAD_DIR=/app/downloads \
    FLASK_DEBUG=false \
    PYTHONUNBUFFERED=1

# Document the listening port (literal number — Railway ignores EXPOSE
# for routing, but a number avoids the "invalid port number" scan error)
EXPOSE 5000

# Run via startup script — port resolution happens inside the shell
CMD ["/app/start.sh"]
