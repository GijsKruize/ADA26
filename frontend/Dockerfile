FROM nginx:alpine

# Copy static files
COPY . /usr/share/nginx/html/

# Remove the Dockerfile and other non-static files from the web root
RUN rm /usr/share/nginx/html/Dockerfile

# Make entrypoint.sh executable
RUN chmod +x /usr/share/nginx/html/entrypoint.sh

# Use entrypoint.sh to inject config.js
ENTRYPOINT ["/usr/share/nginx/html/entrypoint.sh"]
