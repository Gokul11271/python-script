import MetaTrader5 as mt5
import time
from datetime import datetime

# ------------------- Config ------------------- #
SYMBOL = "XAUUSD_"       # Trading symbol
INIT_VOLUME = 0.05        # Initial order volume
NEXT_VOLUME = 0.01        # Following orders volume
SLIPPAGE = 50
MAGIC = 12345

# ------------------- Init ------------------- #
if not mt5.initialize():
    print("❌ Initialize() failed, error code =", mt5.last_error())
    quit()

print("✅ MT5 Initialized")

if not mt5.symbol_select(SYMBOL, True):
    print(f"❌ Failed to select symbol {SYMBOL}")
    mt5.shutdown()
    quit()

print(f"✅ Symbol {SYMBOL} selected")

symbol_info = mt5.symbol_info(SYMBOL)
point = symbol_info.point
stop_level = symbol_info.trade_stops_level * point

# Volume limits
vol_min = symbol_info.volume_min
vol_step = symbol_info.volume_step
vol_max = symbol_info.volume_max

def normalize_volume(vol):
    """Ensure volume is within broker limits."""
    steps = round((vol - vol_min) / vol_step)
    normalized = vol_min + steps * vol_step
    return max(vol_min, min(normalized, vol_max))

# ------------------- Helpers ------------------- #
def cancel_all_pending():
    """Cancel all pending orders for the symbol."""
    orders = mt5.orders_get(symbol=SYMBOL)
    if orders:
        for o in orders:
            mt5.order_send({"action": mt5.TRADE_ACTION_REMOVE, "order": o.ticket})
        print(f"🗑️ Cleared {len(orders)} pending orders.")

def place_order(order_type, base_price, volume):
    """Place a BUY STOP or SELL STOP order, retry until success."""
    cancel_all_pending()
    attempt = 0
    volume = normalize_volume(volume)

    while True:
        attempt += 1
        tick = mt5.symbol_info_tick(SYMBOL)
        if not tick:
            print("❌ No tick data, retrying...")
            time.sleep(1)
            continue

        if order_type == "BUY":
            min_price = tick.ask + stop_level + (2 * point)
            price = max(base_price, min_price)
            mt_type = mt5.ORDER_TYPE_BUY_STOP
        else:
            max_price = tick.bid - stop_level - (2 * point)
            price = min(base_price, max_price)
            mt_type = mt5.ORDER_TYPE_SELL_STOP

        price = round(price, symbol_info.digits)

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": SYMBOL,
            "volume": volume,
            "type": mt_type,
            "price": price,
            "deviation": SLIPPAGE,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "type_time": mt5.ORDER_TIME_GTC,
            "comment": f"Cyclic {order_type} STOP",
            "magic": MAGIC,
        }

        result = mt5.order_send(request)
        if result is None:
            print(f"❌ order_send() returned None, last_error = {mt5.last_error()}, retrying...")
            time.sleep(1)
            continue

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {order_type} STOP placed at {price} (vol={volume}, attempt {attempt})")
            return price
        else:
            print(f"⚠️ {order_type} STOP rejected (Retcode {result.retcode}), retrying...")
            time.sleep(1)

# ------------------- User Input ------------------- #
tick = mt5.symbol_info_tick(SYMBOL)
base_ask = tick.ask
options = [round(base_ask + i * point * 10, symbol_info.digits) for i in range(1, 3 + 1)]

print("\n👉 Choose starting BUY STOP price:")
for i, val in enumerate(options, 1):
    print(f"{i}. {val}")

choice = input("Enter choice (1/2/3 or custom price): ").strip()
if choice in ["1", "2", "3"]:
    buy_price = options[int(choice) - 1]
else:
    buy_price = float(choice)

gap = float(input("Enter gap (distance between BUY and SELL): "))

print(f"🚀 Starting cycle with BUY STOP at {buy_price}, gap = {gap}")
active_price = place_order("BUY", buy_price, INIT_VOLUME)
last_order_type = "BUY"

# ------------------- Cycle Loop ------------------- #
try:
    print("\n🔄 Monitoring orders... Press Ctrl+C to stop.")
    while True:
        positions = mt5.positions_get(symbol=SYMBOL)

        if positions:
            # Take the most recent position
            pos = sorted(positions, key=lambda p: p.time)[-1]

            if last_order_type == "BUY" and pos.type == mt5.POSITION_TYPE_BUY:
                # BUY filled → place SELL STOP
                sell_price = round(active_price - gap, symbol_info.digits)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔔 BUY triggered → SELL STOP {sell_price}")
                active_price = place_order("SELL", sell_price, NEXT_VOLUME)
                last_order_type = "SELL"

            elif last_order_type == "SELL" and pos.type == mt5.POSITION_TYPE_SELL:
                # SELL filled → place BUY STOP
                buy_price = round(active_price + gap, symbol_info.digits)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔔 SELL triggered → BUY STOP {buy_price}")
                active_price = place_order("BUY", buy_price, NEXT_VOLUME)
                last_order_type = "BUY"

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Script stopped by user.")
finally:
    mt5.shutdown()
