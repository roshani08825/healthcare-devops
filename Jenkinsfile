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
                    try {
                        bat '''
                            @echo off
                            where python >nul 2>nul
                            if errorlevel 1 (
                                echo Python not found in PATH
                                echo Checking common installation locations...
                                
                                if exist "C:\\Python311\\python.exe" (
                                    echo Found Python at C:\\Python311
                                    set "PATH=C:\\Python311;%PATH%"
                                ) else if exist "C:\\Python310\\python.exe" (
                                    echo Found Python at C:\\Python310
                                    set "PATH=C:\\Python310;%PATH%"
                                ) else if exist "C:\\Program Files\\Python311\\python.exe" (
                                    echo Found Python at C:\\Program Files\\Python311
                                    set "PATH=C:\\Program Files\\Python311;%PATH%"
                                ) else (
                                    echo ERROR: Python not found!
                                    exit /b 1
                                )
                            )
                            python --version
                        '''
                    } catch (Exception e) {
                        error("Failed to locate Python: ${e.message}")
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
