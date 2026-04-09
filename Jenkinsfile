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
                        
                        REM Check if python is already in PATH
                        where python >nul 2>nul
                        if errorlevel 0 (
                            set "PYTHON_FOUND=1"
                            echo Found Python in PATH
                            python --version
                            goto :EOF
                        )
                        
                        REM Checking common installation locations
                        echo Python not found in PATH, checking common locations...
                        
                        REM Check multiple common Python installation locations
                        for %%P in (
                            "C:\\Python311"
                            "C:\\Python310"
                            "C:\\Python39"
                            "C:\\Program Files\\Python311"
                            "C:\\Program Files\\Python310"
                            "C:\\Program Files\\Python39"
                            "C:\\Users\\!USERNAME!\\AppData\\Local\\Programs\\Python\\Python311"
                            "C:\\Users\\!USERNAME!\\AppData\\Local\\Programs\\Python\\Python310"
                        ) do (
                            if exist "%%P\\python.exe" (
                                echo Found Python at %%P
                                set "PATH=%%P;%%P\\Scripts;!PATH!"
                                set "PYTHON_FOUND=1"
                                python --version
                                goto :FOUND
                            )
                        )
                        
                        :FOUND
                        if !PYTHON_FOUND! equ 0 (
                            echo.
                            echo ===== ERROR: Python NOT FOUND =====
                            echo.
                            echo Python is required but not installed on this Jenkins agent.
                            echo.
                            echo Please install Python on the Jenkins server:
                            echo 1. Download from: https://www.python.org/downloads/
                            echo 2. Run installer with "Add Python to PATH" checked
                            echo 3. Restart Jenkins service
                            echo.
                            echo Or specify Python location in Jenkinsfile PYTHON_HOME variable
                            echo.
                            exit /b 1
                        )
                    '''
                }
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                echo '=== Setting up Python Virtual Environment ==='
                bat '''
                    @echo off
                    setlocal enabledelayedexpansion
                    
                    REM Add Python to PATH if needed
                    if exist "C:\\Python311\\python.exe" (
                        set "PATH=C:\\Python311;%PATH%"
                    )
                    
                    REM Remove old venv if exists
                    if exist "%VENV_DIR%" (
                        echo Removing old virtual environment...
                        rmdir /s /q "%VENV_DIR%"
                    )
                    
                    REM Create new virtual environment
                    echo Creating new virtual environment...
                    python -m venv "%VENV_DIR%"
                    
                    if errorlevel 1 (
                        echo ERROR: Failed to create virtual environment
                        exit /b 1
                    )
                    
                    echo Virtual environment created successfully
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
                    
                    REM Upgrade pip
                    echo Upgrading pip...
                    python -m pip install --upgrade pip
                    
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
                    
                    echo Dependencies installed successfully
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
                    
                    call "%VENV_DIR%\\Scripts\\activate.bat"
                    
                    if exist "create_appointments_table.py" (
                        echo Running database initialization script...
                        python create_appointments_table.py
                    ) else (
                        echo Running app initialization...
                        python -c "from app import init_db; init_db(); print('Database initialized')"
                    )
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
            echo '✓ Pipeline completed successfully!'
        }
        failure {
            echo '✗ Pipeline failed!'
        }
    }
}
