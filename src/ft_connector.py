from futu import *
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel
from lunardate import LunarDate
import configparser, os, pytz, datetime, re, time, asyncio, multiprocessing

current_dir = os.path.dirname(__file__)
config_file_path = os.path.join(current_dir, "..", "config.ini")
config = configparser.ConfigParser()
config.read(config_file_path)

HTI_QTY = int(config["DEFAULT"]["Hti_Quantity"])
HSIF_QTY = int(config["DEFAULT"]["Hsif_Quantity"])
HSIF_CODE = config["DEFAULT"]["Hsif_Type"]
TG_API_ID = config["DEFAULT"]["Telegram_Api_Id"]
TG_API_HASH = config["DEFAULT"]["Telegram_Api_Hash"]
TG_CHANNEL_ID = int(config["DEFAULT"]["Telegram_Channel_Id"])
FUTU_TRADING_PWD = config["DEFAULT"]["Futu_Trading_Password"]


NORMAL_CLOSE_TIME = datetime.time(2, 54).strftime("%H:%M")
HALF_DAY_CLOSE_TIME = datetime.time(11, 54).strftime("%H:%M")


def trade_number():
    current_time = datetime.datetime.now(pytz.timezone("Asia/Hong_Kong"))

    # Get trade number by date
    trade_date_start = current_time.strftime("20%y-01-01")
    trade_date_end = current_time.strftime("20%y-12-31")

    quote_ctx = OpenQuoteContext()
    ret, trade_date_data = quote_ctx.request_trading_days(
        market=TradeDateMarket.HK,
        start=trade_date_start,
        end=trade_date_end,
    )
    if ret != RET_OK:
        print("error:", trade_date_data)
    quote_ctx.close()

    time_values = re.findall(r"'time': '(\d{4}-\d{2}-\d{2})'", str(trade_date_data))
    time_map = {}
    month_dates = {}
    for time in time_values:
        year_month = time[:7]
        if year_month not in month_dates:
            month_dates[year_month] = []
        month_dates[year_month].append(time)
    for dates in month_dates.values():
        last_three_dates = sorted(dates)[-3:]
        for date in dates:
            if date in last_three_dates:
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                next_month = date_obj.replace(day=28) + timedelta(days=4)
                modified_date = next_month.strftime("%y%m")
                time_map[date] = modified_date
            else:
                time_map[date] = date[2:4] + date[5:7]
    map_data = dict(time_map)

    if datetime.time(0, 0) <= current_time.time() <= datetime.time(3, 0):
        return map_data[(current_time + timedelta(days=-1)).strftime("20%y-%m-%d")]
    else:
        return map_data[current_time.strftime("20%y-%m-%d")]


def reminder_time_diff_til_end():
    now = datetime.datetime.now(pytz.timezone("Asia/Hong_Kong"))
    target_time = pytz.timezone("Asia/Hong_Kong").localize(
        datetime.datetime(now.year, now.month, now.day, 3, 3, 8, 8)
    )
    if now >= target_time:
        target_time += datetime.timedelta(days=1)
    return round((target_time - now).total_seconds())


