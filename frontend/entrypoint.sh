#!/bin/sh
echo "window.API_BASE = '${API_GATEWAY_URL}';" > /usr/share/nginx/html/config.js
exec nginx -g 'daemon off;'
