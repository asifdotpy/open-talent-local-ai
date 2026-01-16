# Desktop App Deployment Guide

## System Requirements

### Minimum Requirements
- **RAM**: 8GB (16GB recommended for running all 15 microservices + desktop app)
- **Storage**: 10GB free disk space
- **OS**: Ubuntu 20.04+ (WSL2 or native Linux)
- **CPU**: 4 cores (8+ recommended)

### For Low RAM Devices
If you have limited RAM (< 8GB), consider:
1. Running only essential services (see Production Mode below)
2. Deploying microservices on a separate server
3. Using cloud deployment for heavy services (granite-interview, candidate-service)

---

## Quick Start - New Device Setup

### 1. Prerequisites Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js via nvm (IMPORTANT: Must use WSL-native node, not Windows)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20

# Verify installations
python3 --version  # Should be 3.10+
node --version     # Should be v20.x.x
npm --version      # Should be 10.x.x
```

### 2. Clone Repository

```bash
git clone https://github.com/asifdotpy/open-talent-local-ai.git
cd open-talent-local-ai
```

### 3. Python Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv-1
source .venv-1/bin/activate

# Install dependencies (this may take 10-15 minutes)
pip install --upgrade pip
pip install -r requirements.txt

# Verify services can import dependencies
cd services/user-service && python -c "import fastapi; print('✓ FastAPI OK')" && cd ../..
```

### 4. Desktop App Setup

```bash
cd desktop-app

# Clean install (CRITICAL for WSL users)
rm -rf node_modules package-lock.json
npm cache clean --force

# Install dependencies (use --legacy-peer-deps if needed)
npm install --legacy-peer-deps

# Create .npmrc to force WSL bash (CRITICAL FIX)
cat > .npmrc << 'EOF'
# CRITICAL: Force npm to use bash for scripts, not Windows CMD
script-shell=/bin/bash
EOF

# Create public directory with required files
mkdir -p public
cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="OpenTalent - Local AI Interview Platform" />
    <title>OpenTalent Desktop</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

cat > public/manifest.json << 'EOF'
{
  "short_name": "OpenTalent",
  "name": "OpenTalent Desktop - Local AI Interview Platform",
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}
EOF

cd ..
```

### 5. Environment Configuration

```bash
# Verify .env.shared exists
cat .env.shared  # Should show port configurations

# If missing, copy from template or contact repository maintainer
```

---

## Running OpenTalent

### Option A: Full Stack (Requires 8GB+ RAM)

```bash
# Start all services and desktop app
./manage.sh start

# Expected output: "🌟 OpenTalent is Ready for Demo! 🌟"
```

**Access Points**:
- Desktop App: http://localhost:3000
- API Gateway: http://localhost:8009
- Analytics: http://localhost:8007

### Option B: Production Mode (Lower RAM Usage)

Start only essential services:

```bash
# Start services individually
./manage.sh start

# Monitor which services are using most RAM
ps aux | grep python | sort -k4 -r | head -10

# Stop heavy services you don't need
# (granite-interview-service, candidate-service often use most RAM)
```

### Option C: Desktop App Only

If microservices are running elsewhere (cloud/separate server):

```bash
cd desktop-app

# Set API gateway URL in environment
export REACT_APP_API_URL=https://your-api-gateway.com

# Start desktop app standalone
npm run dev
```

---

## Troubleshooting

### Desktop App Won't Start

**Symptom**: `concurrently not found` or `CMD.EXE UNC paths not supported`

**Solution**:
```bash
cd desktop-app

# 1. Ensure you're using WSL npm, not Windows npm
which npm  # Should show /home/<user>/.nvm/..., NOT /mnt/c/Program Files/

# 2. Fix PATH priority if Windows npm appears first
export PATH="$HOME/.nvm/versions/node/v20.x.x/bin:$PATH"

# 3. Verify .npmrc exists with script-shell=/bin/bash
cat .npmrc

# 4. Test npm config
npm config get script-shell  # Should return: /bin/bash

# 5. Try standalone launch
npm run dev
```

### Out of Memory Errors

**Symptom**: Services crash or system freezes

**Solution**:
```bash
# Check memory usage
free -h

# Stop all services
./manage.sh stop

# Start only core services
# Edit manage.sh SERVICES array to comment out heavy services:
# - granite-interview-service (uses ~2GB during model load)
# - candidate-service (uses ~1.5GB for embeddings)

# Or increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Services Health Check Timeout

**Symptom**: `granite-interview-service health check timed out`

**Expected**: Heavy services may take 60-120 seconds to load models. This is normal.

**Verify**:
```bash
# Check if process is still running
./manage.sh status

# Check logs
tail -f logs/granite-interview-service.log
```

---

## WSL-Specific Notes

### Critical: Use WSL-Native Tools

❌ **DO NOT** use Windows npm/node from `/mnt/c/Program Files/`
✅ **DO** use WSL npm/node from `~/.nvm/` or `/usr/bin/`

### Verify Your Environment

```bash
# Check current npm location
which npm
readlink -f $(which npm)

# Should show WSL path, NOT Windows path
# ✓ Good: /home/asif1/.nvm/versions/node/v20.11.0/bin/npm
# ✗ Bad:  /mnt/c/Program Files/nodejs/npm
```

### Fix PATH Priority

If Windows tools appear first in PATH:

```bash
# Add to ~/.bashrc
echo 'export PATH="$HOME/.nvm/versions/node/$(nvm current)/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Cloud Deployment (Alternative)

For devices with limited resources, deploy microservices to cloud:

### Docker Deployment (Recommended)

```bash
# Each service has Dockerfile
cd services/user-service
docker build -t opentalent-user-service .
docker run -p 8001:8001 opentalent-user-service

# Or use docker-compose (if available)
docker-compose up -d
```

### Remote API Configuration

Update desktop app to use remote APIs:

```bash
# desktop-app/.env.local
REACT_APP_API_URL=https://api.your-opentalent.com
REACT_APP_GATEWAY_PORT=443
```

---

## Performance Tips

1. **Disable unused services** in manage.sh
2. **Use SSD** for better I/O performance
3. **Allocate swap space** (4GB+ recommended)
4. **Close browser tabs** before starting (Chrome/Firefox use significant RAM)
5. **Run services selectively** based on testing needs

---

## Support

- **Logs**: Check `logs/` directory for service-specific logs
- **Status**: Run `./manage.sh status` for health overview
- **GitHub Issues**: Report problems at repository issues page
- **Documentation**: See README.md and individual service README files

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./manage.sh start` | Start all services |
| `./manage.sh stop` | Stop all services |
| `./manage.sh restart` | Restart all services |
| `./manage.sh status` | Check service health |
| `./manage.sh logs <service>` | View service logs |
| `cd desktop-app && npm run dev` | Start desktop app standalone |

---

**Last Updated**: 2026-01-16
**Tested On**: WSL2 Ubuntu 22.04, 16GB RAM, 8-core CPU