def hti():
    print(
        "ft-connector started(HTI)...",
        datetime.datetime.now(pytz.timezone("Asia/Hong_Kong")),
    )

    tg_client = TelegramClient("hti_session", TG_API_ID, TG_API_HASH)

    @tg_client.on(events.NewMessage(PeerChannel(channel_id=TG_CHANNEL_ID)))
    async def handle_new_message(event):
        message = event.message

        # Filter HTI signal
        if "系統提交 科指期貨HTI 買盤" in message.text:
            hti_code = "HK.HTI" + trade_number()

            hti_stop_profit_msg = re.search(r"止賺價為(\d+\.\d+)", message.text)
            hti_stop_loss_msg = re.search(r"止蝕價為(\d+\.\d+)", message.text)

            hti_stop_profit_price = round(float(hti_stop_profit_msg.group(1)))
            hti_stop_loss_price = round(float(hti_stop_loss_msg.group(1)))

            trd_ctx = OpenFutureTradeContext()
            quote_ctx = OpenQuoteContext()

            ret, data = trd_ctx.unlock_trade(FUTU_TRADING_PWD)
            if ret == RET_OK:
                ret, data = trd_ctx.position_list_query(
                    code=hti_code,
                    trd_env=TrdEnv.SIMULATE,
                )
                if ret == RET_OK:
                    print(data)
                    if data.shape[0] == 0 or (
                        data.shape[0] > 0 and data["qty"][0] == 0
                    ):
                        # Place HTI call order
                        ret, data = trd_ctx.place_order(
                            price=28,
                            qty=HTI_QTY,
                            code=hti_code,
                            trd_side=TrdSide.BUY,
                            order_type=OrderType.MARKET,
                            trd_env=TrdEnv.SIMULATE,
                        )
                        if ret == RET_OK:
                            print(data)

                            class PriceReminderTest(PriceReminderHandlerBase):
                                def on_recv_rsp(self, rsp_pb):
                                    ret_code, content = super(
                                        PriceReminderTest, self
                                    ).on_recv_rsp(rsp_pb)
                                    if ret_code != RET_OK:
                                        print(
                                            "PriceReminderTest: error, msg: %s"
                                            % content
                                        )
                                        return RET_ERROR, content
                                    print("PriceReminderTest ", content)

                                    # Place HTI stop profit/stop loss order
                                    if content["code"] == hti_code:
                                        # Delete all related reminder
                                        quote_ctx.set_price_reminder(
                                            code=hti_code,
                                            op=SetPriceReminderOp.DEL_ALL,
                                        )

                                        ret, data = trd_ctx.position_list_query(
                                            code=hti_code,
                                            trd_env=TrdEnv.SIMULATE,
                                        )
                                        if ret == RET_OK:
                                            print(data)
                                            if data.shape[0] > 0 and data["qty"][0] > 0:
                                                ret, data = trd_ctx.place_order(
                                                    price=28,
                                                    qty=data["qty"][0],
                                                    code=hti_code,
                                                    trd_side=TrdSide.SELL,
                                                    order_type=OrderType.MARKET,
                                                    trd_env=TrdEnv.SIMULATE,
                                                )
                                                if ret == RET_OK:
                                                    print(data)
                                                    print(
                                                        "Finished "
                                                        + hti_code
                                                        + " trade:",
                                                        datetime.datetime.now(
                                                            pytz.timezone(
                                                                "Asia/Hong_Kong"
                                                            )
                                                        ),
                                                    )
                                                else:
                                                    print("place_order error: ", data)
                                        else:
                                            print("position_list_query error: ", data)
                                    return RET_OK, content

                            handler = PriceReminderTest()
                            quote_ctx.set_handler(handler)

                            # Set HTI stop profit reminder
                            ret_stop_profit, stop_profit_data = (
                                quote_ctx.set_price_reminder(
                                    code=hti_code,
                                    op=SetPriceReminderOp.ADD,
                                    key=None,
                                    reminder_type=PriceReminderType.PRICE_UP,
                                    reminder_freq=PriceReminderFreq.ONCE,
                                    value=hti_stop_profit_price,
                                )
                            )
                            if ret_stop_profit == RET_OK:
                                print(
                                    "Set HTI stop profit reminder successfully:",
                                    hti_stop_profit_price,
                                )
                            else:
                                print("error:", stop_profit_data)

                            # Set HTI stop loss reminder
                            ret_stop_loss, stop_loss_data = (
                                quote_ctx.set_price_reminder(
                                    code=hti_code,
                                    op=SetPriceReminderOp.ADD,
                                    key=None,
                                    reminder_type=PriceReminderType.PRICE_DOWN,
                                    reminder_freq=PriceReminderFreq.ONCE,
                                    value=hti_stop_loss_price,
                                )
                            )
                            if ret_stop_loss == RET_OK:
                                print(
                                    "Set HTI stop loss reminder successfully:",
                                    hti_stop_loss_price,
                                )
                            else:
                                print("error:", stop_loss_data)
                            await asyncio.sleep(reminder_time_diff_til_end())

                            # Delete all related reminder
                            quote_ctx.set_price_reminder(
                                code=hti_code,
                                op=SetPriceReminderOp.DEL_ALL,
                            )
                        else:
                            print("place_order error: ", data)
                else:
                    print("position_list_query error: ", data)
            else:
                print("unlock_trade failed: ", data)

            trd_ctx.close()
            quote_ctx.close()

    # Start the client and run the event loop
    tg_client.start()
    tg_client.run_until_disconnected()


