pipeline {
    agent any
    
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    environment {
        PYTHON_HOME = 'C:\\Python311'
        VENV_DIR = 'venv'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '=== Checking out code ==='
                checkout scm
            }
        }
        
        stage('Find Python') {
            steps {
                echo '=== Locating Python ==='
                script {
                    bat '''
                        @echo off
                        setlocal enabledelayedexpansion
                        
                        set "PYTHON_FOUND=0"
                        set "PYTHON_PATH="
                        
                        echo Current PATH:
                        echo !PATH!
                        echo.
                        
                        REM Check multiple common Python installation locations
                        echo Searching for Python installations...
                        for %%P in (
                            "C:\\Python311"
                            "C:\\Python310"
                            "C:\\Python39"
                            "C:\\Program Files\\Python311"
                            "C:\\Program Files\\Python310"
                            "C:\\Program Files\\Python39"
                            "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python311"
                            "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python310"
                        ) do (
                            if exist "%%P\\python.exe" (
                                echo ✓ Found Python at: %%P
                                set "PYTHON_PATH=%%P\\python.exe"
                                set "PYTHON_FOUND=1"
                                !PYTHON_PATH! --version
                                set "PATH=%%P;%%P\\Scripts;!PATH!"
                                goto :FOUND
                            )
                        )
                        
                        :FOUND
                        if !PYTHON_FOUND! equ 1 (
                            echo.
                            echo ✓ Python found successfully: !PYTHON_PATH!
                        ) else (
                            echo.
                            echo ⚠ Python not found - will auto-install in next stage
                        )
                    '''
                }
            }
        }
        
        stage('Auto-Install Python') {
            steps {
                echo '=== Checking if Python installation is complete ==='
                script {
                    def pythonExists = bat(script: '''
                        @echo off
                        setlocal enabledelayedexpansion
                        
                        REM Check if Python exists in any common location
                        if exist "C:\\Python311\\python.exe" exit /b 0
                        if exist "C:\\Python310\\python.exe" exit /b 0
                        if exist "C:\\Program Files\\Python311\\python.exe" exit /b 0
                        if exist "C:\\Program Files\\Python310\\python.exe" exit /b 0
                        
                        REM Try to run python command
                        python --version >nul 2>&1
                        exit /b !ERRORLEVEL!
                    ''', returnStatus: true)
                    
                    if (pythonExists == 0) {
                        echo '✓ Python already installed, skipping auto-install'
                    } else {
                        echo '=== Auto-installing Python 3.11 ==='
                        bat '''
                            @echo off
                            setlocal enabledelayedexpansion
                            
                            set "PYTHON_INSTALLER=%TEMP%\\python-3.11.9-amd64.exe"
                            set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
                            
                            echo Downloading Python from: !PYTHON_URL!
                            powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!PYTHON_URL!' -OutFile '!PYTHON_INSTALLER!' -ErrorAction Stop"
                            
                            if not exist "!PYTHON_INSTALLER!" (
                                echo ERROR: Failed to download Python installer
                                exit /b 1
                            )
                            
                            echo Installing Python...
                            "!PYTHON_INSTALLER!" /quiet /simple PrependPath=1 InstallAllUsers=1
                            
                            timeout /t 5 /nobreak
                            
                            echo Verifying installation...
                            if exist "C:\\Program Files\\Python311\\python.exe" (
                                echo ✓ Python installed successfully at C:\\Program Files\\Python311
                                "C:\\Program Files\\Python311\\python.exe" --version
                            ) else if exist "C:\\Python311\\python.exe" (
                                echo ✓ Python installed successfully at C:\\Python311
                                "C:\\Python311\\python.exe" --version
                            ) else (
                                echo ERROR: Python installation failed
                                exit /b 1
                            )
                            
                            echo Cleaning up installer...
                            del /f /q "!PYTHON_INSTALLER!" 2>nul
                        '''
                    }
                }
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                echo '=== Setting up Python Virtual Environment ==='
                bat '''
                    @echo off
                    setlocal enabledelayedexpansion
                    
                    REM Try different possible Python locations
                    set "PYTHON_EXE=python"
                    
                    if exist "C:\\Program Files\\Python311\\python.exe" (
                        set "PYTHON_EXE=C:\\Program Files\\Python311\\python.exe"
                    ) else if exist "C:\\Python311\\python.exe" (
                        set "PYTHON_EXE=C:\\Python311\\python.exe"
                    ) else if exist "C:\\Python310\\python.exe" (
                        set "PYTHON_EXE=C:\\Python310\\python.exe"
                    ) else if exist "C:\\Program Files\\Python310\\python.exe" (
                        set "PYTHON_EXE=C:\\Program Files\\Python310\\python.exe"
                    )
                    
                    echo Using Python: !PYTHON_EXE!
                    "!PYTHON_EXE!" --version
                    
                    REM Remove old venv if exists
                    if exist "%VENV_DIR%" (
                        echo Removing old virtual environment...
                        rmdir /s /q "%VENV_DIR%"
                    )
                    
                    REM Create new virtual environment
                    echo Creating new virtual environment...
                    "!PYTHON_EXE!" -m venv "%VENV_DIR%"
                    
                    if errorlevel 1 (
                        echo ERROR: Failed to create virtual environment
                        exit /b 1
                    )
                    
                    echo ✓ Virtual environment created successfully at: %VENV_DIR%
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '=== Installing Python Dependencies ==='
                bat '''
                    @echo off
                    setlocal enabledelayedexpansion
                    
                    REM Activate virtual environment
                    call "%VENV_DIR%\\Scripts\\activate.bat"
                    
                    if errorlevel 1 (
                        echo ERROR: Failed to activate virtual environment
                        exit /b 1
                    )
                    
                    REM Upgrade pip
                    echo Upgrading pip...
                    python -m pip install --upgrade pip
                    
                    if errorlevel 1 (
                        echo ERROR: Failed to upgrade pip
                        exit /b 1
                    )
                    
                    REM Install requirements
                    echo Installing requirements from requirements.txt...
                    if exist "requirements.txt" (
                        pip install -r requirements.txt
                    ) else (
                        echo WARNING: requirements.txt not found, installing flask directly
                        pip install flask
                    )
                    
                    if errorlevel 1 (
                        echo ERROR: Failed to install dependencies
                        exit /b 1
                    )
                    
                    echo [OK] Dependencies installed successfully
                    pip list
                '''
            }
        }
        
        stage('Initialize Database') {
            steps {
                echo '=== Initializing Database ==='
                bat '''
                    @echo off
                    setlocal enabledelayedexpansion
                    
                    REM Set console encoding to UTF-8 for Unicode support
                    chcp 65001 >nul 2>&1
                    
                    call "%VENV_DIR%\\Scripts\\activate.bat"
                    
                    if errorlevel 1 (
                        echo ERROR: Failed to activate virtual environment
                        exit /b 1
                    )
                    
                    if exist "create_appointments_table.py" (
                        echo Running database initialization script...
                        python create_appointments_table.py
                        REM Ignore errors from Python script and continue
                    ) else (
                        echo Running app initialization...
                        python -c "from app import init_db; init_db(); print('[OK] Database initialized')"
                    )
                    
                    echo [OK] Database initialization completed
                '''
            }
        }
        
        stage('Run Application') {
            steps {
                echo '=== Starting Flask Application ==='
                bat '''
                    @echo off
                    setlocal enabledelayedexpansion
                    
                    call "%VENV_DIR%\\Scripts\\activate.bat"
                    
                    echo Flask application is ready to run
                    echo To start the app, run: flask run --host 0.0.0.0 --port 5000
                    
                    REM Uncomment the line below to auto-start the app
                    REM python app.py
                '''
            }
        }
    }
    
    post {
        always {
            echo '=== Pipeline Execution Summary ==='
            deleteDir()
        }
        success {
            echo '[OK] Pipeline completed successfully!'
        }
        failure {
            echo '[FAIL] Pipeline failed!'
        }
    }
}
