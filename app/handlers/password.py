"""обработчик проверки сложности пароля."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.validators.password import PASSWORD_REGEX

FIND_TEXT = 0


async def verify_password_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """запрашивает пароль для проверки."""
    await update.message.reply_text("Введите пароль для проверки сложности.")
    return FIND_TEXT


async def verify_password_result(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """проверяет пароль и сообщает результат."""
    password = update.message.text
    if PASSWORD_REGEX.match(password):
        result = "Пароль сложный"
    else:
        result = "Пароль простой"
    await update.message.reply_text(result)
    return ConversationHandler.END
