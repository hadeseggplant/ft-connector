# ft-connector

## 免責聲明
「本程式碼 `ft-connector` ﹝下稱本程式﹞」目的為提供學習電腦編程資訊及牛牛API應用學術研究，非供交易或投資之目的，因此請勿使用於真實交易帳戶，請使用於模擬帳戶。透過「本程式」獲得之資料僅作為參考，非供使用者之投資買賣建議，也並不構成投資意見，亦不應被視為任何投資或贖回之招引。使用者在進行投資決策前，應審慎評估或先行諮詢專業人士，自行決定是否使用「本程式」所提供的程式碼，使用者應自行判斷與承擔風險。任何依賴「本程式」提供之程式碼自行作出交易，本研發者恕不負擔任何盈虧及法律責任，請在使用「本程式」及投資決策前謹慎評估風險。

另請參閱以下聲明：
 - https://www.futuhk.com/about/disclaimer
 - https://www.futuhk.com/about/portfolio-agreement
 - https://github.com/hadeseggplant/ft-connector?tab=Apache-2.0-1-ov-file


## User Guide


#### 1. 下載最新版 `ft-connector`：https://github.com/hadeseggplant/ft-connector/releases
- 按 `Source code (zip)`
- 下載後解壓縮


#### 2. 安裝Python 3.11：https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
- 請勾選最底的 `Add python.exe to PATH` 再按安裝
- 如安裝library時出現error，請[開啟cmd](https://blog.miniasp.com/post/2017/09/06/Windows-Explorer-tips-open-cmd-and-VSCode-quickly)輸入 `python -V` 檢查是否安裝了非3.11版本，牛牛API目前只支援至此版本


#### 3. 申請Telegram API token：https://my.telegram.org
- 登入後按 `API development tools`
- `App title` 和 `Short name` 可隨意輸入
- Generate後記低 `App api_id` 和 `App api_hash`


#### 4. 用Notepad開啟 `config.ini` ，輸入以下參數後儲存：
- `Hti_Quantity`：HTI張數
- `Hsif_Quantity`：HSIF張數
- `Hsif_Type`：選擇HSIF大/細期，大期輸入 `HK.HSI`，細期輸入 `HK.MHI`
- `Telegram_Api_Id`：App api_id
- `Telegram_Api_Hash`：App api_hash
- `Telegram_Channel_Id`：登入 https://web.telegram.org/ ，按一下Channel，URL***最後10位***數字就是Channel ID
- `Futu_Trading_Password`：牛牛***6位***數字的交易密碼
- `Trade_Environment`：模擬交易輸入 `SIMULATE`，真實交易輸入 `REAL` (只提供設定參考，請再三閱讀[免責聲明](https://github.com/hadeseggplant/ft-connector?tab=readme-ov-file#%E5%85%8D%E8%B2%AC%E8%81%B2%E6%98%8E)再決定使用)


#### 5. 下載Futu OpenD：https://www.futunn.com/download/fetch-lasted-link?name=opend-windows
- 解壓縮後開啟帶有 `GUI` 的資料夾進行安裝
- 完成後把 `Futu OpenD` 的 ***捷徑*** 放到 `/ft-connector/` 資料夾內


#### 6. 點擊 `start.bat`，系統會先安裝Python library
```
Start checking and installing Python libraries...
...
...
...
Finished checking and installing Python libraries
```


#### 7. 然後系統會要求登入Telegram`兩次`(HTI和HSIF)，順序輸入`兩次`：
- 電話號碼(連+852)
- Login code(會發送至Telegram官方通知)
- 登入Telegram的密碼(如有)


#### 8. 成功執行後會出現：
```
ft-connector started(HTI)...
ft-connector started(HSIF)...
```


#### 9. `Futu OpenD` 會同時啟動，以牛牛帳戶登錄 `Futu OpenD`
- 建議勾選 ***記住密碼*** 及 ***自動登錄***，右邊設置不用更改任何數值


#### 10. 完成一次以上設定後，以後直接點擊 `start.bat` 便會自動運行 `ft-connector` 和 `Futu OpenD`


#### 11. 如擔心Windows自動更新影響運作，請自行更改系統更新時間，並可參考[此文章](https://ithelp.ithome.com.tw/questions/10198372)將 `ft-connector` 設定成開機時自動啟動
- 注意：請先把 `start.bat` 建立捷徑(右鍵 -> 建立捷徑)，再將 ***捷徑*** 放入 `/啟動/` 資料夾，不要把 `/ft-connector/` 資料夾內的 `start.bat` 直接拉過去


## References
- https://openapi.futunn.com/futu-api-doc/intro/intro.html
- https://docs.telethon.dev/en/stable/
