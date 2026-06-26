import logging
import requests
import asyncio
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# ══════════════════════════════════════════════════════════════════════════════
#  KONFİQURASİYA
# ══════════════════════════════════════════════════════════════════════════════
PAYMENT_BOT_TOKEN = "8702590227:AAGxTUfCENQ-5U97JtplEHbsG0mAs3dSqQs"   # Ödəniş botu tokeni
ALERT_BOT_TOKEN   = "8831044220:AAFuQs2O6kYpxw1M3Gc7v3EieMrNSBkJyKE"     # Alert botu tokeni

ADMIN_CHAT_ID = 2094914778    # Sənin chat id-n
API_BASE_URL  = "http://localhost:7999"
BOT_SECRET    = "qolqol-bot-secret-2024"

WELCOME_MESSAGE = """👋 Xoş gəldiniz!

Xidmətimizdən istifadə etmək üçün ödənişi aşağıdakı rekvizitə göndərin:
💳 Kart: 1234 5678 9012 3456
💰 Məbləğ: 10 AZN

Ödənişi etdikdən sonra çekin şəklini buraya göndərin."""

WAITING = 1

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Qlobal state ──────────────────────────────────────────────────────────────
user_state: dict[int, dict] = {}
admin_feedback_target: dict[int, dict] = {}

# receipt_store: { key -> {user_chat_id, photo_bytes} }
# photo_file_id saxlamırıq — fərqli bot üçün keçərli deyil
receipt_store: dict[str, dict] = {}

# Bot instance-ları — işə düşəndə təyin olunur
alert_bot_instance = None
payment_bot_instance = None


def store_receipt(user_chat_id: int, photo_bytes: bytes) -> str:
    key = uuid.uuid4().hex[:12]
    receipt_store[key] = {
        "user_chat_id": user_chat_id,
        "photo_bytes":  photo_bytes,
    }
    return key


def get_receipt(key: str) -> dict | None:
    return receipt_store.get(key)


# ══════════════════════════════════════════════════════════════════════════════
#  ALERT BOTU
# ══════════════════════════════════════════════════════════════════════════════

async def alert_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Bu bot yalnız admin üçündür.")
        return
    await update.message.reply_text(
        "🔔 Alert Botu\n\n"
        "Komandalar:\n"
        "/send <chat_id> <mesaj> — istifadəçiyə mesaj göndər\n"
        "/broadcast <mesaj> — bütün aktiv istifadəçilərə göndər\n"
        "/users — aktiv istifadəçilərin siyahısı"
    )

async def alert_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("İstifadə: /send <chat_id> <mesaj>")
        return
    try:
        target_id = int(args[0])
        text = " ".join(args[1:])
    except ValueError:
        await update.message.reply_text("❌ Chat ID rəqəm olmalıdır.")
        return
    try:
        await context.bot.send_message(chat_id=target_id, text=f"📢 Admin mesajı:\n\n{text}")
        await update.message.reply_text(f"✅ Mesaj {target_id}-ə göndərildi.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xəta: {e}")

async def alert_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return
    if not context.args:
        await update.message.reply_text("İstifadə: /broadcast <mesaj>")
        return
    text = " ".join(context.args)
    targets = set(user_state.keys())
    if not targets:
        await update.message.reply_text("📭 Heç bir aktiv istifadəçi yoxdur.")
        return
    ok, fail = 0, 0
    for uid in targets:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Elan:\n\n{text}")
            ok += 1
        except Exception:
            fail += 1
    await update.message.reply_text(f"✅ Göndərildi: {ok}\n❌ Uğursuz: {fail}")

async def alert_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return
    if not user_state:
        await update.message.reply_text("📭 Aktiv istifadəçi yoxdur.")
        return
    lines = [f"• {uid} — {state}" for uid, state in user_state.items()]
    await update.message.reply_text("👥 Aktiv istifadəçilər:\n" + "\n".join(lines))

