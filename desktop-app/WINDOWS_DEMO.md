# Windows Demo Instructions

## Option 1: Run from Source (Fastest)

**From PowerShell:**

```powershell
# Navigate to the project (adjust path to where you copied it)
cd C:\Users\YourUsername\Desktop\open-talent\desktop-app

# Install dependencies (one time)
npm install --legacy-peer-deps

# Run the app
npm start
```

The app will build and launch in a few seconds. You'll see the 3-step wizard.

---

## Option 2: Build Windows Installer (.exe)

**From WSL (to build):**

```bash
cd /home/asif1/open-talent/desktop-app
npx electron-builder --win nsis
```

This creates `release/OpenTalent Setup 0.1.0.exe`

**Copy to Windows:**

```bash
cp release/OpenTalent*.exe /mnt/c/Users/YourUsername/Desktop/
```

**From Windows:**

Double-click `OpenTalent Setup 0.1.0.exe` to install, then launch from Start Menu.

---

## Option 3: Portable Windows Build

**From WSL:**

```bash
cd /home/asif1/open-talent/desktop-app
npx electron-builder --win portable
```

This creates `release/OpenTalent 0.1.0.exe` (no install needed)

**Copy and Run:**

```bash
cp release/OpenTalent*.exe /mnt/c/Users/YourUsername/Desktop/
```

Double-click the .exe from Windows Desktop.

---

## Verification Checklist

Once the app launches:

1. **Step 1**: See your RAM (e.g., 16GB), CPU cores, platform (WIN32)
2. **Step 2**: See model recommendation based on RAM
3. **Step 3**: Confirm selection, see success message
4. **Restart app**: Should skip to Step 3 with saved config
5. **Config location**: `%APPDATA%\opentalent\config.json`

---

## Troubleshooting

**"npm: command not found" in PowerShell**
- Install Node.js from https://nodejs.org/
- Restart PowerShell

**Build fails in WSL**
- Ensure you have Windows build tools: `npm install --global windows-build-tools` (from WSL)
- Or build from Windows PowerShell directly after copying project files

**App window is blank**
- Check DevTools console (Ctrl+Shift+I in the app window)
- Share any error messages
