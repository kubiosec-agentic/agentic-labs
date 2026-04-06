![Bash](https://img.shields.io/badge/Bash-grey) ![Docker](https://img.shields.io/badge/Docker-blue) ![Python](https://img.shields.io/badge/Python-blue)

# LAB000: Environment Setup

## Introduction

This lab prepares your machine for the entire Agentic-Labs training. It installs core dependencies (Python 3.12, Docker, Node.js, common CLI tools), then distributes per-lab helper scripts (`lab_setup.sh` / `lab_cleanup.sh`) into every lab directory so that each subsequent lab can bootstrap its own virtual environment.

Run this lab **once** before starting any other lab.

## Set up your environment

### Prerequisites
- Ubuntu VM (T2.medium, 50 GB root volume) **or** macOS
- SSH access with the provided key
- Internet connectivity for package downloads

### Setup Commands

#### Step 1 — Connect to your VM

Open **Terminal 1** with port forwarding for the tools used across labs:
```bash
ssh -i agentics-key.pem -L 8080:localhost:8080 \
               -L 8081:localhost:8081 \
               -L 8000:localhost:8000 \
               -L 5000:localhost:5000 \
               -L 8501:localhost:8501 \
                ubuntu@x.x.x.x
```

#### Step 2 — Clone the repository
```bash
git clone https://github.com/kubiosec-agentic/agentic-labs.git
```
```bash
cd agentic-labs/lab000_setup/
```

#### Step 3 — Run the host setup script

This installs system-wide dependencies:
```bash
./setup.sh
```

**What `setup.sh` installs:**
- System tools: `jq`, `net-tools`, `curl`, `git`, `wget`, `vim`
- Python 3.12, pip, and venv support
- Node.js / npm
- Docker Engine (with current user added to the `docker` group)

#### Step 4 — Distribute lab helper scripts

This copies the bootstrap scripts (`lab_setup.sh` and `lab_cleanup.sh`) into every lab directory:
```bash
./prepare_labs.sh
```

#### Step 5 — Return to the repo root
```bash
cd ..
```

You are now ready to start **lab004** and beyond.

### Opening additional terminals

Several labs require multiple terminals (e.g. running an MCP server in one terminal and an agent in another). Open extra sessions without port forwarding:
```bash
ssh -i agentics-key.pem  ubuntu@x.x.x.x
```

## Lab instructions

### How per-lab setup works

Every lab directory receives two scripts from the `bootstrap/` folder:

**`lab_setup.sh`** — run at the start of each lab:
- Derives the virtual environment name from the folder (e.g. `.lab010`)
- Creates a Python venv and installs `requirements.txt` if present
- Prints activation instructions

**`lab_cleanup.sh`** — run at the end of each lab:
- Removes the virtual environment directory
- Reminds you to `deactivate` first

The typical per-lab workflow is:
```bash
cd lab010_ChatCompletion/
export OPENAI_API_KEY="xxxxxxxxx"
./lab_setup.sh
source .lab010/bin/activate

# ... do the lab ...

deactivate
./lab_cleanup.sh
cd ..
```

### File structure
```
lab000_setup/
├── setup.sh           # One-time host setup (Python, Docker, npm, tools)
├── prepare_labs.sh    # Copies bootstrap scripts into all lab directories
└── bootstrap/
    ├── lab_setup.sh   # Per-lab venv creation (distributed to every lab)
    └── lab_cleanup.sh # Per-lab venv removal  (distributed to every lab)
```

## Cleanup environment

This lab has no virtual environment to clean up. If you ever need to re-run the bootstrap distribution:
```bash
cd lab000_setup/
./prepare_labs.sh
cd ..
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