def hsif():
    print(
        "ft-connector started(HSIF)...",
        datetime.datetime.now(pytz.timezone("Asia/Hong_Kong")),
    )

    tg_client = TelegramClient("hsif_session", TG_API_ID, TG_API_HASH)

    @tg_client.on(events.NewMessage(PeerChannel(channel_id=TG_CHANNEL_ID)))
    async def handle_new_message(event):
        message = event.message

        # Filter HSIF signal
        if "系統提交 恆指期貨HSIF 沽盤" in message.text:
            hsif_trade_number = trade_number()

            hsif_stop_profit_msg = re.search(r"止賺價為(\d+\.\d+)", message.text)
            hsif_stop_loss_msg = re.search(r"止蝕價為(\d+\.\d+)", message.text)

            hsif_stop_profit_price = round(float(hsif_stop_profit_msg.group(1)))
            hsif_stop_loss_price = round(float(hsif_stop_loss_msg.group(1)))

            trd_ctx = OpenFutureTradeContext()
            quote_ctx = OpenQuoteContext()

            ret, data = trd_ctx.unlock_trade(FUTU_TRADING_PWD)
            if ret == RET_OK:
                ret, data = trd_ctx.position_list_query(
                    code=HSIF_CODE + hsif_trade_number,
                    trd_env=TrdEnv.SIMULATE,
                )
                if ret == RET_OK:
                    print(data)
                    if data.shape[0] == 0 or (
                        data.shape[0] > 0 and data["qty"][0] == 0
                    ):
                        # Place HSIF put order
                        ret, data = trd_ctx.place_order(
                            price=28,
                            qty=HSIF_QTY,
                            code=HSIF_CODE + hsif_trade_number,
                            trd_side=TrdSide.SELL,
                            order_type=OrderType.MARKET,
                            trd_env=TrdEnv.SIMULATE,
                        )
                        if ret == RET_OK:
                            print(data)

                            class PriceReminderTest(PriceReminderHandlerBase):
                                def on_recv_rsp(self, rsp_pb):
                                    ret_code, content = super(
                                        PriceReminderTest, self
                                    ).on_recv_rsp(rsp_pb)
                                    if ret_code != RET_OK:
                                        print(
                                            "PriceReminderTest: error, msg: %s"
                                            % content
                                        )
                                        return RET_ERROR, content
                                    print("PriceReminderTest ", content)

                                    # Place HSIF stop profit/stop loss order
                                    if content["code"] == "HK.HSI" + hsif_trade_number:
                                        # Delete all related reminder
                                        quote_ctx.set_price_reminder(
                                            code="HK.HSI" + hsif_trade_number,
                                            op=SetPriceReminderOp.DEL_ALL,
                                        )

                                        ret, data = trd_ctx.position_list_query(
                                            code=HSIF_CODE + hsif_trade_number,
                                            trd_env=TrdEnv.SIMULATE,
                                        )
                                        if ret == RET_OK:
                                            print(data)
                                            if data.shape[0] > 0 and data["qty"][0] < 0:
                                                ret, data = trd_ctx.place_order(
                                                    price=28,
                                                    qty=data["qty"][0] * -1,
                                                    code=HSIF_CODE + hsif_trade_number,
                                                    trd_side=TrdSide.BUY,
                                                    order_type=OrderType.MARKET,
                                                    trd_env=TrdEnv.SIMULATE,
                                                )
                                                if ret == RET_OK:
                                                    print(data)
                                                    print(
                                                        "Finished "
                                                        + HSIF_CODE
                                                        + hsif_trade_number
                                                        + " trade:",
                                                        datetime.datetime.now(
                                                            pytz.timezone(
                                                                "Asia/Hong_Kong"
                                                            )
                                                        ),
                                                    )
                                                else:
                                                    print("place_order error: ", data)
                                        else:
                                            print("position_list_query error: ", data)
                                    return RET_OK, content

                            handler = PriceReminderTest()
                            quote_ctx.set_handler(handler)

                            # Set HSIF stop profit reminder
                            ret_stop_profit, stop_profit_data = (
                                quote_ctx.set_price_reminder(
                                    code="HK.HSI" + hsif_trade_number,
                                    op=SetPriceReminderOp.ADD,
                                    key=None,
                                    reminder_type=PriceReminderType.PRICE_DOWN,
                                    reminder_freq=PriceReminderFreq.ONCE,
                                    value=hsif_stop_profit_price,
                                )
                            )
                            if ret_stop_profit == RET_OK:
                                print(
                                    "Set HSIF stop profit reminder successfully:",
                                    hsif_stop_profit_price,
                                )
                            else:
                                print("error:", stop_profit_data)

                            # Set HSIF stop loss reminder
                            ret_stop_loss, stop_loss_data = (
                                quote_ctx.set_price_reminder(
                                    code="HK.HSI" + hsif_trade_number,
                                    op=SetPriceReminderOp.ADD,
                                    key=None,
                                    reminder_type=PriceReminderType.PRICE_UP,
                                    reminder_freq=PriceReminderFreq.ONCE,
                                    value=hsif_stop_loss_price,
                                )
                            )
                            if ret_stop_loss == RET_OK:
                                print(
                                    "Set HSIF stop loss reminder successfully:",
                                    hsif_stop_loss_price,
                                )
                            else:
                                print("error:", stop_loss_data)
                            await asyncio.sleep(reminder_time_diff_til_end())

                            # Delete all related reminder
                            quote_ctx.set_price_reminder(
                                code="HK.HSI" + hsif_trade_number,
                                op=SetPriceReminderOp.DEL_ALL,
                            )
                        else:
                            print("place_order error: ", data)
                else:
                    print("position_list_query error: ", data)
            else:
                print("unlock_trade failed: ", data)

            trd_ctx.close()
            quote_ctx.close()

    # Start the client and run the event loop
    tg_client.start()
    tg_client.run_until_disconnected()


