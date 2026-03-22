#!/bin/bash
set -e

echo "Generating runtime config..."
cat > /app/frontend/config.js << EOF
window.RUNTIME_CONFIG = {
  API_URL: '${API_URL:-}'
};
EOF

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec gunicorn server.wsgi:application --bind 0.0.0.0:80 --workers 2
