"""
TODO

- OS 플랫폼별 Strategy Pattern으로 구현
- Windows Server 지원(PowerShell)
- UI Native Machine LRU Cache 활용해서 연산속도 향상
"""


class SystemCommands:
    @staticmethod
    def get_system_type(ssh):
        stdin, stdout, stderr = ssh.exec_command("uname")
        system_type = stdout.read().decode().strip().lower()
        return system_type

    @staticmethod
    def get_cpu_command(system_type):
        if system_type == "linux":
            return "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"
        elif system_type == "darwin":
            return "top -l 1 | grep 'CPU usage' | awk '{print $3}' | cut -d'%' -f1"
        else:
            raise NotImplementedError(f"Unsupported system type: {system_type}")

    @staticmethod
    def get_memory_command(system_type):
        if system_type == "linux":
            return "LC_ALL=C free -m | awk 'NR==2 {print ($3+$5)/$2 * 100}'"
        elif system_type == "darwin":
            return "vm_stat"
        else:
            raise NotImplementedError(f"Unsupported system type: {system_type}")

    @staticmethod
    def parse_memory_output(system_type, ssh):
        if system_type == "linux":
            stdin, stdout, stderr = ssh.exec_command(
                SystemCommands.get_memory_command(system_type)
            )
            return float(stdout.read().decode().strip())
        elif system_type == "darwin":
            stdin, stdout, stderr = ssh.exec_command("sysctl hw.memsize")
            total = int(stdout.read().decode().strip().split()[1])
            stdin, stdout, stderr = ssh.exec_command(
                SystemCommands.get_memory_command(system_type)
            )
            vm_stat = stdout.read().decode().strip()
            page_size = 4096
            metrics = {}

            for line in vm_stat.split("\n"):
                if ":" in line:
                    key, value = line.split(":")
                    key = key.strip()
                    value = value.strip().rstrip(".")
                    try:
                        metrics[key] = int(value)
                    except ValueError:
                        continue
            used = (
                metrics.get("Pages active", 0)
                + metrics.get("Pages inactive", 0)
                + metrics.get("Pages wired down", 0)
            ) * page_size

            return (used / total) * 100.0
        return 0.0

    @staticmethod
    def get_server_time(ssh):
        stdin, stdout, stderr = ssh.exec_command("date '+%Y-%m-%d %H:%M:%S'")
        return stdout.read().decode().strip()

    @staticmethod
    def get_ping(ssh):
        system_type = SystemCommands.get_system_type(ssh)
        if system_type == "linux":
            cmd = "ping -c 1 localhost | grep 'time=' | cut -d '=' -f 4"
        elif system_type == "darwin":
            cmd = "ping -c 1 localhost | grep 'time=' | cut -d '=' -f 4"
        else:
            return "N/A"

        stdin, stdout, stderr = ssh.exec_command(cmd)
        try:
            return float(stdout.read().decode().split()[0].strip())
        except Exception:
            return "N/A"

    @staticmethod
    def get_timezone(ssh):
        stdin, stdout, stderr = ssh.exec_command("date '+%Z'")
        return stdout.read().decode().strip()

    @staticmethod
    def get_network_command(system_type):
        if system_type == "linux":
            return "cat /proc/net/dev | grep eth0"
        elif system_type == "darwin":
            return "netstat -ib en0 | awk 'NR>1 {print $7, $10}'"
        else:
            raise NotImplementedError(f"Unsupported system type: {system_type}")

    @staticmethod
    def parse_network_traffic(system_type, ssh):
        try:
            stdin, stdout, stderr = ssh.exec_command(
                SystemCommands.get_network_command(system_type)
            )
            output = stdout.read().decode().strip()

            if system_type == "linux":
                stats = output.split()
                if len(stats) >= 10:
                    rx_bytes = int(stats[1])
                    tx_bytes = int(stats[9])
                    return rx_bytes, tx_bytes
            elif system_type == "darwin":
                stats = output.split()
                if len(stats) >= 2:
                    rx_bytes = int(stats[0])
                    tx_bytes = int(stats[1])
                    return rx_bytes, tx_bytes
            return 0, 0
        except (IndexError, ValueError) as e:
            print(f"Error parsing network traffic: {str(e)}")
            return 0, 0

    @staticmethod
    def get_disk_io_command(system_type):
        if system_type == "linux":
            return "cat /proc/diskstats | grep sda"
        elif system_type == "darwin":
            return "iostat -c 2 disk0 | tail -1"
        else:
            raise NotImplementedError(f"Unsupported system type: {system_type}")

    @staticmethod
    def parse_disk_io(system_type, ssh):
        try:
            stdin, stdout, stderr = ssh.exec_command(
                SystemCommands.get_disk_io_command(system_type)
            )
            output = stdout.read().decode().strip()

            if system_type == "linux":
                stats = output.split()
                if len(stats) >= 14:
                    read_bytes = int(stats[5]) * 512
                    write_bytes = int(stats[9]) * 512
                    return read_bytes, write_bytes
            elif system_type == "darwin":
                stats = output.split()
                if len(stats) >= 2:
                    read_bytes = float(stats[0]) * 1024
                    write_bytes = float(stats[1]) * 1024
                    return read_bytes, write_bytes
            return 0, 0
        except (IndexError, ValueError) as e:
            print(f"Error parsing disk I/O: {str(e)}")
            return 0, 0
