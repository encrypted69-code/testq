import json
import datetime
import traceback
import razorpay
from telegram import (
    ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
)

TELEGRAM_TOKEN = "8178112693:AAGVpmXWL6jZ6NRr_a5bRDSdzagcILldaww"
ADMIN_CONTACT = "https://t.me/ottsonly1"
ADMIN_IDS = [7127370646, 7378307078]
LOGS_CHANNEL_ID = -4758912978

# Razorpay Configuration
RAZORPAY_KEY_ID = "rzp_live_eDOWuCgYGroIuq"  # Replace with your actual key
RAZORPAY_KEY_SECRET = "tXKuwMO6ScQUkVpidQSqjf2V"  # Replace with your actual secret

razor = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

WALLET_FILE = "wallets.json"
OTT_FILE = "otts.json"
USERS_FILE = "users.json"
STOCK_FILE = "stock.json"

def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def get_balance(user_id):
    wallets = load_json(WALLET_FILE, {})
    return wallets.get(str(user_id), 0)

def add_balance(user_id, amount):
    wallets = load_json(WALLET_FILE, {})
    uid = str(user_id)
    wallets[uid] = wallets.get(uid, 0) + amount
    save_json(WALLET_FILE, wallets)

def set_balance(user_id, amount):
    wallets = load_json(WALLET_FILE, {})
    wallets[str(user_id)] = amount
    save_json(WALLET_FILE, wallets)

def save_user(user_id):
    users = load_json(USERS_FILE, [])
    if user_id not in users:
        users.append(user_id)
        save_json(USERS_FILE, users)

def get_stock():
    return load_json(STOCK_FILE, {})

def set_stock(stock):
    save_json(STOCK_FILE, stock)

def get_ott_plans():
    return {
        "NETFLIX": {"desc": "📺 NETFLIX", "price": 99},
        "PRIME": {"desc": "📺 PRIME VIDEO", "price": 45},
        "PORNHUB": {"desc": "📛 PORNHUB PREMIUM", "price": 69}
    }

def set_ott_plans(plans):
    save_json(OTT_FILE, plans)

def is_admin(user_id):
    return user_id in ADMIN_IDS

# Razorpay helper functions
def create_payment_link(user_id: int, amount_rupees: int) -> dict:
    paise = amount_rupees * 100  # Razorpay works in paise
    resp = razor.payment_link.create({
        "amount": paise,
        "currency": "INR",
        "reference_id": f"{user_id}_{datetime.datetime.now().timestamp()}",
        "description": f"Wallet top-up for Telegram user {user_id}",
        "customer": {"name": str(user_id)},
        "callback_method": "get",
        "callback_url": "https://t.me/ottsonly1"
    })
    return resp

def is_payment_link_paid(plink_id: str) -> bool:
    try:
        link = razor.payment_link.fetch(plink_id)
        return link["status"] == "paid"
    except:
        return False

user_states = {}
admin_states = {}

async def cmds(update, context):
    user_cmds = (
        "<b>USER COMMANDS:</b>\n"
        "/start - Start the bot and see the main menu\n"
        "/buyotts - Buy OTT subscriptions\n"
        "/addfunds - Add funds to your wallet\n"
        "/chkbal - Check your wallet balance\n"
        "/stock - Check current OTT stock\n"
        "/cmds - Show this command list"
    )
    admin_cmds = (
        "\n\n<b>ADMIN COMMANDS:</b>\n"
        "/add <amount> <user_id> - Add funds to a user\n"
        "/chk <user_id> - Check a user's balance\n"
        "/broadcast <message> - Send a broadcast to all users\n"
        "/editstock - Edit OTT stock interactively\n"
        "/addott - Add a new OTT plan interactively\n"
        "/addaccount <OTT_NAME> <username> <password> - Add an OTT account for auto-delivery\n"
        "/users - View the list of users\n"
        "/clearadminstate - Reset your admin state"
    )
    msg = user_cmds
    if is_admin(update.effective_user.id):
        msg += admin_cmds
    await update.message.reply_text(msg, parse_mode="HTML")

