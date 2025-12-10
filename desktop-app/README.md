# OpenTalent Desktop App

Privacy-first AI interview platform built with Electron and Ollama.

## Quick Start

### Prerequisites

1. **Node.js** (v20.0.0+)
   ```bash
   node --version
   ```

2. **Ollama** (for local AI)
   ```bash
   # Check if Ollama is installed
   ollama --version
   ```

### Installation

1. Install dependencies:
   ```bash
   cd desktop-app
   npm install
   ```

2. Install Ollama (if not already installed):
   ```bash
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # macOS
   brew install ollama
   
   # Windows: Download from https://ollama.com/download
   ```

3. Pull a model:
   ```bash
   # Option 1: Granite Code (recommended, smaller)
   ollama pull granite-code:3b
   
   # Option 2: Llama 3.2 (fallback)
   ollama pull llama3.2
   
   # Option 3: Any other chat model
   ollama list  # See available models
   ```

4. Start Ollama server:
   ```bash
   ollama serve
   ```
   Keep this running in a separate terminal.

### Running the App

```bash
# Development mode (with DevTools)
npm run dev

# Production mode
npm start
```

### Building Installers

```bash
# Build for your current platform
npm run build

# Build for specific platforms
npm run build:linux   # Linux AppImage and .deb
npm run build:win     # Windows installer
npm run build:mac     # macOS .dmg
```

## Project Structure

```
desktop-app/
├── src/
│   ├── main/
│   │   ├── main.js          # Electron main process
│   │   └── preload.js       # IPC bridge
│   ├── renderer/
│   │   ├── index.html       # UI
│   │   ├── styles.css       # Styling
│   │   └── app.js           # Frontend logic
│   └── services/
│       └── ollama-service.js # Ollama API client
├── resources/
├── package.json
└── README.md
```

## Features

- 🤖 **Local AI**: 100% offline, no cloud dependencies
- 🔒 **Privacy-First**: All data stays on your device
- 💼 **3 Interview Roles**: Software Engineer, Product Manager, Data Analyst
- 💬 **Interactive Chat**: Real-time conversation with AI interviewer
- 📊 **Interview Summary**: Review your answers after completion

## Troubleshooting

### Ollama Not Running

**Error:** "🔴 Ollama Offline"

**Solution:**
```bash
# Start Ollama server
ollama serve
```

### No Models Found

**Error:** "No models found. Please install a model."

**Solution:**
```bash
# Pull a model
ollama pull granite-code:3b
# or
ollama pull llama3.2
```

### Slow Response Times

**Possible causes:**
- Large model on low-end hardware
- Insufficient RAM

**Solutions:**
- Use a smaller model (granite-code:3b instead of 7b/13b)
- Close other applications
- Increase system swap space

### Connection Refused

**Error:** "Failed to send message: connect ECONNREFUSED"

**Solution:**
- Ensure Ollama is running (`ollama serve`)
- Check Ollama is on port 11434: `curl http://localhost:11434/api/tags`

## Development

### Testing Ollama API

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test chat
curl http://localhost:11434/api/chat -d '{
  "model": "granite-code:3b",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}'
```

### Adding New Interview Roles

Edit `src/services/ollama-service.js` and add a new entry to the `getInterviewPrompt()` method:

```javascript
'Your Role Name': `You are an experienced interviewer...`
```

Then add the role button in `src/renderer/index.html`.

## License

GPL-3.0

## Support

For issues, visit: https://github.com/asif1/open-talent/issues
