import os

LOG_PATH = "/var/log/postgresql/postgresql-17-main.log"


def get_replication_logs(lines=50):
    try:
        with open(LOG_PATH, "r") as f:
            tail = f.readlines()[-lines:]
        return "".join(tail)
    except Exception as e:
        return f"Ошибка чтения логов: {e}"
