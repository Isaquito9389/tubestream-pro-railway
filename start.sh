#!/bin/sh
# ============================================================
# TubeStream Pro — Point d'entrée Railway / Docker
# ============================================================
# Pourquoi ce script existe :
#   Railway scanne STATIQUEMENT le Procfile et le CMD du Dockerfile
#   pour trouver le port à exposer. Il ne sait pas interpréter
#   $PORT ou ${PORT:-5000} et renvoie :
#       Error: '$PORT' is not a valid port number.
#
#   En mettant la résolution de $PORT DANS ce script shell,
#   Railway ne voit que "/app/start.sh" comme commande — aucun
#   $PORT visible statiquement — et le shell fait la substitution
#   au moment où le conteneur démarre réellement.
# ============================================================
set -e

# Railway injecte $PORT (ex: 5000, 8080...). Fallback 5000 pour run local.
PORT="${PORT:-5000}"

echo "==> TubeStream Pro démarrage sur le port $PORT"
which deno && deno --version || echo "DENO INTROUVABLE"
if [ -n "$COOKIES_B64" ]; then
  echo "$COOKIES_B64" | base64 -d > /app/cookies.txt
  export COOKIES_FILE=/app/cookies.txt
  echo "==> Cookies YouTube chargés"
fi

exec gunicorn app:app \
    --bind "0.0.0.0:${PORT}" \
    --timeout 300 \
    --workers 4 \
    --threads 2 \
    --keep-alive 120 \
    --access-logfile - \
    --error-logfile -
