@echo off
setlocal EnableDelayedExpansion

:: Mirage CLI Tool - mir.bat
:: Version 1.1.1 - Fixed Edition

set VERSION=1.1.1 "eXchange"
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

:: Check PATH status by actually querying the registry
echo Checking PATH status...
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set USER_PATH=%%B
echo !USER_PATH! | find /I "%MIRAGE_DIR%" >nul
if !ERRORLEVEL! EQU 0 (
    echo PATH Status:  Added to User PATH
) else (
    echo PATH Status:  NOT in User PATH - run 'mir path'
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

:: Check PATH by reading registry directly
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set USER_PATH=%%B

:: Check if already in PATH
echo !USER_PATH! | find /I "%MIRAGE_DIR%" >nul
if !ERRORLEVEL! EQU 0 (
    echo Mirage is already in your User PATH!
    echo.
    echo If 'mir' command still doesn't work, close and reopen your terminal.
    exit /b 0
)

echo This will add %MIRAGE_DIR% to your User PATH.
echo You'll be able to run 'mir' from anywhere.
echo.
set /p CONFIRM="Continue? (Y/N): "
if /I not "!CONFIRM!"=="Y" (
    echo Cancelled.
    exit /b 0
)

:: Add to User PATH using setx (more reliable than PowerShell for this)
echo.
echo Adding to PATH...

:: Get current PATH
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set CURRENT_PATH=%%B

:: Check if PATH is empty
if "!CURRENT_PATH!"=="" (
    setx PATH "%MIRAGE_DIR%" >nul 2>&1
) else (
    :: Check if path already ends with semicolon
    if "!CURRENT_PATH:~-1!"==";" (
        setx PATH "!CURRENT_PATH!%MIRAGE_DIR%" >nul 2>&1
    ) else (
        setx PATH "!CURRENT_PATH!;%MIRAGE_DIR%" >nul 2>&1
    )
)

if !ERRORLEVEL! EQU 0 (
    echo.
    echo ========================================
    echo   SUCCESS!
    echo ========================================
    echo.
    echo Mirage has been added to your User PATH.
    echo.
    echo IMPORTANT: Close and reopen your terminal for changes to take effect.
    echo After that, you can run 'mir' from anywhere!
    echo.
    
    :: Verify it was added
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set VERIFY_PATH=%%B
    echo !VERIFY_PATH! | find /I "%MIRAGE_DIR%" >nul
    if !ERRORLEVEL! EQU 0 (
        echo Verification: PATH successfully updated in registry
    ) else (
        echo WARNING: Could not verify PATH update
    )
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR
    echo ========================================
    echo.
    echo Failed to add to PATH. This might happen if:
    echo   - The PATH variable is too long (over 1024 characters)
    echo   - You need administrator privileges
    echo.
    echo Manual instructions:
    echo 1. Press Win+R, type: sysdm.cpl
    echo 2. Go to Advanced tab ^> Environment Variables
    echo 3. Under User variables, edit PATH
    echo 4. Add: %MIRAGE_DIR%
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

:: Files to download (NOT including mir.bat to avoid self-overwrite)
set FILES=mirage.py mirage_editor.py

:: Check if curl is available
where curl >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: curl not found.
    echo Please install curl, or download files manually from GitHub releases:
    echo https://github.com/galaxyg144/MirageOS/releases/latest
    pause
    exit /b 1
)

set DOWNLOAD_FAILED=0

:: Download each file from the latest release
for %%F in (%FILES%) do (
    echo Downloading %%F...
    curl -L -H "User-Agent: MirageCLI" -o "%MIRAGE_DIR%\%%F" "%GITHUB_RELEASE%/%%F" 2>nul

    :: Check if file exists and is not empty
    if exist "%MIRAGE_DIR%\%%F" (
        for %%S in ("%MIRAGE_DIR%\%%F") do (
            if %%~zS GTR 0 (
                echo       SUCCESS - %%F downloaded
            ) else (
                echo       FAILED - %%F is empty
                set DOWNLOAD_FAILED=1
            )
        )
    ) else (
        echo       FAILED - %%F not downloaded
        set DOWNLOAD_FAILED=1
    )
)

echo.
echo ========================================
echo   Download Complete!
echo ========================================
echo.

if !DOWNLOAD_FAILED! GTR 0 (
    echo WARNING: Some files failed to download.
    echo Please check your internet connection or visit:
    echo https://github.com/galaxyg144/MirageOS/releases/latest
    echo.
) else (
    echo All files downloaded successfully!
    echo Files installed to: %MIRAGE_DIR%
    echo.
    echo NOTE: mir.bat was not updated to avoid conflicts.
    echo       To update mir.bat, download it manually from GitHub.
    echo.
    echo You can now run: mir run
    echo.
)

exit /b 0

:DownloadMenu
cls
call :Download
pause
goto :MainMenu

:RunMirage
:: Check if Python is installed
where python >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
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
echo   - Remove Mirage from your User PATH
echo.
echo WARNING: This will NOT delete user data in ~/MirageUsers
echo.
set /p CONFIRM="Are you sure? Type 'yes' to confirm: "
if /I not "!CONFIRM!"=="yes" (
    echo Uninstall cancelled.
    exit /b 0
)

echo.
echo Removing from PATH...

:: Get current PATH from registry
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set CURRENT_PATH=%%B

:: Remove Mirage directory from PATH
set NEW_PATH=!CURRENT_PATH!

:: Replace the Mirage path with nothing (handle with and without semicolons)
set NEW_PATH=!NEW_PATH:%MIRAGE_DIR%;=!
set NEW_PATH=!NEW_PATH:;%MIRAGE_DIR%=!
set NEW_PATH=!NEW_PATH:%MIRAGE_DIR%=!

:: Update PATH if it changed
if not "!NEW_PATH!"=="!CURRENT_PATH!" (
    setx PATH "!NEW_PATH!" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo PATH updated successfully
        
        :: Verify removal
        for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set VERIFY_PATH=%%B
        echo !VERIFY_PATH! | find /I "%MIRAGE_DIR%" >nul
        if !ERRORLEVEL! NEQ 0 (
            echo Verification: Mirage successfully removed from PATH
        ) else (
            echo WARNING: Mirage might still be in PATH
        )
    ) else (
        echo WARNING: Failed to update PATH
    )
) else (
    echo Mirage was not found in PATH
)

echo.
echo Removing Mirage files...
if exist "%MIRAGE_DIR%" (
    rmdir /S /Q "%MIRAGE_DIR%" 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo Files deleted successfully
    ) else (
        echo WARNING: Some files could not be deleted
        echo You may need to delete %MIRAGE_DIR% manually
    )
) else (
    echo No Mirage directory found
)

echo.
echo ========================================
echo   Uninstall Complete
echo ========================================
echo.
echo Mirage has been removed from your system.
echo User data in ~/MirageUsers was preserved.
echo.
echo IMPORTANT: Close and reopen your terminal or run refreshenv for PATH changes to take effect.
echo.
exit /b 0

:UninstallMenu
cls
call :Uninstall
pause
exit /b 0