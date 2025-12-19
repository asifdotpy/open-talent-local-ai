# OpenTalent Demo Environment Guide

## 🎯 Overview

OpenTalent is a desktop-first, offline-capable AI interview platform that runs 100% locally on user hardware. This guide covers the complete demo environment setup and operation.

## 🏗️ Architecture

```
OpenTalent Demo Environment
├── Ollama (Port 11434)          - Local AI Model Server
├── Analytics Service (Port 8007) - Sentiment & Quality Analysis
├── Gateway Service (Port 8009)   - API Gateway & Interview Processing
└── Desktop App (Port 3000)       - React/Electron UI
```

## 🚀 Quick Start

### Automated Startup (Recommended)
```bash
# Start all services automatically
./start-demo.sh

# Stop all services
./stop-demo.sh
```

### Manual Startup (Advanced)
```bash
# Terminal 1: Start Ollama
cd /home/asif1/open-talent
ollama serve

# Terminal 2: Start Analytics Service
cd microservices/analytics-service
./start.sh

# Terminal 3: Start Gateway Service
cd microservices/desktop-integration-service
./start.sh

# Terminal 4: Start Desktop App
cd desktop-app
npm run dev
```

## 📋 Prerequisites

### System Requirements
- **RAM**: 8GB minimum (12GB recommended)
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 11+
- **Disk**: 5GB free space
- **Python**: 3.9+ with pip
- **Node.js**: 18+ with npm

### Required Software
- Ollama (installed via script)
- Python virtual environment tools
- Node.js and npm

## 🔧 Services Configuration

### Ollama (Port 11434)
- **Purpose**: Local AI model serving
- **Models**: granite4:350m-h (downloaded automatically)
- **Health Check**: `curl http://localhost:11434/api/tags`

### Analytics Service (Port 8007)
- **Purpose**: Interview analysis and insights
- **Features**:
  - Sentiment analysis
  - Response quality scoring
  - Bias detection
  - Expertise assessment
- **Health Check**: `curl http://localhost:8007/health`
- **API Docs**: `http://localhost:8007/docs`

### Gateway Service (Port 8009)
- **Purpose**: Unified API gateway
- **Features**:
  - Interview processing
  - Analytics integration
  - Service discovery
  - Health monitoring
- **Health Check**: `curl http://localhost:8009/health`
- **API Docs**: `http://localhost:8009/docs`

### Desktop App (Port 3000)
- **Purpose**: User interface
- **Technology**: React + Electron
- **Features**:
  - Interview interface
  - Results visualization
  - Analytics dashboard
- **Access**: `http://localhost:3000`

## 🎬 Demo Flow

### 1. Start Environment
```bash
./start-demo.sh
```
Wait for all services to start (2-3 minutes).

### 2. Access Application
Open browser to: `http://localhost:3000`

### 3. Complete Interview
1. Enter candidate details
2. Select interview type
3. Answer questions
4. View enhanced results with analytics

### 4. Stop Environment
```bash
./stop-demo.sh
```

## 📊 Enhanced Interview Results

The demo showcases comprehensive interview analysis:

### Sentiment Analysis
- Real-time sentiment tracking
- Emotional state visualization
- Confidence assessment

### Quality Metrics
- Response completeness scoring
- Technical accuracy evaluation
- Communication clarity assessment

### Intelligence Insights
- Expertise level detection
- Bias identification
- Recommendation generation

### Visual Analytics
- Interactive charts and graphs
- Performance dashboards
- Detailed feedback reports

## 🔍 Troubleshooting

### Service Won't Start
```bash
# Check if port is in use
lsof -i :PORT_NUMBER

# Kill process on port
kill -9 $(lsof -t -i :PORT_NUMBER)

# Restart service
./start-demo.sh
```

### Analytics Not Working
```bash
# Check analytics service logs
cd microservices/analytics-service
tail -f logs/analytics.log

# Test analytics endpoint
curl -X POST http://localhost:8007/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Test response"}'
```

