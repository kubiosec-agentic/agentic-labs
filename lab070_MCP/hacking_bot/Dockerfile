FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive

# Base deps
RUN apt-get update && apt-get install -y \
    curl git ca-certificates \
    python3 python3-pip python3-venv build-essential \
 && rm -rf /var/lib/apt/lists/*

# Node.js (LTS) + npm (npx is bundled)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
 && apt-get install -y nodejs

# Install uv (puts binaries in /root/.local/bin by default)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# Make uv/uvx visible
ENV PATH="/root/.local/bin:${PATH}"

# Sanity checks
RUN node -v && npm -v && npx -v \
 && python3 --version && pip3 --version \
 && uv --version && uvx --version

CMD ["bash"]
