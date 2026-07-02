import os

from dotenv import load_dotenv

load_dotenv()

# Telegram
TOKEN = os.getenv("TOKEN")

# SSH
RM_HOST = os.getenv("RM_HOST")
RM_PORT_STR = os.getenv("RM_PORT", "22")
RM_USER = os.getenv("RM_USER")
RM_PASSWORD = os.getenv("RM_PASSWORD")

# PostgreSQL – используем переменные из .env
# Если в .env есть DB_HOST, DB_PORT и т.д. – можно взять их
PG_HOST = os.getenv("PG_HOST", os.getenv("DB_HOST", "localhost"))
PG_PORT_STR = os.getenv("PG_PORT", os.getenv("DB_PORT", "5432"))
PG_SLAVE_HOST = os.getenv("PG_SLAVE_HOST", "localhost")
PG_SLAVE_PORT_STR = os.getenv("PG_SLAVE_PORT", "5433")
PG_DB = os.getenv("PG_DB", os.getenv("DB_DATABASE", "db_customers"))
PG_USER = os.getenv("PG_USER", os.getenv("DB_USER", "postgres"))
PG_PASSWORD = os.getenv("PG_PASSWORD", os.getenv("DB_PASSWORD", ""))

# Проверка обязательных переменных
if not all([TOKEN, RM_HOST, RM_USER, RM_PASSWORD]):
    raise ValueError(
        "Не заданы необходимые переменные: TOKEN, RM_HOST, RM_USER, RM_PASSWORD"
    )

# Преобразование портов
try:
    RM_PORT = int(RM_PORT_STR)
    PG_PORT = int(PG_PORT_STR)
    PG_SLAVE_PORT = int(PG_SLAVE_PORT_STR)
except ValueError as exc:
    raise ValueError("Порты должны быть целыми числами") from exc
