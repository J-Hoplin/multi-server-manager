import paramiko
import socket
from manager.database.manager import ApplicationPersistManager
from typing import Optional, Tuple

database = ApplicationPersistManager()


def get_connections():
    return database.get_connections()


def save_connection(
    name, host, port, user, connection_type, password=None, key_file=None
) -> bool:
    return database.add_connection(
        name, host, port, user, connection_type, password, key_file
    )


def delete_connection(connection_id: int):
    return database.delete_connection(connection_id)


def test_ssh_connection(
    host: str,
    port: int,
    username: str,
    password: Optional[str] = None,
    key_file: Optional[str] = None,
    timeout: int = 15,
) -> Tuple[bool, Optional[str]]:
    """
    Return

    - param[0]: If Success
    - param[1]: Error Message
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if key_file:
            ssh_key = paramiko.RSAKey.from_private_key_file(key_file)
            ssh_client.connect(
                hostname=host,
                port=port,
                username=username,
                pkey=ssh_key,
                timeout=timeout,
            )
        else:
            ssh_client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
            )
        return True, ""
    except paramiko.AuthenticationException:
        return False, "Authentication failed"
    except paramiko.SSHException:
        return False, "SSH Connection failed"
    except socket.error:
        return False, "Out of Socket Connection"
    except Exception as e:
        return False, str(e)
    finally:
        ssh_client.close()
