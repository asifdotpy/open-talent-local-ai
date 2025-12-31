# OpenTalent - User Guide for Non-Technical Users 👥

Welcome to OpenTalent! This guide will help you run the AI recruitment platform without any technical knowledge.

---

## What is OpenTalent?

OpenTalent is a desktop application that uses artificial intelligence to find and evaluate technical candidates from platforms like GitHub, LinkedIn, and Stack Overflow.

**Key Benefits:**
- 🤖 **AI-Powered**: Automatically finds the best candidates
- 🔒 **Private**: All data stays on your computer
- ⚡ **Fast**: Results in seconds, not hours
- 💰 **Cost-Effective**: No monthly subscription fees

---

## Step 1: First-Time Setup (One Time Only)

### For Windows Users

1. **Download the project**:
   - Visit: https://github.com/asifdotpy/open-talent-local-ai
   - Click the green "Code" button → "Download ZIP"
   - Extract the ZIP file to your Documents folder

2. **Install Python**:
   - Download from: https://www.python.org/downloads/
   - During installation, CHECK ☑️ "Add Python to PATH"
   - Click "Install Now"

3. **Install Node.js**:
   - Download from: https://nodejs.org/
   - Choose "LTS" version
   - Click through the installer (use default settings)

4. **Open Command Prompt**:
   - Press `Windows Key + R`
   - Type `cmd` and press Enter

5. **Navigate to the project**:
   ```cmd
   cd Documents\open-talent-local-ai
   ```

6. **Run setup** (copy and paste these commands one by one):
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   cd desktop-app
   npm install --legacy-peer-deps
   cd ..
   ```

### For Mac Users

1. **Download the project**:
   - Visit: https://github.com/asifdotpy/open-talent-local-ai
   - Click "Code" → "Download ZIP"
   - Double-click to extract to your Desktop

2. **Install Homebrew** (if not already installed):
   - Open Terminal (find it in Applications → Utilities)
   - Paste this command and press Enter:
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

3. **Install Python and Node.js**:
   ```bash
   brew install python@3.12 node
   ```

4. **Setup the project**:
   ```bash
   cd ~/Desktop/open-talent-local-ai
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cd desktop-app
   npm install --legacy-peer-deps
   cd ..
   ```

---

## Step 2: Daily Usage (Every Time You Want to Use OpenTalent)

### Starting OpenTalent

**Windows**:
```cmd
cd Documents\open-talent-local-ai
manage.bat start
```

**Mac/Linux**:
```bash
cd ~/Desktop/open-talent-local-ai
./manage.sh start
```

**What you'll see**:
- Several lines of text showing services starting
- Green checkmarks ✅ when each service is ready
- A message: "OpenTalent is Ready for Demo! 🌟"
- A web address: `http://localhost:3000`

### Opening the Application

1. **Open your web browser** (Chrome, Firefox, Safari, or Edge)
2. **Type in the address bar**: `http://localhost:3000`
3. **Press Enter**

You should see the OpenTalent interface!

---

## Step 3: Using OpenTalent

### Searching for Candidates

1. **Enter your search**:
   ```
   Example: "Senior Python Developer in San Francisco"
   ````

2. **Click "Search"** button

3. **Wait 10-30 seconds** while AI finds candidates

4. **Review results**:
   - Each candidate shows:
     - Name and profile picture
     - Skills and experience
     - GitHub projects
     - AI-generated quality score (0-100)

5. **Click on a candidate** to see detailed information

### Understanding Scores

- **80-100**: Excellent match ⭐⭐⭐⭐⭐
- **60-79**: Good match ⭐⭐⭐⭐
- **40-59**: Fair match ⭐⭐⭐
- **Below 40**: Poor match ⭐⭐

---

## Step 4: Stopping OpenTalent

When you're done:

**Windows**:
```cmd
manage.bat stop
```

**Mac/Linux**:
```bash
./manage.sh stop
```

**Important**: Always stop OpenTalent before shutting down your computer!

---

## Step 5: Checking if Everything is Working

Run this command:

**Windows**: `manage.bat status`
**Mac/Linux**: `./manage.sh status`

You should see a table showing all services with:
- ✓ Healthy - Service is working perfectly
- ? Responding - Service is starting up
- ✗ No response - Service needs to be restarted

---

## Common Issues and Solutions

### "Python not found"
**Solution**: Make sure you installed Python and checked "Add to PATH"

### "Node not found"
**Solution**: Restart your computer after installing Node.js

### "Port already in use"
**Solution**: Run the stop command first, then start again

### Browser shows "Cannot connect"
**Solution**: Wait 30 more seconds - services may still be starting

### Nothing works!
**Solution**:
1. Close everything
2. Restart your computer
3. Run the stop command
4. Run the start command
5. Wait 1 minute before opening browser

---

## Getting Help

If you encounter issues:

1. **Take a screenshot** of any error messages
2. **Email**: support@opentalent-demo.com
3. **Include**:
   - Your operating system (Windows 10, Mac OS, etc.)
   - What you were trying to do
   - The error message screenshot

---

## Tips for Best Results

✅ **DO**:
- Close other programs while running OpenTalent
- Use specific job titles ("Senior React Developer" not just "Developer")
- Include location ("in New York", "Remote USA")
- Wait for the "Ready for Demo" message before opening browser

❌ **DON'T**:
- Run multiple instances of OpenTalent at once
- Close Terminal/Command Prompt while OpenTalent is running
- Use very broad searches ("Any developer")
- Shut down computer without running stop command

---

## System Requirements

**Minimum**:
- 8GB RAM
- 20GB free disk space
- Windows 10/Mac OS 10.14 or newer
- Internet connection (first time only for AI model download)

**Recommended**:
- 16GB RAM
- 50GB free disk space
- Recent operating system
- SSD drive for faster performance

---

**Questions?** This is cutting-edge AI technology made simple. You've got this! 🚀
