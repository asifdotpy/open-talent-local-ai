# OpenTalent - Investor Demo Guide 🎬

## Quick Start for Investors

OpenTalent is an AI-powered recruitment platform that revolutionizes technical hiring. This guide will help you set up and record a professional demo.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.12+** installed
- **Node.js 20+** installed
- **10GB free disk space** for AI models
- **Stable internet connection** (first-time model download)

---

## 🚀 One-Command Setup

```bash
# 1. Clone and navigate to the project
git clone https://github.com/asifdotpy/open-talent-local-ai.git
cd open-talent-local-ai

# 2. Install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd desktop-app
npm install --legacy-peer-deps
cd ..

# 3. Start the entire platform
./manage.sh start
```

**That's it!** The platform will start automatically with all services running.

---

## 📊 What Gets Started

When you run `./manage.sh start`, the system launches:

1. **Scout Service** (Port 8000) - GitHub/LinkedIn talent sourcing
2. **Voice Service** (Port 8003) - Speech-to-text AI processing
3. **Analytics Service** (Port 8007) - Interview insights engine
4. **API Gateway** (Port 8009) - Unified service orchestration
5. **Desktop App** (Port 3000) - Modern Electron UI

---

## 🎥 Recording a Professional Demo

### Recommended Setup

1. **Screen Recording Tool**:
   - MacOS: QuickTime Player (built-in)
   - Windows: OBS Studio (free)
   - Linux: SimpleScreenRecorder

2. **Demo Scenario**:

   ```
   Role: Senior React Developer
   Location: Remote (US)
   Skills: React, TypeScript, Node.js
   Experience: 5+ years
   ```

### Recording Steps

1. **Start fresh**:

   ```bash
   ./manage.sh restart
   ```

2. **Wait 30 seconds** for all services to be healthy:

   ```bash
   ./manage.sh status
   ```

   All services should show `✓ Healthy`

3. **Open browser** to `http://localhost:3000`

4. **Begin recording** and demonstrate:
   - **Candidate Search**: Enter "Senior React Developer in NYC"
   - **AI Processing**: Show real-time Scout service finding candidates
   - **Results Display**: Browse candidate profiles with scores
   - **Analytics**: Click on candidates to see detailed matching insights

5. **Stop recording** and save your video

---

## 🎬 Demo Script (60 seconds)

> "**OpenTalent** uses local AI to transform technical recruitment. Watch as I search for a Senior React Developer..."
>
> *[Type query and hit search]*
>
> "Within seconds, our AI Scout service scans GitHub, LinkedIn, and Stack Overflow..."
>
> *[Show candidate results appearing]*
>
> "Here are the top matches, ranked by AI-powered quality scoring. Each candidate includes verified skills, project contributions, and cultural fit analysis..."
>
> *[Click on a candidate]*
>
> "Our analytics engine provides deep insights - years of experience, technology stack alignment, and even communication style predictions based on their public contributions."
>
> "**All of this runs locally** - no cloud dependencies, complete data privacy, and instant results."

---

## 🛑 After Demo

```bash
# Gracefully stop all services
./manage.sh stop
```

This ensures clean shutdown and frees up system resources.

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Run `./manage.sh stop` then `./manage.sh start` |
| Service unhealthy | Check logs: `./manage.sh logs <service-name>` |
| Desktop app won't load | Ensure Node.js dependencies: `cd desktop-app && npm install` |
| Python errors | Activate venv: `source .venv/bin/activate` |

---

## 📈 Key Metrics to Highlight

- **Search Speed**: < 5 seconds for 50+ candidates
- **AI Models**: 100% local (Mistral, Llama for embedding)
- **Data Privacy**: Zero cloud dependencies
- **Cost Savings**: $0/month vs. $500-2000/month for cloud AI services

---

## 📞 Support

For demo setup assistance:

- GitHub Issues: [open-talent-local-ai/issues](https://github.com/asifdotpy/open-talent-local-ai/issues)
- Email: <support@opentalent-demo.com>

---

**Built with ❤️ for the future of AI-powered recruitment**
