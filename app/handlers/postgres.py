from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from app.services.postgres_client import PostgresClient
from app.services.repl_logs import get_replication_logs
from app.validators.email_phone import EMAIL_REGEX, PHONE_REGEX

# Состояния для диалогов добавления
WAITING_EMAIL_TEXT = 1
WAITING_PHONE_TEXT = 2


# Клиенты БД (будут инициализированы в main и положены в bot_data)
def get_master_db(context):
    return context.bot_data["master_db"]


def get_slave_db(context):
    return context.bot_data["slave_db"]


# Команда /get_repl_logs
async def get_repl_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logs = get_replication_logs(50)
    if len(logs) > 4000:
        logs = logs[-4000:]
    await update.message.reply_text(f"<pre>{logs}</pre>", parse_mode="HTML")


# Команды чтения таблиц
async def get_emails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    slave = get_slave_db(context)
    rows = slave.execute_query("SELECT email FROM emails ORDER BY id")
    if not rows:
        await update.message.reply_text("Email-адреса не найдены.")
    else:
        text = "\n".join([row["email"] for row in rows])
        await update.message.reply_text(f"Список email:\n{text}")


async def get_phone_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    slave = get_slave_db(context)
    rows = slave.execute_query("SELECT phone FROM phones ORDER BY id")
    if not rows:
        await update.message.reply_text("Номера телефонов не найдены.")
    else:
        text = "\n".join([row["phone"] for row in rows])
        await update.message.reply_text(f"Список телефонов:\n{text}")


# Добавление email (диалог)
async def add_email_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправьте текст, из которого нужно извлечь email-адреса."
    )
    return WAITING_EMAIL_TEXT


async def add_email_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    emails = EMAIL_REGEX.findall(text)
    if not emails:
        await update.message.reply_text("Email-адреса не найдены. Завершаю.")
        return ConversationHandler.END

    context.user_data["found_emails"] = emails
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="confirm_email"),
            InlineKeyboardButton("Нет", callback_data="cancel_email"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Найдены email:\n{chr(10).join(emails)}\nЗаписать их в базу?",
        reply_markup=reply_markup,
    )
    return WAITING_EMAIL_TEXT


async def email_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "confirm_email":
        emails = context.user_data.get("found_emails", [])
        master = get_master_db(context)
        inserted = 0
        for email in emails:
            try:
                master.execute_query(
                    "INSERT INTO emails (email) VALUES (%s) ON CONFLICT (email) DO NOTHING",
                    (email,),
                    fetch=False,
                )
                inserted += 1
            except Exception as e:
                print(e)
        await query.edit_message_text(
            f"Добавлено {inserted} из {len(emails)} email-адресов."
        )
    else:
        await query.edit_message_text("Запись отменена.")
    return ConversationHandler.END


# Аналогично для телефонов
async def add_phone_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправьте текст, из которого нужно извлечь номера телефонов."
    )
    return WAITING_PHONE_TEXT


async def add_phone_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    phones = PHONE_REGEX.findall(text)
    if not phones:
        await update.message.reply_text("Номера телефонов не найдены. Завершаю.")
        return ConversationHandler.END

    context.user_data["found_phones"] = phones
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="confirm_phone"),
            InlineKeyboardButton("Нет", callback_data="cancel_phone"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Найдены телефоны:\n{chr(10).join(phones)}\nЗаписать их в базу?",
        reply_markup=reply_markup,
    )
    return WAITING_PHONE_TEXT


async def phone_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "confirm_phone":
        phones = context.user_data.get("found_phones", [])
        master = get_master_db(context)
        inserted = 0
        for phone in phones:
            try:
                master.execute_query(
                    "INSERT INTO phones (phone) VALUES (%s) ON CONFLICT (phone) DO NOTHING",
                    (phone,),
                    fetch=False,
                )
                inserted += 1
            except Exception as e:
                print(e)
        await query.edit_message_text(f"Добавлено {inserted} из {len(phones)} номеров.")
    else:
        await query.edit_message_text("Запись отменена.")
    return ConversationHandler.END
