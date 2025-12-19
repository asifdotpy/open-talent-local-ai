# OpenTalent Demo Quick Reference

## 🚀 Quick Commands

### Start Demo
```bash
./start-demo.sh
```

### Stop Demo
```bash
./stop-demo.sh
```

### Check Services
```bash
# All services health
curl http://localhost:8009/health

# Individual services
curl http://localhost:8007/health  # Analytics
curl http://localhost:11434/api/tags  # Ollama
```

## 🌐 Access Points

- **Desktop App**: http://localhost:3000
- **Gateway API**: http://localhost:8009/docs
- **Analytics API**: http://localhost:8007/docs

## 📊 Demo Flow

1. **Start**: `./start-demo.sh` (2-3 min startup)
2. **Access**: Open http://localhost:3000
3. **Interview**: Enter "test-001" → Select Frontend → Start
4. **Results**: View enhanced analytics dashboard
5. **Stop**: `./stop-demo.sh`

## 🔧 Troubleshooting

### Services Won't Start
```bash
# Kill all on ports
kill $(lsof -t -i :3000) 2>/dev/null || true
kill $(lsof -t -i :8007) 2>/dev/null || true
kill $(lsof -t -i :8009) 2>/dev/null || true
pkill ollama

# Restart
./start-demo.sh
```

### Memory Issues
- Close other apps
- Use smaller model: Edit start-demo.sh → change to granite3.1:350m

### Analytics Not Working
```bash
# Check analytics logs
tail -f microservices/analytics-service/logs/analytics.log
```

## 📈 Key Features to Demo

- ✅ **Offline AI**: No internet required after setup
- ✅ **Enhanced Analytics**: Sentiment + quality analysis
- ✅ **Real-time Processing**: Live interview analysis
- ✅ **Rich Results**: Charts, metrics, recommendations
- ✅ **Privacy First**: All data stays local

## 🎯 Demo Script

**"Welcome to OpenTalent - the future of AI interviews that respects your privacy!"**

1. **Show Architecture**: "Everything runs locally - no cloud, no API keys"
2. **Start Demo**: "One command starts everything: `./start-demo.sh`"
3. **Live Interview**: "Let's do a sample interview with 'test-001'"
4. **Enhanced Results**: "See how analytics provide deep insights"
5. **Privacy**: "All processing happens on this machine - complete privacy"

---

**🎬 Demo Time: 5-7 minutes | Setup: 2-3 minutes**