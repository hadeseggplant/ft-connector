from telethon import TelegramClient
import configparser, os

current_dir = os.path.dirname(__file__)
config_file_path = os.path.join(current_dir, '..', 'config.ini')
config = configparser.ConfigParser()
config.read(config_file_path)

TG_API_ID = int(config["DEFAULT"]["Telegram_Api_Id"])
TG_API_HASH = config['DEFAULT']['Telegram_Api_Hash']

tg_client = TelegramClient("hti_session", TG_API_ID, TG_API_HASH)
tg_client.start()
tg_client.disconnect()

tg_client = TelegramClient("hsif_session", TG_API_ID, TG_API_HASH)
tg_client.start()
tg_client.disconnect()
