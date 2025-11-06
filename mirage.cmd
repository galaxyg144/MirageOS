@echo off
setlocal EnableDelayedExpansion

:: Mirage CLI Tool - mir.bat
:: Version 1.0.0

set VERSION=1.0.0
set MIRAGE_DIR=%USERPROFILE%\.mirage
set GITHUB_RELEASE=https://github.com/galaxyg144/MirageOS/releases/latest/download

:: Check if script is in PATH, if not offer to add it
if not exist "%MIRAGE_DIR%" (
    call :FirstTimeSetup
    goto :MainMenu
)

:: Parse command line arguments - if empty, show menu
if "%~1"=="" goto :MainMenu
if /I "%~1"=="run" goto :RunMirage
if /I "%~1"=="-v" goto :ShowVersion
if /I "%~1"=="--version" goto :ShowVersion
if /I "%~1"=="version" goto :ShowVersion
if /I "%~1"=="download" goto :Download
if /I "%~1"=="update" goto :Download
if /I "%~1"=="install" goto :Download
if /I "%~1"=="uninstall" goto :Uninstall
if /I "%~1"=="help" goto :ShowHelp
if /I "%~1"=="-h" goto :ShowHelp
if /I "%~1"=="--help" goto :ShowHelp
if /I "%~1"=="path" goto :AddToPath
if /I "%~1"=="info" goto :ShowInfo

echo Unknown command: %~1
echo Type 'mir help' for usage information
exit /b 1

:MainMenu
cls
echo.
echo  __  __ _                        
echo ^|  \/  (_)_ __ __ _  __ _  ___ 
echo ^| ^|\/^| ^| ^| '__/ _` ^|/ _` ^|/ _ \
echo ^| ^|  ^| ^| ^| ^| ^| (_^| ^| (_^| ^|  __/
echo ^|_^|  ^|_^|_^|_^|  \__,_^|\__, ^|\_^|
echo                     ^|___/      
echo.
echo Mirage OS Manager v%VERSION%
echo ================================
echo.
echo [1] Run Mirage OS
echo [2] Download/Update Mirage Files
echo [3] Add Mirage to System PATH
echo [4] Installation Information
echo [5] Uninstall Mirage
echo [6] Help
echo [0] Exit
echo.
set /p choice="Enter your choice: "

if "%choice%"=="1" goto :RunMirageMenu
if "%choice%"=="2" goto :DownloadMenu
if "%choice%"=="3" goto :AddToPathMenu
if "%choice%"=="4" goto :ShowInfoMenu
if "%choice%"=="5" goto :UninstallMenu
if "%choice%"=="6" goto :ShowHelpMenu
if "%choice%"=="0" exit /b 0

echo.
echo Invalid choice! Please try again.
timeout /t 2 >nul
goto :MainMenu

:ShowHelp
echo.
echo  __  __ _                        
echo ^|  \/  (_)_ __ __ _  __ _  ___ 
echo ^| ^|\/^| ^| ^| '__/ _` ^|/ _` ^|/ _ \
echo ^| ^|  ^| ^| ^| ^| ^| (_^| ^| (_^| ^|  __/
echo ^|_^|  ^|_^|_^|_^|  \__,_^|\__, ^|\_^|
echo                     ^|___/      
echo.
echo Mirage OS Command Line Interface v%VERSION%
echo.
echo Usage: mir [command]
echo.
echo Commands:
echo   run          - Launch Mirage OS
echo   download     - Download/update Mirage files from GitHub
echo   install      - Same as download
echo   update       - Same as download
echo   version      - Show Mirage version
echo   -v           - Show Mirage version
echo   info         - Show installation information
echo   path         - Add mir to system PATH
echo   uninstall    - Remove Mirage from your system
echo   help         - Show this help message
echo.
echo Examples:
echo   mir run          Start Mirage OS
echo   mir download     Download latest version from GitHub
echo   mir -v           Display version
echo.
echo Note: Running 'mir' without arguments opens the interactive menu.
echo.
exit /b 0

:ShowHelpMenu
cls
call :ShowHelp
pause
goto :MainMenu

:ShowVersion
echo Mirage Version %VERSION%
exit /b 0

:ShowInfo
echo.
echo ================================
echo Mirage OS Installation Info
echo ================================
echo Version:      %VERSION%
echo Install Dir:  %MIRAGE_DIR%
echo Python:       %MIRAGE_DIR%\mirage.py
echo Editor:       %MIRAGE_DIR%\mirage_editor.py
echo.
if exist "%MIRAGE_DIR%\mirage.py" (
    echo Status:       Installed
) else (
    echo Status:       Not installed - run 'mir download'
)
echo.
exit /b 0

:ShowInfoMenu
cls
call :ShowInfo
pause
goto :MainMenu

:FirstTimeSetup
cls
echo.
echo ========================================
echo   Mirage OS - First Time Setup
echo ========================================
echo.
echo Creating Mirage directory at:
echo %MIRAGE_DIR%
echo.
mkdir "%MIRAGE_DIR%" 2>nul