async def buyotts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("Netflix", callback_data="buy_NETFLIX")],
        [InlineKeyboardButton("Prime", callback_data="buy_PRIME")],
        [InlineKeyboardButton("Pornhub", callback_data="buy_PORNHUB")]
    ]
    await update.message.reply_text(
        "<b>SELECT WHICH OTTS YOU WANT TO BUY</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )

async def ott_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        if not query or not query.data:
            return
        user_id = query.from_user.id
        ott_plans = get_ott_plans()
        stock = get_stock()

        # Netflix preview
        if query.data == "buy_NETFLIX":
            try:
                with open("images/netflix.png", "rb") as photo:
                    caption = (
                        "<b>NETFLIX AVAILABLE 📺</b>\n"
                        "<b>✅PRIVATE SCREEN</b>\n"
                        "<b>🔥BENEFITS -</b>\n"
                        "<b>➡️TV/LAPTOP SUPPORTED</b>\n"
                        "<b>➡️NO PASSWORD CHANGE ISSUE</b>\n"
                        "<b>➡️NO HOLD WARRANTY AND SHIT</b>\n"
                        "<b>➡️NO LOG OUT PROBLEM</b>\n"
                        "<b>➡️4K + HDR PLAN</b>\n"
                        "<b>💰PRICE -:</b>\n"
                        "<b>😀1 MONTH - 99₹</b>"
                    )
                    buy_button = [[InlineKeyboardButton("BUY NOW", callback_data="confirm_buy_NETFLIX")]]
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(buy_button),
                        parse_mode="HTML"
                    )
                await query.answer()
            except Exception as e:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="<b>❌ ERROR: NETFLIX IMAGE NOT FOUND OR CANNOT BE SENT.</b>",
                    parse_mode="HTML"
                )
            return

        # Prime preview
        if query.data == "buy_PRIME":
            try:
                with open("images/prime.png", "rb") as photo:
                    caption = (
                        "<b>AMAZON PRIME VIDEO</b>\n"
                        "<b>~ 1 MONTH</b>\n"
                        "<b>~ PRIVATE SINGLE SCREEN</b>\n"
                        "<b>~ MAX QUALITY</b>\n"
                        "<b>~ TV/PC SUPPORTED</b>\n"
                        "<b>~ ID PASS LOGIN</b>\n"
                        "<b>~ PRICE : 45₹</b>"
                    )
                    buy_button = [[InlineKeyboardButton("BUY NOW", callback_data="confirm_buy_PRIME")]]
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(buy_button),
                        parse_mode="HTML"
                    )
                await query.answer()
            except Exception as e:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="<b>❌ ERROR: PRIME IMAGE NOT FOUND OR CANNOT BE SENT.</b>",
                    parse_mode="HTML"
                )
            return

        # Pornhub preview
        if query.data == "buy_PORNHUB":
            try:
                with open("images/pornhub.png", "rb") as photo:
                    caption = (
                        "<b>PORN HUB PREMIUM</b>\n"
                        "<b>~ 1 MONTH</b>\n"
                        "<b>~ PRIVATE SINGLE SCREEN</b>\n"
                        "<b>~ MAX QUALITY</b>\n"
                        "<b>~ TV/PC SUPPORTED</b>\n"
                        "<b>~ ID PASS LOGIN</b>\n"
                        "<b>~ PRICE : 69₹</b>"
                    )
                    buy_button = [[InlineKeyboardButton("BUY NOW", callback_data="confirm_buy_PORNHUB")]]
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(buy_button),
                        parse_mode="HTML"
                    )
                await query.answer()
            except Exception as e:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="<b>❌ ERROR: PORNHUB IMAGE NOT FOUND OR CANNOT BE SENT.</b>",
                    parse_mode="HTML"
                )
            return

        # Netflix actual purchase
        if query.data == "confirm_buy_NETFLIX":
            plan = ott_plans["NETFLIX"]
            price = plan["price"]
            balance = get_balance(user_id)
            if stock.get("NETFLIX", 0) <= 0:
                await query.answer()
                await context.bot.send_message(
                    chat_id=user_id,
                    text="<b>❌ OUT OF STOCK FOR NETFLIX!</b>",
                    parse_mode="HTML"
                )
                return
            if balance >= price:
                set_balance(user_id, balance - price)
                stock["NETFLIX"] = stock.get("NETFLIX", 0) - 1
                set_stock(stock)
                try:
                    with open("netflix_accounts.json", "r") as f:
                        accounts = json.load(f)
                    if accounts:
                        account = accounts.pop(0)
                        with open("netflix_accounts.json", "w") as f:
                            json.dump(accounts, f)
                        now = datetime.datetime.now()
                        end = now + datetime.timedelta(days=30)
                        cred_msg = (
                            f"<b>🎉 YOUR SUBSCRIPTION DETAILS:</b>\n\n"
                            f"<b>🆔:</b> <code>{account['username']}</code>\n"
                            f"<b>🔑:</b> <code>{account['password']}</code>\n\n"
                            f"<b>🚫 DONT CHANGE THE PASSWORD OR LOCK THE PROFILE!</b>\n"
                            f"<b>🚫 DONT TOUCH ANYTHING IN BILLING / ACCOUNT SECTION!</b>\n"
                            f"<b>⚠️ OR ELSE NO REFUND WILL BE GIVEN.</b>\n\n"
                            f"<b>🕒 YOUR SUBSCRIPTION STARTS ON: {now.strftime('%d %B %Y').upper()}</b>\n"
                            f"<b>🕒 YOUR SUBSCRIPTION ENDS ON: {end.strftime('%d %B %Y').upper()}</b>\n\n"
                            f"<b>📸 AFTER PAYMENT, SEND YOUR PAYMENT SCREENSHOT TO THE ADMIN FOR INSTANT ACTIVATION OR SUPPORT:</b>"
                        )
                        screenshot_btn = [[InlineKeyboardButton("SEND SCREENSHOT", url="https://t.me/ottsonly1")]]
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=cred_msg,
                            reply_markup=InlineKeyboardMarkup(screenshot_btn),
                            parse_mode="HTML"
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"<b>❌ SORRY, NO NETFLIX ACCOUNTS AVAILABLE AT THE MOMENT.</b>",
                            parse_mode="HTML"
                        )
                except Exception:
                    tb = traceback.format_exc()
                    await context.bot.send_message(
                        chat_id=LOGS_CHANNEL_ID,
                        text=f"<b>ERROR IN NETFLIX DELIVERY:</b>\n<code>{tb}</code>",
                        parse_mode="HTML"
                    )
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"<b>❌ ERROR ACCESSING NETFLIX ACCOUNTS.</b>",
                        parse_mode="HTML"
                    )
                await query.answer()
            else:
                await query.answer()
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"<b>❌ INSUFFICIENT FUNDS! YOUR BALANCE: ₹{balance}\nPLEASE ADD FUNDS FIRST.</b>",
                    parse_mode="HTML"
                )
            return

        # Prime actual purchase
        if query.data == "confirm_buy_PRIME":
            plan = ott_plans["PRIME"]
            price = plan["price"]
            balance = get_balance(user_id)
            if stock.get("PRIME", 0) <= 0:
                await query.answer()
                await context.bot.send_message(
                    chat_id=user_id,
                    text="<b>❌ OUT OF STOCK FOR PRIME!</b>",
                    parse_mode="HTML"
                )
                return
            if balance >= price:
                set_balance(user_id, balance - price)
                stock["PRIME"] = stock.get("PRIME", 0) - 1
                set_stock(stock)
                try:
                    with open("prime_accounts.json", "r") as f:
                        accounts = json.load(f)
                    if accounts:
                        account = accounts.pop(0)
                        with open("prime_accounts.json", "w") as f:
                            json.dump(accounts, f)
                        now = datetime.datetime.now()
                        end = now + datetime.timedelta(days=30)
                        cred_msg = (
                            f"<b>🎉 YOUR SUBSCRIPTION DETAILS:</b>\n\n"
                            f"<b>🆔:</b> <code>{account['username']}</code>\n"
                            f"<b>🔑:</b> <code>{account['password']}</code>\n\n"
                            f"<b>🚫 DONT CHANGE THE PASSWORD OR LOCK THE PROFILE!</b>\n"
                            f"<b>🚫 DONT TOUCH ANYTHING IN BILLING / ACCOUNT SECTION!</b>\n"
                            f"<b>⚠️ OR ELSE NO REFUND WILL BE GIVEN.</b>\n\n"
                            f"<b>🕒 YOUR SUBSCRIPTION STARTS ON: {now.strftime('%d %B %Y').upper()}</b>\n"
                            f"<b>🕒 YOUR SUBSCRIPTION ENDS ON: {end.strftime('%d %B %Y').upper()}</b>\n\n"
                            f"<b>📸 AFTER PAYMENT, SEND YOUR PAYMENT SCREENSHOT TO THE ADMIN FOR INSTANT ACTIVATION OR SUPPORT:</b>"
                        )
                        screenshot_btn = [[InlineKeyboardButton("SEND SCREENSHOT", url="https://t.me/ottsonly1")]]
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=cred_msg,
                            reply_markup=InlineKeyboardMarkup(screenshot_btn),
                            parse_mode="HTML"
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"<b>❌ SORRY, NO PRIME ACCOUNTS AVAILABLE AT THE MOMENT.</b>",
                            parse_mode="HTML"
                        )
                except Exception:
                    tb = traceback.format_exc()
                    await context.bot.send_message(
                        chat_id=LOGS_CHANNEL_ID,
                        text=f"<b>ERROR IN PRIME DELIVERY:</b>\n<code>{tb}</code>",
                        parse_mode="HTML"
                    )
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"<b>❌ ERROR ACCESSING PRIME ACCOUNTS.</b>",
                        parse_mode="HTML"
                    )
                await query.answer()
            else:
                await query.answer()
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"<b>❌ INSUFFICIENT FUNDS! YOUR BALANCE: ₹{balance}\nPLEASE ADD FUNDS FIRST.</b>",
                    parse_mode="HTML"
                )
            return

        # Pornhub actual purchase
        if query.data == "confirm_buy_PORNHUB":
            plan = ott_plans["PORNHUB"]
            price = plan["price"]
            balance = get_balance(user_id)
            if stock.get("PORNHUB", 0) <= 0:
                await query.answer()
                await context.bot.send_message(
                    chat_id=user_id,
                    text="<b>❌ OUT OF STOCK FOR PORNHUB!</b>",
                    parse_mode="HTML"
                )
                return
            if balance >= price:
                set_balance(user_id, balance - price)
                stock["PORNHUB"] = stock.get("PORNHUB", 0) - 1
                set_stock(stock)
                try:
                    with open("pornhub_accounts.json", "r") as f:
                        accounts = json.load(f)
                    if accounts:
                        account = accounts.pop(0)
                        with open("pornhub_accounts.json", "w") as f:
                            json.dump(accounts, f)
                        msg = (
                            f"🔥 | Mail - {account['username']}\n"
                            f"🔥 | Pass - {account['password']}\n\n"
                            f"Rules For PORNHUB:\n"
                            f"(1) Login to Only Single Device Strictly.\n"
                            f"(2) Dont Change Email or Password\n"
                            f"(3) Use Single USA IP Address and Good VPN,\n"
                            f"Don't Use Multiple IP Addresses"
                        )
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=msg,
                            parse_mode="HTML"
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text="<b>❌ SORRY, NO PORNHUB ACCOUNTS AVAILABLE AT THE MOMENT.</b>",
                            parse_mode="HTML"
                        )
                except Exception:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="<b>❌ ERROR ACCESSING PORNHUB ACCOUNTS.</b>",
                        parse_mode="HTML"
                    )
            else:
                await query.answer()
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"<b>❌ INSUFFICIENT FUNDS! YOUR BALANCE: ₹{balance}\nPLEASE ADD FUNDS FIRST.</b>",
                    parse_mode="HTML"
                )
            return

    except Exception:
        tb = traceback.format_exc()
        await context.bot.send_message(
            chat_id=LOGS_CHANNEL_ID,
            text=f"<b>INLINE BUTTON ERROR:</b>\n<code>{tb}</code>",
            parse_mode="HTML"
        )
        if update and hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.answer("❌ An error occurred. Admin has been notified.", show_alert=True)