def build_alert_app() -> Application:
    app = Application.builder().token(ALERT_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",     alert_start))
    app.add_handler(CommandHandler("send",      alert_send))
    app.add_handler(CommandHandler("broadcast", alert_broadcast))
    app.add_handler(CommandHandler("users",     alert_users))
    app.add_handler(CallbackQueryHandler(pay_admin_callback))
    return app


# ══════════════════════════════════════════════════════════════════════════════
#  ÖDƏNİŞ BOTU
# ══════════════════════════════════════════════════════════════════════════════

async def pay_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.effective_chat.id
    if uid not in user_state:
        user_state[uid] = {}
    await update.message.reply_text(WELCOME_MESSAGE)
    return WAITING

async def pay_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_chat.id

    if user_id == ADMIN_CHAT_ID and ADMIN_CHAT_ID in admin_feedback_target:
        await pay_process_feedback(update, context)
        return WAITING

    if user_id in user_state and user_state[user_id].get("awaiting"):
        await pay_collect_credentials(update, context)
        return WAITING

    return await pay_receive_receipt(update, context)

async def pay_receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user    = update.effective_user
    chat_id = update.effective_chat.id

    if not update.message.photo:
        if not context.user_data.get("warned"):
            context.user_data["warned"] = True
            await update.message.reply_text("⚠️ Xahiş olunur resim formatında cavab verin.")
        return WAITING

    context.user_data["warned"] = False

    # Şəkli ödəniş botundan yüklə (bytes kimi)
    tg_file = await context.bot.get_file(update.message.photo[-1].file_id)
    photo_bytes = bytes(await tg_file.download_as_bytearray())

    # Bytes-ı store-a yaz, qısa key al
    key = store_receipt(chat_id, photo_bytes)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Təsdiqlə",   callback_data=f"approve:{key}"),
            InlineKeyboardButton("❌ Rədd et",    callback_data=f"reject:{key}"),
        ],
        [
            InlineKeyboardButton("💬 Rəy bildir", callback_data=f"feedback:{key}"),
        ],
    ])

    # Alert botu vasitəsilə adminin yanına göndər
    sender = alert_bot_instance if alert_bot_instance else context.bot
    sent = await sender.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo_bytes,
        caption=(
            f"📥 Yeni ödəniş çeki\n"
            f"👤 İstifadəçi: {user.full_name} (@{user.username or 'yoxdur'})\n"
            f"🆔 Chat ID: {chat_id}"
        ),
        reply_markup=keyboard,
    )
    logger.info("Çek alındı. key=%s admin_msg_id=%s", key, sent.message_id)
    await update.message.reply_text("⏳ Çekiniz göndərildi. Nəticə gözləyin...")
    return WAITING

async def pay_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer("Bu əməliyyat yalnız admin üçündür.", show_alert=True)
        return

    try:
        action, key = query.data.split(":", 1)
    except ValueError:
        return

    receipt = get_receipt(key)
    if not receipt:
        await query.answer("Bu çek artıq mövcud deyil.", show_alert=True)
        return

    user_chat_id = receipt["user_chat_id"]
    photo_bytes  = receipt["photo_bytes"]
    user_bot = payment_bot_instance if payment_bot_instance else context.bot

    if action == "reject":
        await user_bot.send_message(
            chat_id=user_chat_id,
            text="❌ Ödəniş çekiniz qəbul edilmədi.\nXahiş olunur çeki yenidən göndərin.",
        )
        await query.edit_message_caption(
            caption=(query.message.caption or "") + "\n\n❌ RƏDD EDİLDİ",
            reply_markup=None,
        )
        receipt_store.pop(key, None)

    elif action == "approve":
        user_state[user_chat_id] = {"awaiting": "username"}
        await user_bot.send_message(
            chat_id=user_chat_id,
            text=(
                "✅ Ödənişiniz təsdiqləndi!\n\n"
                "Hesabınızı yaratmaq üçün məlumatlarınızı daxil edin.\n"
                "📝 İstifadəçi adınızı (username) yazın:"
            ),
        )
        await query.edit_message_caption(
            caption=(query.message.caption or "") + "\n\n✅ TƏSDİQLƏNDİ",
            reply_markup=None,
        )
        receipt_store.pop(key, None)

    elif action == "feedback":
        admin_feedback_target[ADMIN_CHAT_ID] = {
            "user_chat_id": user_chat_id,
            "photo_bytes":  photo_bytes,
            "message_id":   query.message.message_id,
            "key":          key,
        }
        await query.edit_message_caption(
            caption=(query.message.caption or "") + "\n\n💬 RƏY GÖZLƏNİR",
            reply_markup=None,
        )
        await payment_bot_instance.send_message(
            chat_id=ADMIN_CHAT_ID,
            text="✍️ Rəyinizi yazın (istifadəçiyə göndəriləcək):",
        )

