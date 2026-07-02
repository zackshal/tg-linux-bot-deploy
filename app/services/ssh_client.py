"""низкоуровневый SSH-клиент с обработкой ошибок и автоматическим переподключением."""

import logging
from typing import Optional

import paramiko

logger = logging.getLogger(__name__)


class SSHCommandError(Exception):
    """ошибка выполнения команды на удалённом хосте."""


class SSHClient:
    """клиент для выполнения команд на удалённом Linux-хосте через SSH."""

    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._client: Optional[paramiko.SSHClient] = None

    def connect(self) -> None:
        """установить SSH-соединение."""
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._client.connect(
                hostname=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                timeout=10,
                allow_agent=False,
                look_for_keys=False,
            )
            logger.info("SSH-соединение установлено с %s", self._host)
        except (paramiko.SSHException, OSError) as exc:
            logger.error("Ошибка подключения по SSH: %s", exc)
            raise

    def execute(self, command: str) -> str:
        """выполнить команду и вернуть stdout. При ошибке поднимает SSHCommandError."""
        # проверяем, что клиент существует и транспорт активен
        if self._client is None:
            self.connect()
        transport = self._client.get_transport()
        if transport is None or not transport.is_active():
            self.connect()
        # теперь self._client гарантированно не None
        assert self._client is not None
        _, stdout, stderr = self._client.exec_command(command)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if err:
            logger.warning("stderr от команды '%s': %s", command, err)
        if not out and err:
            raise SSHCommandError(err)
        return out

    def close(self) -> None:
        """закрыть соединение."""
        if self._client:
            self._client.close()
            logger.info("SSH-соединение закрыто.")