# Updated addfunds function with Razorpay integration
async def addfunds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>💰 ENTER THE AMOUNT (₹) YOU WANT TO ADD:</b>",
        parse_mode="HTML"
    )
    user_states[update.effective_user.id] = "awaiting_amount"

# Handle amount input for Razorpay payment
async def amount_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)
    
    if state != "awaiting_amount":
        return
    
    try:
        amount = int(update.message.text.strip())
        if amount < 1:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "<b>❌ PLEASE ENTER A VALID POSITIVE NUMBER.</b>",
            parse_mode="HTML"
        )
        return
    
    try:
        link = create_payment_link(user_id, amount)
        cb_data = f"plink_check_{link['id']}_{amount}"
        buttons = [[InlineKeyboardButton("✅ I HAVE PAID", callback_data=cb_data)]]
        
        await update.message.reply_text(
            f"<b>💳 CLICK THE LINK BELOW TO PAY ₹{amount}:</b>\n\n"
            f"{link['short_url']}\n\n"
            f"<b>AFTER COMPLETING THE PAYMENT, CLICK THE BUTTON BELOW:</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="HTML"
        )
        user_states[user_id] = None
    except Exception as e:
        await update.message.reply_text(
            "<b>❌ ERROR CREATING PAYMENT LINK. PLEASE TRY AGAIN.</b>",
            parse_mode="HTML"
        )
        user_states[user_id] = None

