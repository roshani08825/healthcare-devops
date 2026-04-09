# Python Installation Guide for Jenkins Server

This guide helps you install Python on the Jenkins server machine to fix the pipeline error.

## Quick Start (Automated)

### Step 1: Run the Installation Script

On the **Jenkins server machine**, open PowerShell as Administrator and run:

```powershell
# Navigate to the script location (adjust path if needed)
cd "C:\healthcare-portal"

# Run the installation script
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
.\install-python-jenkins.ps1
```

Or download and run directly:

```powershell
# Run from any location
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
& ([ScriptBlock]::Create((New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/roshani08825/healthcare-devops/main/install-python-jenkins.ps1')))
```

### Step 2: Restart Jenkins Service

After the script completes, restart Jenkins:

**Option A - Using Services GUI:**
1. Press `Win + R`
2. Type `services.msc` and press Enter
3. Find "Jenkins" in the list
4. Right-click → Restart

**Option B - Using PowerShell (as Administrator):**
```powershell
Restart-Service Jenkins
```

**Option C - Using Command Prompt (as Administrator):**
```cmd
net stop Jenkins
net start Jenkins
```

### Step 3: Verify Installation

Check Python is installed:

```powershell
python --version
pip --version
```

Expected output:
```
Python 3.11.9
pip 23.3.1 from C:\Python311\lib\site-packages\pip (python 3.11)
```

### Step 4: Re-run Jenkins Pipeline

1. Go to your Jenkins instance
2. Navigate to your healthcare-devops pipeline
3. Click "Build Now"
4. Monitor the console output - it should now succeed!

---

## Manual Installation (If Script Fails)

If the automated script doesn't work, install Python manually:

1. **Download Python 3.11:**
   - Visit https://www.python.org/downloads/
   - Click "Download Python 3.11.9" (or latest 3.11)

2. **Run the Installer:**
   - Open the `.exe` file
   - **IMPORTANT:** Check the box "Add Python to PATH"
   - Click "Install Now"
   - Wait for completion

3. **Verify Installation:**
   ```powershell
   python --version
   ```

4. **Restart Jenkins:**
   ```powershell
   Restart-Service Jenkins
   ```

---

## Troubleshooting

### "Access Denied" when running script
- Right-click PowerShell → "Run as Administrator"

### "Python not recognized" after installation
- Restart Jenkins service
- Close and reopen PowerShell
- Verify Python is in PATH:
  ```powershell
  $env:Path -split ';' | Select-String Python
  ```

### Jenkins pipeline still fails
- Restart the entire Jenkins server (not just the service)
- Check Jenkins agent logs for errors
- Verify git is installed: `git --version`

---

## Need More Help?

If you encounter issues, please check:

1. **Is Python in PATH?**
   ```powershell
   where python
   ```
   Should show the Python installation path.

2. **Is pip working?**
   ```powershell
   pip list
   ```

3. **Can Jenkins access Python?**
   Run this in Jenkins pipeline console:
   ```groovy
   bat 'python --version'
   ```

---

**Built for:** Healthcare DevOps Pipeline on Windows Jenkins Server