:: Copy mir.bat to Mirage directory
echo Copying mir.bat to installation directory...
copy /Y "%~f0" "%MIRAGE_DIR%\mir.bat" >nul

echo.
echo Setup complete!
echo.
echo Next steps:
echo   1. Run 'mir path' to add mir to your PATH
echo   2. Run 'mir download' to get Mirage files
echo   3. Run 'mir run' to start Mirage
echo.
pause
exit /b 0

:AddToPath
echo.
echo ========================================
echo   Adding Mirage to System PATH
echo ========================================
echo.

:: Check if already in PATH
echo %PATH% | find /I "%MIRAGE_DIR%" >nul
if %ERRORLEVEL% EQU 0 (
    echo Mirage is already in your PATH!
    exit /b 0
)

echo This will add %MIRAGE_DIR% to your system PATH.
echo You'll be able to run 'mir' from anywhere.
echo.
set /p CONFIRM="Continue? (Y/N): "
if /I not "!CONFIRM!"=="Y" (
    echo Cancelled.
    exit /b 0
)

:: Add to User PATH using PowerShell
powershell -Command "$currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User'); if ($currentPath -notlike '*%MIRAGE_DIR%*') { [Environment]::SetEnvironmentVariable('PATH', $currentPath + ';%MIRAGE_DIR%', 'User') }"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Mirage has been added to your PATH.
    echo.
    echo IMPORTANT: Close and reopen your terminal for changes to take effect.
    echo After that, you can run 'mir' from anywhere!
    echo.
) else (
    echo.
    echo ERROR: Failed to add to PATH. You may need administrator privileges.
    echo.
    echo Manual instructions:
    echo 1. Open System Properties ^> Environment Variables
    echo 2. Edit the PATH variable for your user
    echo 3. Add: %MIRAGE_DIR%
    echo.
)
exit /b 0

:AddToPathMenu
cls
call :AddToPath
pause
goto :MainMenu

:Download
echo.
echo ========================================
echo   Downloading Latest Mirage Release
echo ========================================
echo.

if not exist "%MIRAGE_DIR%" mkdir "%MIRAGE_DIR%"

:: Files to download
set FILES=mirage.py mirage_editor.py

:: Check if curl is available
where curl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: curl not found.
    echo Please install curl, or download files manually from GitHub releases:
    echo https://github.com/galaxyg144/MirageOS/releases/latest
    pause
    exit /b 1
)

:: Download each file from the latest release
for %%F in (%FILES%) do (
    echo Downloading %%F...
    curl -L -H "User-Agent: MirageCLI" -o "%MIRAGE_DIR%\%%F" "%GITHUB_RELEASE%/%%F"

    :: Check if file exists and is not empty
    if exist "%MIRAGE_DIR%\%%F" (
        for %%S in ("%MIRAGE_DIR%\%%F") do if %%~zS NEQ 0 (
            echo       SUCCESS - %%F downloaded
        ) else (
            echo       FAILED - %%F is empty
            echo       Please check the latest release on GitHub
        )
    ) else (
        echo       FAILED - %%F not downloaded
        echo       Please check the latest release on GitHub
    )
)

echo.
echo ========================================
echo   Download Complete!
echo ========================================
echo.
echo Files installed to: %MIRAGE_DIR%
echo.
echo You can now run: mir run
echo.
exit /b 0

:DownloadMenu
cls
call :Download
pause
goto :MainMenu

:RunMirage
:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    exit /b 1
)

:: Check if mirage.py exists
if not exist "%MIRAGE_DIR%\mirage.py" (
    echo ERROR: mirage.py not found!
    echo Run 'mir download' to install Mirage files.
    exit /b 1
)

:: Run Mirage
echo Running Mirage OS...
echo.
python "%MIRAGE_DIR%\mirage.py"
exit /b 0

:RunMirageMenu
cls
call :RunMirage
echo.
echo Mirage OS exited.
pause
goto :MainMenu

:Uninstall
echo.
echo ========================================
echo   Uninstall Mirage OS
echo ========================================
echo.
echo This will:
echo   - Delete %MIRAGE_DIR%
echo   - Remove Mirage from your PATH
echo.
echo WARNING: This will NOT delete user data in ~/MirageUsers
echo.
set /p CONFIRM="Are you sure? (yes/no): "
if /I not "!CONFIRM!"=="yes" (
    echo Uninstall cancelled.
    exit /b 0
)

echo.
echo Removing Mirage files...
if exist "%MIRAGE_DIR%" (
    rmdir /S /Q "%MIRAGE_DIR%"
    echo Files deleted.
)

echo Removing from PATH...
powershell -Command "$currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User'); $newPath = ($currentPath -split ';' | Where-Object { $_ -ne '%MIRAGE_DIR%' }) -join ';'; [Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')"

echo.
echo ========================================
echo   Uninstall Complete
echo ========================================
echo.
echo Mirage has been removed from your system.
echo User data in ~/MirageUsers was preserved.
echo.
echo Close and reopen your terminal for PATH changes to take effect.
echo.
exit /b 0

:UninstallMenu
cls
call :Uninstall
pause
exit /b 0
