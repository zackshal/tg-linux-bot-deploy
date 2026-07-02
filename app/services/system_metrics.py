"""высокоуровневые функции для сбора системных метрик через SSH."""

from app.services.ssh_client import SSHClient


# Эти функции принимают клиент, чтобы можно было мокать его в тестах.
def get_release(ssh: SSHClient) -> str:
    """информация о релизе."""
    return ssh.execute("cat /etc/os-release 2>/dev/null || cat /etc/*release")


def get_uname(ssh: SSHClient) -> str:
    return ssh.execute("uname -a")


def get_uptime(ssh: SSHClient) -> str:
    return ssh.execute("uptime")


def get_df(ssh: SSHClient) -> str:
    return ssh.execute("df -h")


def get_free(ssh: SSHClient) -> str:
    return ssh.execute("free -m")


def get_mpstat(ssh: SSHClient) -> str:
    return ssh.execute("mpstat 1 1")


def get_w(ssh: SSHClient) -> str:
    return ssh.execute("w")


def get_auths(ssh: SSHClient) -> str:
    return ssh.execute("last -n 10")


def get_critical(ssh: SSHClient) -> str:
    out = ssh.execute("journalctl -p crit -n 5 --no-pager")
    if not out:
        out = ssh.execute("grep -i 'crit' /var/log/syslog | tail -n 5")
    return out


def get_ps(ssh: SSHClient) -> str:
    return ssh.execute("ps aux")


def get_ss(ssh: SSHClient) -> str:
    return ssh.execute("ss -tulpn")


def get_services(ssh: SSHClient) -> str:
    return ssh.execute("systemctl list-units --type=service --state=running")


def get_apt_list_all(ssh: SSHClient) -> str:
    return ssh.execute("dpkg -l | tail -n +6")


def get_apt_package_info(ssh: SSHClient, package: str) -> str:
    return ssh.execute(
        f"dpkg -s {package} 2>/dev/null || apt-cache show {package} 2>/dev/null"
    )
