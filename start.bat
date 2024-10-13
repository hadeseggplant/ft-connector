@echo off
set packages=futu-api telethon lunardate pytz datetime asyncio
set "FutuOpenD=Futu OpenD.lnk"
set LOGIN_TG_SCRIPT_NAME="./src/login_telegram.py"
set FT_CONNECTOR_SCRIPT_NAME="./src/ft_connector.py"

echo Start checking and installing Python libraries...
echo:
echo:

for %%i in (%packages%) do (
    pip3 install %%i
)

echo:
echo:
echo Finished checking and installing Python libraries

python %LOGIN_TG_SCRIPT_NAME%
start "" "%FutuOpenD%"
python %FT_CONNECTOR_SCRIPT_NAME%
