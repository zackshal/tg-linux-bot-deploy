"""главный модуль для запуска Telegram-бота."""

import logging
from typing import cast

import paramiko
from telegram import Update
from telegram.ext import CallbackQueryHandler  # обязательно добавить!
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.config import (
    PG_DB,
    PG_HOST,
    PG_PASSWORD,
    PG_PORT,
    PG_SLAVE_HOST,
    PG_SLAVE_PORT,
    PG_USER,
    RM_HOST,
    RM_PASSWORD,
    RM_PORT,
    RM_USER,
    TOKEN,
)
from app.handlers.find import (
    FIND_TEXT,
    find_email_result,
    find_email_start,
    find_phone_result,
    find_phone_start,
)
from app.handlers.monitoring import (
    APT_LIST_STATE,
    APT_SEARCH_STATE,
    get_apt_list_choice,
    get_apt_list_search,
    get_apt_list_start,
    get_auths_cmd,
    get_critical_cmd,
    get_df_cmd,
    get_free_cmd,
    get_mpstat_cmd,
    get_ps_cmd,
    get_release_cmd,
    get_services_cmd,
    get_ss_cmd,
    get_uname_cmd,
    get_uptime_cmd,
    get_w_cmd,
)
from app.handlers.password import verify_password_result, verify_password_start
from app.handlers.postgres import (
    WAITING_EMAIL_TEXT,
    WAITING_PHONE_TEXT,
    add_email_start,
    add_email_text,
    add_phone_start,
    add_phone_text,
    email_confirm_callback,
    get_emails,
    get_phone_numbers,
    get_repl_logs,
    phone_confirm_callback,
)
from app.services.postgres_client import PostgresClient
from app.services.ssh_client import SSHClient

# настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот для мониторинга Linux и поиска данных.\n"
        "Используй /help для списка команд. ⸜(｡˃ ᵕ ˂ )⸝♡"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/find_email - найти email в тексте\n"
        "/find_phone_number - найти номера телефонов\n"
        "/verify_password - проверить сложность пароля\n"
        "Мониторинг:\n"
        "/get_release - информация о релизе\n"
        "/get_uname - архитектура, хост, версия ядра\n"
        "/get_uptime - время работы\n"
        "/get_df - файловые системы\n"
        "/get_free - оперативная память\n"
        "/get_mpstat - производительность CPU\n"
        "/get_w - пользователи в системе\n"
        "/get_auths - последние 10 входов\n"
        "/get_critical - последние 5 критических событий\n"
        "/get_ps - запущенные процессы\n"
        "/get_ss - используемые порты\n"
        "/get_apt_list - установленные пакеты\n"
        "/get_services - запущенные сервисы\n"
        "PostgreSQL:\n"
        "/get_repl_logs - логи репликации\n"
        "/get_emails - список email\n"
        "/get_phone_numbers - список телефонов\n"
        "/add_email - добавить email (с извлечением из текста)\n"
        "/add_phone - добавить телефон"
    )


def main() -> None:
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # 1. Проверка переменных
    if not all([RM_HOST, RM_USER, RM_PASSWORD]):
        raise ValueError("Не заданы RM_HOST, RM_USER или RM_PASSWORD")
    if not PG_PASSWORD:
        logger.warning("Пароль PostgreSQL не задан, возможно используется peer auth")

    # 2. Создание SSH-клиента
    ssh_client = SSHClient(
        host=cast(str, RM_HOST),
        port=RM_PORT,
        username=cast(str, RM_USER),
        password=cast(str, RM_PASSWORD),
    )
    try:
        ssh_client.connect()
    except (OSError, paramiko.SSHException) as e:
        logger.error("Не удалось подключиться к удалённому хосту при старте: %s", e)

    # 3. Создание клиентов PostgreSQL
    master_db = PostgresClient(PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD)
    slave_db = PostgresClient(PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD)

    # 4. Создание приложения Telegram
    application = Application.builder().token(TOKEN).build()

    # 5. Сохранение клиентов в bot_data (после создания application)
    application.bot_data["ssh_client"] = ssh_client
    application.bot_data["master_db"] = master_db
    application.bot_data["slave_db"] = slave_db

    # 6. Conversation handlers
    conv_find_email = ConversationHandler(
        entry_points=[CommandHandler("find_email", find_email_start)],
        states={
            FIND_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, find_email_result)
            ]
        },
        fallbacks=[],
    )
    conv_find_phone = ConversationHandler(
        entry_points=[CommandHandler("find_phone_number", find_phone_start)],
        states={
            FIND_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, find_phone_result)
            ]
        },
        fallbacks=[],
    )
    conv_verify_password = ConversationHandler(
        entry_points=[CommandHandler("verify_password", verify_password_start)],
        states={
            FIND_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, verify_password_result)
            ]
        },
        fallbacks=[],
    )
    conv_apt_list = ConversationHandler(
        entry_points=[CommandHandler("get_apt_list", get_apt_list_start)],
        states={
            APT_LIST_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_apt_list_choice)
            ],
            APT_SEARCH_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_apt_list_search)
            ],
        },
        fallbacks=[],
    )

    # Диалог для добавления email
    add_email_conv = ConversationHandler(
        entry_points=[CommandHandler("add_email", add_email_start)],
        states={
            WAITING_EMAIL_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_email_text),
                CallbackQueryHandler(
                    email_confirm_callback, pattern="^(confirm_email|cancel_email)$"
                ),
            ]
        },
        fallbacks=[],
    )
    # Диалог для добавления телефона
    add_phone_conv = ConversationHandler(
        entry_points=[CommandHandler("add_phone", add_phone_start)],
        states={
            WAITING_PHONE_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_phone_text),
                CallbackQueryHandler(
                    phone_confirm_callback, pattern="^(confirm_phone|cancel_phone)$"
                ),
            ]
        },
        fallbacks=[],
    )

    # Регистрация всех обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_find_email)
    application.add_handler(conv_find_phone)
    application.add_handler(conv_verify_password)
    application.add_handler(conv_apt_list)
    application.add_handler(add_email_conv)
    application.add_handler(add_phone_conv)

    # Мониторинг
    application.add_handler(CommandHandler("get_release", get_release_cmd))
    application.add_handler(CommandHandler("get_uname", get_uname_cmd))
    application.add_handler(CommandHandler("get_uptime", get_uptime_cmd))
    application.add_handler(CommandHandler("get_df", get_df_cmd))
    application.add_handler(CommandHandler("get_free", get_free_cmd))
    application.add_handler(CommandHandler("get_mpstat", get_mpstat_cmd))
    application.add_handler(CommandHandler("get_w", get_w_cmd))
    application.add_handler(CommandHandler("get_auths", get_auths_cmd))
    application.add_handler(CommandHandler("get_critical", get_critical_cmd))
    application.add_handler(CommandHandler("get_ps", get_ps_cmd))
    application.add_handler(CommandHandler("get_ss", get_ss_cmd))
    application.add_handler(CommandHandler("get_services", get_services_cmd))

    # PostgreSQL (функции из handlers.postgres – без суффикса _cmd)
    application.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    application.add_handler(CommandHandler("get_emails", get_emails))
    application.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

    logger.info("Бот запущен...")
    application.run_polling()

    # Закрытие ресурсов при остановке
    ssh_client.close()
    master_db.close()
    slave_db.close()


if __name__ == "__main__":
    main()