def close_position():
    while True:
        current_time = datetime.datetime.now(pytz.timezone("Asia/Hong_Kong"))

        lunar_date = LunarDate.fromSolarDate(
            current_time.year, current_time.month, current_time.day
        )
        try:
            ninsaamsap = LunarDate(lunar_date.year, 12, 30).toSolarDate()
        except Exception as e:
            ninsaamsap = LunarDate(lunar_date.year, 12, 29).toSolarDate()

        half_dates = {
            datetime.date(current_time.year, 12, 24),
            datetime.date(current_time.year, 12, 31),
            ninsaamsap,
        }

        if (
            current_time.date() in half_dates
            and current_time.time().strftime("%H:%M") == HALF_DAY_CLOSE_TIME
        ) or current_time.time().strftime("%H:%M") == NORMAL_CLOSE_TIME:
            trd_ctx = OpenFutureTradeContext()
            quote_ctx = OpenQuoteContext()

            ret, data = trd_ctx.unlock_trade(FUTU_TRADING_PWD)
            if ret == RET_OK:
                ret, position_data = trd_ctx.position_list_query(
                    trd_env=TrdEnv.SIMULATE,
                )
                if ret == RET_OK:
                    print(position_data)
                    if position_data.shape[0] > 0:
                        for i in range(position_data.shape[0]):
                            # Delete all related reminder
                            quote_ctx.set_price_reminder(
                                code=position_data["code"][i],
                                op=SetPriceReminderOp.DEL_ALL,
                            )

                            # Place close long position order
                            if (
                                position_data["position_side"][i] == PositionSide.LONG
                                and position_data["qty"][i] > 0
                            ):
                                ret, data = trd_ctx.place_order(
                                    price=28,
                                    qty=position_data["qty"][i],
                                    code=position_data["code"][i],
                                    trd_side=TrdSide.SELL,
                                    order_type=OrderType.MARKET,
                                    trd_env=TrdEnv.SIMULATE,
                                )
                                if ret == RET_OK:
                                    print(data)
                                    print(
                                        "Finished "
                                        + position_data["code"][i]
                                        + " trade:",
                                        current_time,
                                    )
                                else:
                                    print("place_order error: ", data)
                            # Place close short position order
                            elif (
                                position_data["position_side"][i] == PositionSide.SHORT
                                and position_data["qty"][i] < 0
                            ):
                                ret, data = trd_ctx.place_order(
                                    price=28,
                                    qty=position_data["qty"][i] * -1,
                                    code=position_data["code"][i],
                                    trd_side=TrdSide.BUY,
                                    order_type=OrderType.MARKET,
                                    trd_env=TrdEnv.SIMULATE,
                                )
                                if ret == RET_OK:
                                    print(data)
                                    print(
                                        "Finished "
                                        + position_data["code"][i]
                                        + " trade:",
                                        current_time,
                                    )
                                else:
                                    print("place_order error: ", data)
                else:
                    print("position_list_query error: ", position_data)
            else:
                print("unlock_trade failed: ", data)

            trd_ctx.close()
            quote_ctx.close()

        time.sleep(30)


if __name__ == "__main__":
    process1 = multiprocessing.Process(target=hti)
    process2 = multiprocessing.Process(target=hsif)
    process3 = multiprocessing.Process(target=close_position)

    process1.start()
    process2.start()
    process3.start()

    while True:
        pass
