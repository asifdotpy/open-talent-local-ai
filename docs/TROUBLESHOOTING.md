# Troubleshooting Guide

**Version:** 1.0  
**Date:** December 14, 2025  
**Status:** Phase 8 Implementation

---

## Quick Reference

| Problem | Symptom | Solution |
|---------|---------|----------|
| Ollama offline | "Service offline" error | Start Ollama: `ollama serve` |
| Model not available | "Model not available" error | Download model: `ollama pull modelname` |
| Slow responses | Long wait times | Check internet, restart app, free RAM |
| Validation error | "Input invalid" message | Check input format, read error message |
| Microphone not working | Can't record responses | Check microphone permissions |
| High CPU usage | App is slow | Close other apps, reduce model size |
| High memory usage | App crashes | Switch to smaller model (350M) |

---

## Installation Troubleshooting

### Problem: Application Won't Start

**Symptoms:**
- Blank window or crash immediately
- "Error starting application" message

**Solutions:**

1. **Check system requirements:**
   ```bash
   # Check RAM
   free -h  # Linux
   vm_stat  # macOS
   wmic OS get TotalVisibleMemorySize  # Windows
   ```

2. **Ensure Node.js is installed:**
   ```bash
   node --version  # Should be v20.0.0+
   npm --version
   ```

3. **Reinstall application:**
   ```bash
   npm install
   npm start
   ```

4. **Check logs:**
   ```bash
   # Linux/macOS
   ~/.OpenTalent/logs/app.log
   
   # Windows
   C:\Users\YourUsername\AppData\Local\OpenTalent\logs\app.log
   ```

### Problem: Ollama Service Won't Start

**Symptoms:**
- "Ollama offline" error immediately on startup
- Connection refused to localhost:11434

**Solutions:**

1. **Install Ollama:**
   - Visit https://ollama.ai
   - Download for your OS (Windows/macOS/Linux)
   - Run installer

2. **Start Ollama service:**
   ```bash
   # Linux
   sudo systemctl start ollama
   
   # macOS
   brew services start ollama
   
   # Windows (already running as service)
   # Check Services app
   
   # Manual start (any OS)
   ollama serve
   ```

3. **Verify Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **Check firewall:**
   - Ensure port 11434 is accessible locally
   - Check firewall settings

### Problem: Model Download Fails