# Handle payment verification
async def payment_poll_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    try:
        # Ensure this callback is meant for payment verification
        if not data.startswith("plink_check_"):
            await query.answer("Invalid payment check request.", show_alert=True)
            return

        parts = data.split("_")
        if len(parts) < 4:
            await query.answer("Malformed payment data. Contact admin.", show_alert=True)
            return

        plink_id = parts[2]
        try:
            amount = int(parts[3])
        except Exception:
            await query.answer("Invalid payment amount. Contact admin.", show_alert=True)
            return

        await query.answer("🔄 Checking payment status...")

        if is_payment_link_paid(plink_id):  # Razorpay check here
            add_balance(query.from_user.id, amount)
            new_balance = get_balance(query.from_user.id)
            await query.edit_message_text(
                f"<b>✅ PAYMENT SUCCESSFUL!</b>\n\n"
                f"<b>₹{amount} HAS BEEN ADDED TO YOUR WALLET.</b>\n"
                f"<b>💰 YOUR NEW BALANCE: ₹{new_balance}</b>",
                parse_mode="HTML"
            )
        else:
            await query.answer(
                "❌ Payment not found yet. Please complete your payment and try again.",
                show_alert=True)
            
    except Exception as e:
        # Optionally, log the error for admin review
        LOGS_CHANNEL_ID = -4758912978  # Replace if needed
        tb = traceback.format_exc()
        # Log full error message for admin
        await context.bot.send_message(
            chat_id=LOGS_CHANNEL_ID,
            text=f"<b>Payment verification error:</b>\n<code>{tb}</code>",
            parse_mode="HTML"
        )
        await query.answer("❌ Unexpected error during payment check. Please contact admin.", show_alert=True)

