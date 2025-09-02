# Filename: mt5_buy_stop.py

import MetaTrader5 as mt5
import time

# ---------------- USER SETTINGS ----------------
symbol = "XAUUSD_"          # Your trading symbol in MT5
buy_target = 3482.50        # Price to trigger Buy Stop
volume = 0.01               # Lot size
deviation = 20              # Max slippage in points
magic_number = 123456       # Unique ID for your orders
check_interval = 0.1        # Seconds between price checks
# ------------------------------------------------

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    quit()

print(f"Monitoring {symbol} for Buy ≥ {buy_target}")

while True:
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        time.sleep(check_interval)
        continue

    buy_price = tick.ask
    print(f"Buy (Ask): {buy_price:.2f}")

    if buy_price >= buy_target:
        print(f"Target reached: {buy_price:.2f}. Sending Buy Stop order...")

        request = {
            "action": mt5.TRADE_ACTION_PENDING,   # Pending order
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY_STOP,      # Buy Stop order
            "price": buy_price,                   # Place at current price
            "sl": 0.0,                            # Optional: Stop Loss
            "tp": 0.0,                            # Optional: Take Profit
            "deviation": deviation,
            "magic": magic_number,
            "comment": "Auto Buy Stop",
            "type_time": mt5.ORDER_TIME_GTC,      # Good till cancelled
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed: {result.retcode}")
        else:
            print(f"Buy Stop placed successfully at {buy_price:.2f}")
        break

    time.sleep(check_interval)

mt5.shutdown()
