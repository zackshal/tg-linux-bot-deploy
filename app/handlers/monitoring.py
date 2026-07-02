"""обработчики команд мониторинга Linux через SSH."""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.services.ssh_client import SSHClient, SSHCommandError
from app.services.system_metrics import (
    get_apt_list_all,
    get_apt_package_info,
    get_auths,
    get_critical,
    get_df,
    get_free,
    get_mpstat,
    get_ps,
    get_release,
    get_services,
    get_ss,
    get_uname,
    get_uptime,
    get_w,
)

MAX_TELEGRAM_MESSAGE_LENGTH = 200


def _get_ssh_client(context: ContextTypes.DEFAULT_TYPE) -> SSHClient:
    """извлекает SSH-клиент из bot_data."""
    return context.bot_data["ssh_client"]


async def send_long_message(update: Update, text: str) -> None:
    """Разбивает длинный текст на несколько сообщений и отправляет их все."""
    # eсли текст короткий, отправляем как обычно
    if len(text) <= MAX_TELEGRAM_MESSAGE_LENGTH:
        await update.message.reply_text(text)
        return

    # разбиваем на блоки по MAX_TELEGRAM_MESSAGE_LENGTH символов
    blocks = []
    start = 0
    while start < len(text):
        end = start + MAX_TELEGRAM_MESSAGE_LENGTH
        # пытаемся разорвать по последнему переводу строки, чтобы не резать строку пополам
        if end < len(text):
            # ищем ближайший \n в пределах 100 символов назад
            last_newline = text.rfind("\n", start, end)
            if last_newline != -1:
                end = last_newline + 1
        blocks.append(text[start:end])
        start = end
    # отправляем все блоки
    for block in blocks:
        await update.message.reply_text(block)
        # небольшая пауза между сообщениями (вежливость перед Telegram API)
        await asyncio.sleep(0.2)


async def get_release_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_release(ssh)
        await update.message.reply_text(output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_uname_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_uname(ssh)
        await update.message.reply_text(output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_uptime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_uptime(ssh)
        await update.message.reply_text(output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_df_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_df(ssh)
        await send_long_message(update, output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_free_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_free(ssh)
        await update.message.reply_text(output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_mpstat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_mpstat(ssh)
        if not output:
            output = "mpstat не установлен на удалённом хосте."
        await update.message.reply_text(output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_w_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_w(ssh)
        await update.message.reply_text(output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_auths_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_auths(ssh)
        await update.message.reply_text(output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_critical_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_critical(ssh)
        if not output:
            output = "Критические события не найдены."
        await update.message.reply_text(output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_ps_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_ps(ssh)
        await send_long_message(update, output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_ss_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_ss(ssh)
        await send_long_message(update, output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def get_services_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ssh = _get_ssh_client(context)
    try:
        output = get_services(ssh)
        await send_long_message(update, output)
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")


# APT LIST (Conversation)
APT_LIST_STATE, APT_SEARCH_STATE = range(2)


async def get_apt_list_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Выберите действие:\n"
        "1. Отправить все пакеты (введите 'all')\n"
        "2. Найти конкретный пакет (введите название пакета)"
    )
    return APT_LIST_STATE


async def get_apt_list_choice(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    text = update.message.text.strip().lower()
    if text == "all":
        ssh = _get_ssh_client(context)
        try:
            output = get_apt_list_all(ssh)
            await send_long_message(update, output)
            return ConversationHandler.END
        except SSHCommandError as e:
            await update.message.reply_text(f"Ошибка: {e}")
            return ConversationHandler.END
    else:
        context.user_data["apt_pkg"] = text
        await update.message.reply_text(f"Ищем информацию о пакете: {text}")
        return APT_SEARCH_STATE


async def get_apt_list_search(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    pkg = context.user_data.get("apt_pkg", update.message.text.strip())
    ssh = _get_ssh_client(context)
    try:
        output = get_apt_package_info(ssh, pkg)
        if not output:
            output = f"Пакет '{pkg}' не найден."
        await update.message.reply_text(output)
        return ConversationHandler.END
    except SSHCommandError as e:
        await update.message.reply_text(f"Ошибка: {e}")
        return ConversationHandler.END
