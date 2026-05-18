FROM nginx:alpine

# Copy static files
COPY frontend/index.html /usr/share/nginx/html/
COPY frontend/app.js /usr/share/nginx/html/
COPY frontend/style.css /usr/share/nginx/html/
COPY frontend/entrypoint.sh /usr/share/nginx/html/

# Make entrypoint.sh executable
RUN chmod +x /usr/share/nginx/html/entrypoint.sh

# Use entrypoint.sh to inject config.js
ENTRYPOINT ["/usr/share/nginx/html/entrypoint.sh"]
