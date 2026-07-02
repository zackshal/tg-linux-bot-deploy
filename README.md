# tg-linux-bot
![Python Version](https://img.shields.io/badge/python-3.13-blue)
![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-20.7-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Ansible](https://img.shields.io/badge/Ansible-9.0.0-red)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
## Возможности 🚀

tg-linux-bot — это Telegram-бот на Python, который мониторит Linux-сервера через SSH и управляет PostgreSQL. Бот может искать данные в тексте и проверять сложность пароля.

## Стек технологий 🛠️

| Библиотека/Сервис | Версия |
| --- | --- |
| Python | 3.13 |
| python-telegram-bot | 20.7 |
| paramiko | 3.4.0 |
| psycopg2-binary |  |
| python-dotenv |  |
| pytest |  |
| pytest-asyncio |  |

## Архитектура 🏗️

tg-linux-bot использует микросервисную архитектуру, где каждый функционал реализован в виде отдельного сервиса. Общение между сервисами происходит через асинхронные вызовы.

## Структура проекта 📁

```
tg-linux-bot/
│
├── app/
│   ├── handlers/
│   ├── services/
│   ├── validators/
│   ├── config.py
│   └── main.py
│
├── infrastructure/
│   ├── ansible/
│   ├── docker/
│   └── logs/
│
├── tests/
│
├── docs/
│
├── scripts/
│
├── .env.example.dev
├── requirements.txt
└── pyproject.toml
```

## Быстрый старт 

### Локальный запуск

1. Создайте виртуальное окружение:
   ```bash
   python3 -m venv venv && source venv/bin/activate
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Создайте файл `.env` на основе `.env.example.dev` и отредактируйте его (TOKEN, RM_HOST, RM_PORT, RM_USER, RM_PASSWORD, DB_*)
4. Запустите бота:
   ```bash
   python app/main.py
   ```

### Развёртывание через Ansible

1. Поднимите контейнеры:
   ```bash
   docker compose -f infrastructure/docker/docker-compose.yml up -d
   ```
2. Скопируйте SSH-ключи в контейнеры (команды в README)
3. Установите Python в контейнерах:
   ```bash
   apk add python3
   ```
4. Запустите Ansible playbook:
   ```bash
   cd infrastructure/ansible && ansible-playbook -i inventory playbook_tg_bot.yml
   ```

## Команды бота 📜

| Команда | Описание |
| --- | --- |
| /get_release | Получить информацию о релизе ОС |
| /get_uname | Получить архитектуру, хост и версию ядра |
| /get_uptime | Получить время работы системы |
| /get_df | Получить использование дисков |
| /get_free | Получить оперативную память |
| /get_mpstat | Получить загрузку CPU |
| /get_w | Получить количество пользователей в системе |
| /get_auths | Получить последние 10 входов |
| /get_critical | Получить последние 5 критических событий |
| /get_ps | Получить список запущенных процессов |
| /get_ss | Получить используемые порты |
| /get_services | Получить список запущенных сервисов |
| /get_apt_list | Получить список установленных пакетов |
| /find_email | Найти email-адреса в тексте |
| /find_phone_number | Найти номера телефонов в тексте |
| /verify_password | Проверить пароль на сложность |
| /get_repl_logs | Получить логи репликации |
| /get_emails | Получить список сохраненных email |
| /get_phone_numbers | Получить список сохраненных телефонов |
| /add_email | Добавить email из текста |
| /add_phone | Добавить телефон |

## Устранение проблем 🛠️

| Проблема | Решение |
| --- | --- |
| Бот не отвечает | Проверьте, не превышает ли количество запросов Telegram API |
| Ошибка SSH | Убедитесь, что SSH-ключи корректно скопированы в контейнеры |
| Проблемы с PostgreSQL | Проверьте конфигурацию `.env` и подключение к БД |

