from telegram import InputFile

app = None

def set_bot_application(bot_app):
    global app
    app = bot_app

async def send_signal_message(user_id, message: str, screenshot_path: str = None, signal: dict = None):
    if not app:
        return

    if signal:
        text = (
            f"📢 *Signal Alert!*\n"
            f"Pair: `{signal.get('pair')}`\n"
            f"Direction: *{signal.get('direction').upper()}*\n"
            f"Confidence: `{signal.get('confidence') * 100:.2f}%`\n"
            f"Time: `{signal.get('time')}`"
        )
        await app.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")

    await app.bot.send_message(chat_id=user_id, text=message)

    if screenshot_path:
        with open(screenshot_path, "rb") as img:
            await app.bot.send_photo(chat_id=user_id, photo=InputFile(img))
