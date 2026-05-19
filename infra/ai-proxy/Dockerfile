FROM nginx:alpine

# Copy the configuration template
COPY ai-proxy.conf /etc/nginx/conf.d/default.conf.template

# Use envsubst to replace the OLLAMA_URL at runtime
# Cloud Run sets PORT environment variable, so we must listen on it.
CMD ["sh", "-c", "envsubst '$OLLAMA_URL $OLLAMA_HOST_HEADER $PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