async def pay_process_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    target = admin_feedback_target.pop(ADMIN_CHAT_ID, None)
    if not target or not update.message or not update.message.text:
        return

    user_chat_id = target["user_chat_id"]
    photo_bytes  = target["photo_bytes"]
    msg_id       = target["message_id"]
    key          = target["key"]

    user_bot = payment_bot_instance if payment_bot_instance else context.bot
    await user_bot.send_photo(
        chat_id=user_chat_id,
        photo=photo_bytes,
        caption=f"💬 Admin rəyi:\n{update.message.text}\n\nXahiş olunur çeki yenidən göndərin.",
    )
    await update.message.reply_text("✅ Rəy istifadəçiyə göndərildi.")

    try:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Təsdiqlə",   callback_data=f"approve:{key}"),
                InlineKeyboardButton("❌ Rədd et",    callback_data=f"reject:{key}"),
            ],
            [
                InlineKeyboardButton("💬 Rəy bildir", callback_data=f"feedback:{key}"),
            ],
        ])
        await context.bot.edit_message_reply_markup(
            chat_id=ADMIN_CHAT_ID,
            message_id=msg_id,
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.warning("Keyboard bərpa xətası: %s", e)

async def pay_collect_credentials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id  = update.effective_chat.id
    state    = user_state.get(user_id, {})
    awaiting = state.get("awaiting")

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    import re

    if awaiting == "username":
        if not re.match(r"^[a-zA-Z0-9]+$", text):
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Username yalnız latın hərfləri və rəqəmlərdən ibarət ola bilər (boşluq yox). Yenidən yazın:",
            )
            return
        if len(text) < 3 or len(text) > 20:
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Username 3-20 simvol arası olmalıdır. Yenidən yazın:",
            )
            return
        user_state[user_id]["username"] = text
        user_state[user_id]["awaiting"] = "password"
        await context.bot.send_message(chat_id=user_id, text="🔒 İndi şifrənizi (password) yazın:")

    elif awaiting == "password":
        username = state.get("username", "")
        password = text
        if len(password) < 6:
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Şifrə minimum 6 simvol olmalıdır. Yenidən yazın:",
            )
            return
        if len(password) > 40:
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Şifrə maksimum 40 simvol ola bilər. Yenidən yazın:",
            )
            return
        try:
            resp = requests.post(
                f"{API_BASE_URL}/create-user",
                json={"username": username, "password": password},
                headers={"X-BOT-SECRET": BOT_SECRET},
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error("API xətası: %s", e)
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Hesab yaradılarkən xəta baş verdi. Adminlə əlaqə saxlayın."
            )
            user_state.pop(user_id, None)
            return

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"🎉 Hesabınız uğurla yaradıldı!\n\n"
                f"👤 İstifadəçi adı: <code>{username}</code>\n"
                f"🔑 Şifrə: <code>{password}</code>\n\n"
                f"Bu məlumatları yadda saxlayın."
            ),
            parse_mode="HTML",
        )
        user_state.pop(user_id, None)

def build_payment_app() -> Application:
    app = Application.builder().token(PAYMENT_BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", pay_start)],
        states={
            WAITING: [
                MessageHandler(filters.ALL & ~filters.COMMAND, pay_handle_message),
            ],
        },
        fallbacks=[CommandHandler("start", pay_start)],
        per_user=True,
        per_chat=False,
        allow_reentry=True,
    )
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(pay_admin_callback))
    return app


# ══════════════════════════════════════════════════════════════════════════════
#  İKİ BOTU PARALEL İŞƏ SAL
# ══════════════════════════════════════════════════════════════════════════════

async def run_both():
    global alert_bot_instance, payment_bot_instance

    payment_app = build_payment_app()
    alert_app   = build_alert_app()

    await payment_app.initialize()
    await alert_app.initialize()
    await payment_app.start()
    await alert_app.start()

    alert_bot_instance = alert_app.bot
    payment_bot_instance = payment_app.bot
    logger.info("Alert bot instance təyin edildi: %s", alert_bot_instance)
    logger.info("Payment bot instance təyin edildi: %s", payment_bot_instance)

    await payment_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    await alert_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    logger.info("✅ Hər iki bot işə düşdü.")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await payment_app.updater.stop()
        await alert_app.updater.stop()
        await payment_app.stop()
        await alert_app.stop()
        await payment_app.shutdown()
        await alert_app.shutdown()


if __name__ == "__main__":
    asyncio.run(run_both())