**Symptoms:**
- "Model download failed" error
- Stuck on download progress

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping 8.8.8.8  # Google DNS
   ```

2. **Try manual download:**
   ```bash
   ollama pull granite2b
   # Wait for completion
   ollama list
   ```

3. **Check disk space:**
   ```bash
   # Linux/macOS
   df -h
   
   # Windows
   dir C:\
   
   # Need 5GB+ free space
   ```

4. **Check model availability:**
   ```bash
   ollama list
   # Should show available models
   ```

---

## Runtime Troubleshooting

### Problem: "Service Offline" Error

**When it happens:**
- On startup
- During interview
- When sending responses

**Debugging steps:**

1. **Check if Ollama is running:**
   ```bash
   # Try to connect
   curl http://localhost:11434/api/tags
   
   # If no response: Ollama is offline
   ```

2. **Start Ollama:**
   ```bash
   ollama serve
   ```

3. **Check Ollama logs:**
   ```bash
   # Linux
   journalctl -u ollama -f
   
   # macOS
   log stream --predicate 'process == "ollama"' --level debug
   ```

4. **Restart application:**
   - Close OpenTalent
   - Ensure Ollama is running
   - Restart OpenTalent

5. **Check firewall:**
   - Verify port 11434 is not blocked
   - Try on another port (advanced)

### Problem: "Model Not Available" Error

**When it happens:**
- After selecting a model
- When starting interview

**Solutions:**

1. **Check available models:**
   ```bash
   ollama list
   ```

2. **Download missing model:**
   ```bash
   # Available models
   ollama pull granite2b     # 2B parameter model
   ollama pull granite350b   # 350M parameter model
   ollama pull granite8b     # 8B parameter model
   ```

3. **Wait for download:**
   ```bash
   # Monitor download progress
   watch ollama list
   ```

4. **Restart application:**
   - Close and reopen OpenTalent
   - Model should now be available

### Problem: Slow Response Times

**Symptoms:**
- Long wait (>30s) for response
- "Request timeout" error

**Causes and solutions:**

1. **Check internet connection:**
   ```bash
   # Test speed
   ping -c 1 8.8.8.8
   
   # Test latency
   tracert 8.8.8.8  # Windows
   traceroute 8.8.8.8  # Linux/macOS
   ```

2. **Check system resources:**
   ```bash
   # Linux
   top  # Press 'q' to exit
   
   # macOS
   Activity Monitor
   
   # Windows
   Task Manager
   ```
   - Free up RAM if usage > 80%
   - Close unnecessary applications

3. **Check model performance:**
   - Granite-350M: Fastest but lower quality
   - Granite-2B: Balanced performance
   - Granite-8B: Highest quality, slower
   - Consider switching to smaller model

4. **Optimize system:**
   ```bash
   # Close background apps
   # Disable GPU acceleration if causing issues
   # Increase swap memory if available
   ```

5. **Check Ollama logs:**
   ```bash
   # Look for error messages or performance issues
   journalctl -u ollama -f
   ```

### Problem: Response Validation Error

**Symptoms:**
- Error message: "Response should be at least 10 characters"
- Error message: "Response should not exceed 2000 characters"
- Error message: "Response contains invalid characters"

**Solutions:**

1. **Read the error message carefully** - It explains what's wrong

2. **For "too short" error:**
   - Provide at least 10 characters
   - Full sentences work better

3. **For "too long" error:**
   - Keep response under 2000 characters
   - Break into multiple responses if needed

4. **For "invalid characters" error:**
   - Don't use excessive special characters
   - Max 30% special characters
   - Avoid null bytes or control characters

---

## Performance Troubleshooting

### Problem: High CPU Usage

**Symptoms:**
- Application CPU usage > 80%
- Computer is slow/unresponsive

**Solutions:**

1. **Close unnecessary applications:**
   ```bash
   # Kill background processes
   killall -9 chrome  # Example
   ```

2. **Check Ollama CPU usage:**
   ```bash
   # Linux/macOS
   top  # Look for ollama process
   ps aux | grep ollama
   ```

3. **Switch to smaller model:**
   - Settings → Model Size
   - Select Granite-350M (fastest)

4. **Disable GPU acceleration** (if enabled):
   - Settings → Advanced
   - Disable "Use GPU if available"

5. **Restart Ollama:**
   ```bash
   # Kill Ollama
   killall ollama
   
   # Start fresh
   ollama serve
   ```

### Problem: High Memory Usage

**Symptoms:**
- Application RAM usage > 80% of total
- Application crashes with "out of memory" error

**Solutions:**

1. **Check current memory usage:**
   ```bash
   # Linux
   free -h
   
   # macOS
   memory_pressure
   
   # Windows
   wmic OS get TotalVisibleMemorySize
   ```

2. **Switch to smaller model:**
   - Settings → Model Size
   - Select Granite-350M (uses ~2-4GB)
   - Granite-2B uses ~8-12GB
   - Granite-8B uses ~16-32GB

3. **Close other applications:**
   - Browsers, IDEs, other heavy applications

4. **Increase available memory:**
   - Close browser tabs
   - Restart computer

5. **Check for memory leaks:**
   ```bash
   # Monitor memory over time
   watch -n 1 'free -h'  # Linux
   ```

### Problem: High Disk Usage

**Symptoms:**
- "Disk space low" warning
- Download fails due to disk space

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h  # Linux/macOS
   ```

2. **Required space by model:**
   - Granite-350M: 1GB
   - Granite-2B: 2GB
   - Granite-8B: 5GB
   - Plus 1GB for application = 6-7GB total needed

3. **Free up disk space:**
   - Delete old files/applications
   - Clear browser cache
   - Empty trash/recycle bin

4. **Move model cache:**
   - Linux/macOS: `~/.ollama/models`
   - Windows: `%USERPROFILE%\.ollama\models`
   - Move to drive with more space
   - Update settings with new path

---

## Audio/Microphone Troubleshooting

### Problem: Microphone Not Working

