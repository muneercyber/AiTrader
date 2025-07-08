from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from utils import capture_screenshot
from trade_logic import start_signal_loop_for_user
from notification import set_bot_application
from trade_state import set_selected_pair, get_selected_pair
import datetime
from config import BOT_TOKEN, ADMIN_ID

users = set()
blocked_users = set()
app: Application = None

main_menu_kb = [
    ["Pairs", "Request Signal"],
    ["History", "Stop"],
    ["Admin Panel"]
]

pair_type_kb = [
    ["Forex", "Crypto"],
    ["🔙 Back"]
]

forex_pairs = [
    "AEDCNY_otc", "AUDCAD_otc", "EURUSD_otc", "GBPJPY_otc", "USDJPY_otc"
]

crypto_pairs = [
    "BTCUSD_otc", "ETHUSD_otc", "DOGEUSD_otc", "AVAXUSD_otc"
]

forex_kb = [[p] for p in forex_pairs] + [["🔙 Back"]]
crypto_kb = [[p] for p in crypto_pairs] + [["🔙 Back"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in blocked_users:
        await update.message.reply_text("⛔ You are blocked by admin.")
        return
    users.add(user_id)
    await update.message.reply_text(
        "🤖 Welcome to P.O Trader Bot!\nUse the buttons below.",
        reply_markup=ReplyKeyboardMarkup(main_menu_kb, resize_keyboard=True)
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Access denied.")
        return
    kb = [["List Users", "Block User"], ["Unblock User"], ["🔙 Back"]]
    await update.message.reply_text("👑 Admin Panel", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def handle_admin_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Admin commands only.")
        return

    if text == "List Users":
        users_list = "\n".join(str(u) for u in users)
        await update.message.reply_text(f"👥 Users:\n{users_list or 'No users yet.'}")
    elif text == "Block User":
        await update.message.reply_text("Send user ID to block:")
        context.user_data['admin_action'] = 'block'
    elif text == "Unblock User":
        await update.message.reply_text("Send user ID to unblock:")
        context.user_data['admin_action'] = 'unblock'
    elif text.isdigit() and 'admin_action' in context.user_data:
        target_id = int(text)
        action = context.user_data.pop('admin_action')
        if action == 'block':
            blocked_users.add(target_id)
            users.discard(target_id)
            await update.message.reply_text(f"User {target_id} blocked.")
        elif action == 'unblock':
            blocked_users.discard(target_id)
            await update.message.reply_text(f"User {target_id} unblocked.")
    elif text == "🔙 Back":
        await update.message.reply_text("Returning to main menu.", reply_markup=ReplyKeyboardMarkup(main_menu_kb, resize_keyboard=True))
    else:
        await update.message.reply_text("Unknown admin command.")

async def general_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in blocked_users:
        await update.message.reply_text("⛔ You are blocked by admin.")
        return

    if text == "Pairs":
        await update.message.reply_text("Select pair type:", reply_markup=ReplyKeyboardMarkup(pair_type_kb, resize_keyboard=True))
    elif text == "Forex":
        await update.message.reply_text("Select a forex pair:", reply_markup=ReplyKeyboardMarkup(forex_kb, resize_keyboard=True))
    elif text == "Crypto":
        await update.message.reply_text("Select a crypto pair:", reply_markup=ReplyKeyboardMarkup(crypto_kb, resize_keyboard=True))
    elif text in forex_pairs + crypto_pairs:
        set_selected_pair(user_id, text)
        await update.message.reply_text(f"✅ Pair selected: {text}\nYou can now request signals.", reply_markup=ReplyKeyboardMarkup(main_menu_kb, resize_keyboard=True))
    elif text == "Request Signal":
        pair = get_selected_pair(user_id)
        if not pair:
            await update.message.reply_text("❗ Please select a trading pair first.", reply_markup=ReplyKeyboardMarkup(main_menu_kb, resize_keyboard=True))
            return
        await update.message.reply_text("📊 Analyzing market, please wait...")
        await start_signal_loop_for_user(user_id, pair)
    elif text == "Stop":
        await update.message.reply_text("⛔ Signal loop stopped for you.")
        # ToDo: implement stop user signal loop cancellation if desired
    elif text == "History":
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        await update.message.reply_text(f"📈 No recent trades.\n🕒 {now}")
    elif text == "Admin Panel":
        await admin_panel(update, context)
    elif user_id == ADMIN_ID:
        await handle_admin_commands(update, context)
    else:
        await update.message.reply_text("❓ Unknown command. Please use the buttons below.", reply_markup=ReplyKeyboardMarkup(main_menu_kb, resize_keyboard=True))

async def start_telegram_bot():
    global app
    app = Application.builder().token(BOT_TOKEN).build()
    set_bot_application(app)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), general_message_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("🤖 Telegram bot started.")