async def chkbal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance = get_balance(update.effective_user.id)
    await update.message.reply_text(
        f"<b>💰 YOUR CURRENT WALLET BALANCE IS: ₹{balance}</b>",
        parse_mode="HTML"
    )

async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ott_plans = get_ott_plans()
    stock = get_stock()
    if not stock:
        stock = {key: 10 for key in ott_plans}
        set_stock(stock)
    stock_lines = [f"<b>{key}</b>: {stock.get(key, 0)}" for key in ott_plans]
    await update.message.reply_text(
        "<b>📦 CURRENT STOCK:</b>\n" + "\n".join(stock_lines),
        parse_mode="HTML"
    )

async def clearadminstate(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ YOU ARE NOT AUTHORIZED.", parse_mode="HTML")
        return
    user_id = update.effective_user.id
    admin_states.pop(user_id, None)
    await update.message.reply_text("✅ ADMIN STATE CLEARED. YOU CAN NOW USE THE BOT NORMALLY.", parse_mode="HTML")

async def add_funds_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ YOU ARE NOT AUTHORIZED.", parse_mode="HTML")
        return
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text(
                "<b>Usage:</b> /add <amount> <user_id>", parse_mode="HTML"
            )
            return
        amount = int(args[0])
        user_id = int(args[1])
        if amount <= 0:
            await update.message.reply_text(
                "<b>Amount must be positive.</b>", parse_mode="HTML"
            )
            return
        add_balance(user_id, amount)
        new_balance = get_balance(user_id)
        await update.message.reply_text(
            f"<b>✅ Added ₹{amount} to user {user_id}'s wallet.</b>", parse_mode="HTML"
        )
        # Notify the user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"<b>YOUR WALLET HAS BEEN CREDITED!</b>\n\n<b>YOUR NEW BALANCE IS: ₹{new_balance}</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass
    except Exception as e:
        await update.message.reply_text(
            "<b>❌ Error: Could not add funds. Check your command and try again.</b>",
            parse_mode="HTML"
        )

async def chk_user_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ YOU ARE NOT AUTHORIZED.", parse_mode="HTML")
        return
    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text(
                "<b>Usage:</b> /chk <user_id>", parse_mode="HTML"
            )
            return
        user_id = int(args[0])
        balance = get_balance(user_id)
        await update.message.reply_text(
            f"<b>User {user_id} balance: ₹{balance}</b>", parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(
            "<b>❌ Error: Could not fetch balance. Check your command and try again.</b>",
            parse_mode="HTML"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    menu = [
        ["💸 ADD FUNDS", "💰 CHECK BALANCE"],
        ["🎬 BUY OTTS", "📦 STOCK"]
    ]
    reply_markup = ReplyKeyboardMarkup(menu, resize_keyboard=True)
    welcome_text = (
        f"<b>👋 HII {user.first_name.upper()} WELCOME TO OUR OTT SUBSCRIPTION!</b>\n\n"
        f"<b>👉 JOIN OUR MAIN CHANNEL FOR MORE UPDATES!</b>\n\n"
        f"<b>✅ WE PROMISE TO PROVIDE GUARANTEED SERVICES AS WRITTEN IN THE POSTS.</b>\n"
        f"<b>💯 IF YOU HAVE ANY KIND OF ISSUES, WE WILL REFUND YOU THE FULL AMOUNT OR GIVE A REPLACEMENT WITHIN THE SAME DAY.</b>\n\n"
        f"<b>🤖 THIS IS AN AUTOMATED SUBSCRIPTION BOT – YOU DON'T HAVE TO WAIT FOR MANUAL SERVICE. YOU WILL GET YOUR SUBSCRIPTIONS AUTOMATICALLY!</b>"
    )
    buttons = [
        [
            InlineKeyboardButton("MAIN CHANNEL", url="https://t.me/ottsonly01"),
            InlineKeyboardButton("HELP", url="https://t.me/ottsonly1")
        ]
    ]
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )
    await update.message.reply_text(
        "<b>CHOOSE AN OPTION FROM THE MENU BELOW:</b>",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    save_user(user_id)
    ott_plans = get_ott_plans()
    
    # Check if user is in amount input state
    if user_states.get(user_id) == "awaiting_amount":
        await amount_reply_handler(update, context)
        return
    
    if text.upper() == "💸 ADD FUNDS":
        await addfunds(update, context)
    elif text.upper() == "💰 CHECK BALANCE":
        await chkbal(update, context)
    elif text.upper() == "🎬 BUY OTTS":
        await buyotts(update, context)
    elif text.upper() == "📦 STOCK":
        await stock(update, context)
    else:
        await update.message.reply_text(
            "<b>❌ INVALID OPTION. PLEASE USE THE MENU.</b>",
            parse_mode="HTML"
        )

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CallbackQueryHandler(ott_button_handler))
    app.add_handler(CallbackQueryHandler(payment_poll_handler, pattern="^plink_check_"))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmds", cmds))
    app.add_handler(CommandHandler("buyotts", buyotts))
    app.add_handler(CommandHandler("addfunds", addfunds))
    app.add_handler(CommandHandler("chkbal", chkbal))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("clearadminstate", clearadminstate))
    app.add_handler(CommandHandler("add", add_funds_admin))
    app.add_handler(CommandHandler("chk", chk_user_balance))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.run_polling()

if __name__ == "__main__":
    main()
