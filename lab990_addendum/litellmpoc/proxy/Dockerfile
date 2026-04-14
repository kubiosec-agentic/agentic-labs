FROM docker.litellm.ai/berriai/litellm:main-latest

# Copy custom callback module into the app directory
COPY custom_callbacks.py /app/custom_callbacks.py

# Copy proxy config
COPY config.yaml /app/config.yaml

EXPOSE 4000

CMD ["--config", "/app/config.yaml", "--detailed_debug"]
