#!/bin/bash
set -e

echo "Generating runtime config..."
cat > /usr/share/nginx/html/config.js << EOF
window.RUNTIME_CONFIG = {
  API_URL: '${API_URL:-}'
};
EOF

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