**Symptoms:**
- No audio recording
- "Permission denied" error
- Microphone not detected

**Solutions:**

1. **Check microphone permissions:**
   
   **Linux:**
   ```bash
   # Check audio group
   groups $USER | grep audio
   
   # Add user to audio group if needed
   sudo usermod -a -G audio $USER
   ```
   
   **macOS:**
   - System Preferences → Security & Privacy
   - Microphone
   - Enable OpenTalent

   **Windows:**
   - Settings → Privacy & Security → Microphone
   - Enable microphone access

2. **Check microphone is detected:**
   ```bash
   # Linux
   arecord -l
   
   # macOS
   system_profiler SPAudioDataType
   
   # Windows
   wmic sounddev list
   ```

3. **Test microphone:**
   ```bash
   # Linux
   rec test.wav  # Press Ctrl+C to stop
   
   # macOS
   sox -d -t wav -r 16000 -b 16 -c 1 - | sox - -d
   ```

4. **Restart application:**
   - Close OpenTalent
   - Allow microphone permissions
   - Restart OpenTalent

5. **Try another microphone:**
   - Unplug current microphone
   - Plug in another microphone
   - Restart application

### Problem: Audio Quality Issues

**Symptoms:**
- Background noise
- Crackling or distortion
- Echoingwhen speaking

**Solutions:**

1. **Use microphone mute/unmute:**
   - Mute background noise when not speaking
   - Use push-to-talk mode if available

2. **Improve microphone placement:**
   - Closer to mouth (3-6 inches)
   - Away from fans/background noise
   - Not pointing at keyboard

3. **Check microphone settings:**
   - System volume: 50-75%
   - Microphone input level: optimal
   - Check for noise cancellation

4. **Use headphones:**
   - Reduces echo/feedback
   - Improves privacy

---

## Connection Troubleshooting

### Problem: Network Error During Interview

**Symptoms:**
- "Network error occurred" message
- Can't reach Ollama after working
- Intermittent connectivity issues

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping -c 5 8.8.8.8
   ```

2. **Check localhost connectivity:**
   ```bash
   ping localhost
   ping 127.0.0.1
   curl http://localhost:11434/api/tags
   ```

3. **Restart network:**
   ```bash
   # Linux
   sudo systemctl restart networking
   
   # macOS
   sudo killall -HUP mDNSResponder
   
   # Windows
   ipconfig /release
   ipconfig /renew
   ```

4. **Check firewall:**
   - Ensure port 11434 is accessible
   - Check Windows Defender Firewall
   - Check third-party firewall

5. **Restart Ollama:**
   ```bash
   ollama serve
   ```

---

## Getting Help

### Before Contacting Support

1. **Collect error details:**
   - Exact error message
   - When error occurs (startup/mid-interview)
   - Steps to reproduce

2. **Gather system information:**
   ```bash
   # System info
   uname -a  # Linux/macOS
   systeminfo  # Windows
   
   # RAM
   free -h  # Linux
   vm_stat  # macOS
   
   # Ollama status
   curl http://localhost:11434/api/tags
   ollama list
   ```

3. **Check logs:**
   - Application logs: `~/.OpenTalent/logs/app.log`
   - Ollama logs: `~/.ollama/logs/` or `journalctl -u ollama`

4. **Reproduce the issue:**
   - Document exact steps to reproduce
   - Test on different model if applicable

### Contact Support

When contacting support, include:
1. Error message (exact text)
2. System information (OS, RAM, disk space)
3. OpenTalent version
4. Ollama version and installed models
5. Steps to reproduce
6. Relevant log excerpts

---

## Known Issues

| Issue | Status | Workaround |
|-------|--------|-----------|
| High latency on first response | Investigating | Happens when model is loading from disk |
| Memory spike on model switch | Known | Restart app to free memory |
| Slow audio transcription | Investigating | Use external audio if needed |
| Microphone not working on Linux | Investigating | Ensure user in audio group |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 14, 2025 | Initial troubleshooting guide |

---

**For more information, see:**
- [ERROR_HANDLING.md](./ERROR_HANDLING.md)
- [API_REFERENCE.md](./API_REFERENCE.md)
- [README.md](../README.md)
