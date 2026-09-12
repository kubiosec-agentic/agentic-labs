FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Kept intentionally small so the image builds fast and does not OOM a small
# cloud instance. desktop-commander + supergateway are Node; the agent
# apt-installs its own scanners (e.g. nikto) at runtime. This is a throwaway
# container, so if a task needs build-essential / uv / anything else, install
# it inside the container at runtime rather than baking it into every build.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git ca-certificates \
    python3 python3-pip python3-venv \
 && rm -rf /var/lib/apt/lists/*

# Node.js (LTS) + npm (npx is bundled)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && rm -rf /var/lib/apt/lists/*

# Sanity checks
RUN node -v && npm -v && npx -v && python3 --version && pip3 --version

CMD ["bash"]
