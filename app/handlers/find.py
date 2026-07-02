"""обработчики для поиска email и телефонов."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.validators.email_phone import EMAIL_REGEX, PHONE_REGEX

FIND_TEXT = 0


async def find_email_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:  # pylint: disable=unused-argument
    """запрашивает текст для поиска email."""
    await update.message.reply_text(
        "Отправьте текст, в котором нужно найти email-адреса."
    )
    return FIND_TEXT


async def find_email_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ищет email в тексте и выводит результат."""
    text = update.message.text
    emails = EMAIL_REGEX.findall(text)
    if emails:
        result = "Найденные email-адреса:\n" + "\n".join(emails)
    else:
        result = "Email-адреса не найдены."
    await update.message.reply_text(result)
    return ConversationHandler.END


async def find_phone_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """запрашивает текст для поиска номеров телефонов."""
    await update.message.reply_text(
        "Отправьте текст, в котором нужно найти номера телефонов."
    )
    return FIND_TEXT


async def find_phone_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ищет номера телефонов в тексте и выводит результат."""
    text = update.message.text
    phones = PHONE_REGEX.findall(text)
    if phones:
        result = "Найденные номера телефонов:\n" + "\n".join(phones)
    else:
        result = "Номера телефонов не найдены."
    await update.message.reply_text(result)
    return ConversationHandler.END
