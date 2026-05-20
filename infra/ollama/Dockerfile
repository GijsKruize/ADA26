FROM ollama/ollama:latest

# Set environment variables
ENV OLLAMA_HOST=0.0.0.0

# Pre-load the model
# We need to start the server, pull the model, then kill the server to bake it into the image
RUN ollama serve & sleep 5 && ollama pull llama3.1 && pkill ollama

EXPOSE 11434

ENTRYPOINT ["ollama", "serve"]
