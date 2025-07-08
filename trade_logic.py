import asyncio
from datetime import datetime
from strategy import candle_analysis
from utils import get_recent_candles, capture_screenshot
from notification import send_signal_message
from trade_state import get_selected_pair

# Store ongoing user signal loops so they can be cancelled if needed
user_signal_tasks = {}

async def signal_loop(user_id, pair):
    print(f"▶️ Starting signal loop for user {user_id} on pair {pair}")
    candles_count = 4  # 4 candles * 30 seconds = 2 minutes

    try:
        while True:
            # 1. Get candles (simulate 30s candles, 4 total)
            candles = get_recent_candles(pair, candles_count)
            
            # 2. Analyze market
            signal = candle_analysis(candles)
            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            signal["time"] = now_str
            signal["pair"] = pair

            # 3. Check confidence threshold fallback (90% min)
            if signal["confidence"] >= 0.90:
                await send_signal_message(user_id, "✅ Signal detected!", signal=signal)
            else:
                await send_signal_message(user_id, "⚠️ Analyzing market, no strong signal yet...")

            # 4. Capture and send chart screenshot every 30 seconds (simulate candle interval)
            screenshot_path = await capture_screenshot(pair)
            await send_signal_message(user_id, "📊 Chart update:", screenshot_path=screenshot_path)

            # 5. Wait 30 seconds before next candle
            await asyncio.sleep(30)

            # Check if user changed pair or stopped (optional - implement if needed)
            current_pair = get_selected_pair(user_id)
            if current_pair != pair:
                print(f"⏹️ User {user_id} changed pair or stopped. Ending loop.")
                break

    except asyncio.CancelledError:
        print(f"⏹️ Signal loop cancelled for user {user_id}")
    except Exception as e:
        print(f"❌ Error in signal loop for user {user_id}: {e}")

async def start_signal_loop_for_user(user_id, pair):
    # Cancel existing loop for this user if running
    task = user_signal_tasks.get(user_id)
    if task and not task.done():
        task.cancel()

    # Start new loop
    task = asyncio.create_task(signal_loop(user_id, pair))
    user_signal_tasks[user_id] = task

async def continuous_analysis_loop():
    # This can be expanded if you want background continuous analysis for all pairs/users
    # For now, it does nothing but keeps bot alive
    while True:
        await asyncio.sleep(10)
