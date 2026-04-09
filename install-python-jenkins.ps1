# PowerShell Script to Install Python on Jenkins Server
# Run this script as Administrator on the Jenkins server machine

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Python Installation for Jenkins Server" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Check if Python is already installed
Write-Host "Checking if Python is already installed..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python is already installed: $pythonVersion" -ForegroundColor Green
    Write-Host "No installation needed!"
    exit 0
}
catch {
    Write-Host "✓ Python not found - proceeding with installation" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Downloading Python 3.11 installer..." -ForegroundColor Cyan

# Python 3.11 installer URL
$pythonVersion = "3.11.9"
$pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
$installerPath = "$env:TEMP\python-installer.exe"

# Download Python installer
try {
    Write-Host "Downloading from: $pythonUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✓ Download completed" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Failed to download Python installer" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Download manually from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Installing Python 3.11..." -ForegroundColor Cyan
Write-Host "(This may take a few minutes)" -ForegroundColor Gray

# Run installer with flags
# /quiet - silent installation
# /norestart - don't restart
# PrependPath=1 - add to PATH automatically
try {
    $process = Start-Process -FilePath $installerPath `
        -ArgumentList "/quiet /norestart PrependPath=1" `
        -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✓ Python installation completed successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: Installer returned exit code $($process.ExitCode)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "ERROR: Installation failed" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Cleaning up installer..." -ForegroundColor Cyan
Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue
Write-Host "✓ Cleaned up" -ForegroundColor Green

Write-Host ""
Write-Host "Refreshing environment variables..." -ForegroundColor Cyan
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ""
Write-Host "Verifying Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version
    $pipVersion = pip --version
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
    Write-Host "✓ Pip: $pipVersion" -ForegroundColor Green
}
catch {
    Write-Host "WARNING: Could not verify Python installation" -ForegroundColor Yellow
    Write-Host "Please restart Jenkins service or the server for PATH to be updated" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Close this PowerShell window" -ForegroundColor White
Write-Host "2. Restart Jenkins service:" -ForegroundColor White
Write-Host "   Services.msc → Find 'Jenkins' → Restart" -ForegroundColor Gray
Write-Host "3. Re-run your Jenkins pipeline" -ForegroundColor White
Write-Host ""
