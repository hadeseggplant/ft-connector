@echo off
setlocal enabledelayedexpansion

set packages=futu-api telethon lunardate pytz datetime asyncio
set "FutuOpenD=Futu OpenD.lnk"
set LOGIN_TG_SCRIPT_NAME="./src/login_telegram.py"
set FT_CONNECTOR_SCRIPT_NAME="./src/ft_connector.py"

echo Start checking and installing Python libraries...
echo:

for %%i in (%packages%) do (
    pip3 show %%i >nul 2>&1
    if errorlevel 1 (
        echo Installing %%i...
        pip3 install %%i
    ) else (
        echo %%i is already installed.
    )
)

echo:
echo Finished checking and installing Python libraries

python %LOGIN_TG_SCRIPT_NAME%
start "" "%FutuOpenD%"
python %FT_CONNECTOR_SCRIPT_NAME%

endlocal
