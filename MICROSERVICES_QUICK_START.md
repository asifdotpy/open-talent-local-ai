# Microservices Quick Start Guide

**Last Updated**: December 13, 2025  
**Status**: ✅ All services tested and ready

---

## 🚀 Quick Start

### Option 1: Run All Services at Once (Docker Compose)

```bash
cd /home/asif1/open-talent/microservices
docker-compose up
```

Services will be available at:
- Scout Service: http://localhost:8000
- Interview Service: http://localhost:8001
- Conversation Service: http://localhost:8002
- Voice Service: http://localhost:8003
- Avatar Service: http://localhost:8004
- User Service: http://localhost:8005
- Candidate Service: http://localhost:8006
- Analytics Service: http://localhost:8007
- Desktop Integration: http://localhost:8009

---

### Option 2: Run Services Individually

#### 1. Scout Service (Port 8000)
```bash
cd /home/asif1/open-talent/microservices/scout-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
Access: http://localhost:8000/docs

#### 2. Conversation Service (Port 8002)
```bash
cd /home/asif1/open-talent/microservices/conversation-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
Access: http://localhost:8002/docs

#### 3. Interview Service (Port 8001)
```bash
cd /home/asif1/open-talent/microservices/interview-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
Access: http://localhost:8001/docs

#### 4. Desktop Integration Service (Port 8009)
```bash
cd /home/asif1/open-talent/microservices/desktop-integration-service
chmod +x start.sh
./start.sh
```
Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009
```
Access: http://localhost:8009/docs

#### 5. User Service (Port 8005)
```bash
cd /home/asif1/open-talent/microservices/user-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
Access: http://localhost:8005/docs

#### 6. Candidate Service (Port 8006)
```bash
cd /home/asif1/open-talent/microservices/candidate-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
Access: http://localhost:8006/docs

---

## 🎙️ Audio/Video Services (Python 3.12)

### Voice Service (Port 8003)

```bash
# Install system dependencies first
sudo apt-get install libsndfile1 portaudio19-dev

# Setup Python 3.12 environment
cd /home/asif1/open-talent/microservices/voice-service
python3.12 -m venv venv-3.12
source venv-3.12/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-webrtc.txt

# Download Vosk model (optional for better speech recognition)
mkdir -p models/vosk
cd models/vosk
wget https://github.com/alphacep/vosk-api/releases/download/v0.3.45/model-en-us-0.42-gigaspeech.zip
unzip model-en-us-0.42-gigaspeech.zip
cd ../..

# Start service
python3.12 main.py
```
Access: http://localhost:8003/docs

### Avatar Service (Port 8004)

```bash
cd /home/asif1/open-talent/microservices/avatar-service
python3.12 -m venv venv-3.12
source venv-3.12/bin/activate
pip install -r requirements.txt
python3.12 main.py
```
Access: http://localhost:8004/docs

---

## 🔍 Check Service Health

```bash
# Scout Service
curl http://localhost:8000/health

# Interview Service  
curl http://localhost:8001/health

# Conversation Service
curl http://localhost:8002/health

# Voice Service
curl http://localhost:8003/health

# Avatar Service
curl http://localhost:8004/health

# Desktop Integration
curl http://localhost:8009/health
```

---

## 📊 Service Dependencies

### Python 3.13 Services (Core)
- scout-service (8000)
- conversation-service (8002)
- interview-service (8001)
- user-service (8005)
- candidate-service (8006)
- analytics-service (8007)
- desktop-integration-service (8009)
- security-service (8010)
- notification-service (8011)
- ai-auditing-service (8012)
- explainability-service (8013)

### Python 3.12 Services (Audio/Video)
- voice-service (8003)
- avatar-service (8004)

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using the port
lsof -i :8000  # Replace 8000 with your port

# Kill the process
kill -9 <PID>
```

### Module Not Found
```bash
# Make sure dependencies are installed
source venv/bin/activate  # or venv-3.12/bin/activate
pip install -r requirements.txt
```

### Import Error: agent_registry
This is expected if you're running scout-service before installing agent modules. The agent integration is built-in and will work once dependencies are installed.

### Python 3.12 Not Found
```bash
# Install Python 3.12
sudo apt-get install python3.12 python3.12-venv

# Verify installation
python3.12 --version
```

### Audio Device Issues (Voice Service)
```bash
# Check available audio devices
python3.12 -c "import sounddevice as sd; print(sd.query_devices())"

# List ALSA devices
arecord -l
```

---

## 📚 Full Documentation

See detailed documentation:
- **[MICROSERVICES_TEST_REPORT.md](MICROSERVICES_TEST_REPORT.md)** - Complete test results
- **[MICROSERVICES_TEST_QUICK_SUMMARY.md](MICROSERVICES_TEST_QUICK_SUMMARY.md)** - Quick summary
- **[SCOUT_AGENT_INTEGRATION_INDEX.md](SCOUT_AGENT_INTEGRATION_INDEX.md)** - Agent integration guide

---

## ✅ Verification Checklist

- [ ] Python 3.13 installed
- [ ] Python 3.12 installed (for voice/avatar)
- [ ] System dependencies installed (libsndfile1, portaudio19-dev)
- [ ] Git repository cloned
- [ ] Docker installed (for docker-compose)
- [ ] All services tested successfully

---

## 🎯 Development Workflow

1. **Start Core Services First**
   ```bash
   # Terminal 1: Scout Service
   cd scout-service && python main.py
   
   # Terminal 2: User Service
   cd user-service && python main.py
   
   # Terminal 3: Conversation Service
   cd conversation-service && python main.py
   ```

2. **Then Start Supporting Services**
   ```bash
   # Interview, Analytics, etc.
   ```

3. **Test Endpoints**
   ```bash
   # Use Swagger UI at http://localhost:8000/docs
   # or curl commands
   curl -X GET "http://localhost:8000/health"
   ```

---

## 📞 Support

**Need Help?**
1. Check logs in service directory
2. Review documentation
3. Check GitHub issues
4. Review error messages carefully

---

**Status**: ✅ READY FOR DEPLOYMENT  
**Last Tested**: December 13, 2025  
**All Systems Operational** 🚀