### Desktop App Issues
```bash
# Clear node modules and reinstall
cd desktop-app
rm -rf node_modules package-lock.json
npm install

# Start in development mode
npm run dev
```

### Ollama Issues
```bash
# Check Ollama status
ollama list

# Restart Ollama
pkill ollama
ollama serve

# Pull model manually
ollama pull granite4:350m-h
```

## 📈 Performance Optimization

### Memory Management
- **Minimum RAM**: 8GB (Granite-2B model)
- **Recommended RAM**: 12GB+ for optimal performance
- **Close other applications** during demo

### Model Selection
- **Fast**: granite3.1:350m (4GB RAM, basic quality)
- **Fast**: granite4:350m-h (4GB RAM, basic quality)
- **Best**: granite3.1:8b (16GB RAM, excellent quality)

### Hardware Acceleration
- **NVIDIA**: CUDA acceleration enabled automatically
- **AMD**: ROCm support (if available)
- **Apple Silicon**: Metal acceleration

## 🔒 Security & Privacy

### Local-First Design
- ✅ **No cloud dependencies**: All processing local
- ✅ **No data transmission**: Conversations stay on device
- ✅ **No API keys required**: Works offline
- ✅ **GDPR compliant**: Data never leaves your control

### Data Storage
- Conversations: `~/OpenTalent/cache/conversations/`
- Audio files: `~/OpenTalent/cache/audio/`
- Logs: `~/OpenTalent/logs/`

## 📚 API Documentation

### Analytics Service
- **Base URL**: `http://localhost:8007`
- **Endpoints**:
  - `POST /analyze` - Analyze interview response
  - `GET /health` - Service health check
  - `GET /docs` - Interactive API documentation

### Gateway Service
- **Base URL**: `http://localhost:8009`
- **Endpoints**:
  - `POST /interview/respond` - Process interview response
  - `GET /interview/summary/{id}` - Get interview summary
  - `GET /health` - Service health check
  - `GET /docs` - Interactive API documentation

## 🛠️ Development

### Project Structure
```
open-talent/
├── microservices/
│   ├── analytics-service/        # Sentiment analysis
│   └── desktop-integration-service/  # API gateway
├── desktop-app/                  # React/Electron UI
├── scripts/                      # Utility scripts
├── docs/                         # Documentation
└── start-demo.sh                 # Demo startup script
```

### Adding New Features
1. **Analytics**: Extend `analytics-service/app/main.py`
2. **Gateway**: Modify `desktop-integration-service/app/main.py`
3. **UI**: Update `desktop-app/src/`
4. **Models**: Add to Ollama via `ollama pull <model>`

## 📞 Support

### Common Issues
- **Port conflicts**: Stop other services using same ports
- **Memory issues**: Close unnecessary applications
- **Model download**: Ensure stable internet for initial setup

### Logs Location
- Analytics: `microservices/analytics-service/logs/`
- Gateway: `microservices/desktop-integration-service/logs/`
- Desktop App: `desktop-app/logs/`
- Ollama: System logs (varies by OS)

### Getting Help
1. Check service logs for error messages
2. Verify all prerequisites are installed
3. Ensure sufficient RAM is available
4. Test individual services before full demo

## 🎯 Demo Checklist

### Pre-Demo Setup
- [ ] System meets requirements (8GB+ RAM)
- [ ] All prerequisites installed
- [ ] Demo scripts are executable
- [ ] Test environment works

### During Demo
- [ ] Start with `./start-demo.sh`
- [ ] Wait for all services to be healthy
- [ ] Open `http://localhost:3000`
- [ ] Complete sample interview
- [ ] Showcase enhanced analytics results

### Post-Demo Cleanup
- [ ] Stop with `./stop-demo.sh`
- [ ] Clear browser cache if needed
- [ ] Review logs for any issues

---

**🎉 Ready to experience the future of AI interviews? Run `./start-demo.sh` and open `http://localhost:3000`!**