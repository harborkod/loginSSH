import subprocess
import os
import sys


def parse_ssh_config(config_path):
    hosts = []
    with open(config_path, 'r') as file:
        host_data = {}
        for line in file:
            line = line.strip()
            if line.startswith("Host "):  # 新的 Host 开始
                if host_data:  # 如果存在前一个主机的数据，则添加到列表中
                    hosts.append(host_data)
                host_data = {"alias": line.split()[1]}
            elif line.startswith("HostName"):
                host_data["hostname"] = line.split()[1]
            elif line.startswith("Port"):
                host_data["port"] = line.split()[1]
            elif line.startswith("User"):
                host_data["user"] = line.split()[1]
            elif line.startswith("IdentityFile"):
                host_data["identityfile"] = line.split()[1]
            elif line.startswith("HostkeyAlgorithms"):
                host_data["hostkeyalgorithms"] = line.split()[1]
            elif line.startswith("PubkeyAcceptedAlgorithms"):
                host_data["pubkeyacceptedalgorithms"] = line.split()[1]
        if host_data:  # 添加最后一个主机数据
            hosts.append(host_data)
    return hosts


def display_hosts(hosts):
    print("=" * 80)
    print(f"{'编号':<6} | {'主机别名':<18} | {'主机名':<20} | {'用户名':<10}")
    print("-" * 80)

    alias_map = {}

    for idx, host in enumerate(hosts, start=1):
        alias = host.get("alias", "Unknown")
        hostname = host.get("hostname", "Unknown")
        user = host.get("user", "root")

        print(f"{idx:<6} | {alias:<18} | {hostname:<20} | {user:<10}")

        alias_map[str(idx)] = host
        alias_map[alias] = host

    print("=" * 80)

    while True:
        choice = input("请输入您想要连接的服务器编号、主机别名，或输入 '0'、'exit'、'q' 退出: ").strip().lower()
        if choice in {"0", "exit", "q"}:
            print("程序已退出。")
            return None
        elif choice in alias_map:
            return alias_map[choice]
        else:
            print("无效的输入，请重新输入。")


def connect_to_host(host):
    hostname = host.get("hostname")
    port = host.get("port", "22")
    user = host.get("user", "root")
    identityfile = host.get("identityfile")
    hostkeyalgorithms = host.get("hostkeyalgorithms", "+ssh-rsa")
    pubkeyacceptedalgorithms = host.get("pubkeyacceptedalgorithms", "+ssh-rsa")

    command = f'powershell -NoExit ssh -tt -o HostKeyAlgorithms={hostkeyalgorithms} -o PubkeyAcceptedAlgorithms={pubkeyacceptedalgorithms} -p {port} -i {identityfile} {user}@{hostname}'

    try:
        process = subprocess.Popen(command, shell=True)
        process.communicate()  # 等待进程完成
    except Exception as e:
        print(f"连接服务器时发生错误: {e}")
        sys.exit(1)  # 异常情况下直接退出


def find_host_by_alias(hosts, alias):
    for host in hosts:
        if host.get("alias") == alias:
            return host
    print(f"未找到别名为 '{alias}' 的主机")
    return None


if __name__ == "__main__":
    config_path = os.path.expanduser("~/.ssh/config")
    if not os.path.exists(config_path):
        print(f"未找到 SSH 配置文件: {config_path}")
        sys.exit(1)

    hosts = parse_ssh_config(config_path)
    if not hosts:
        print("未找到任何主机配置")
        sys.exit(1)

    # 处理命令行输入
    raw_input = " ".join(sys.argv[1:])  # 将命令行所有参数合并成一个字符串
    cleaned_input = raw_input.strip()  # 去掉两侧空格
    command_parts = cleaned_input.split()  # 分割参数为列表

    if len(command_parts) == 0:  # 没有输入有效参数
        selected_host = display_hosts(hosts)
        if selected_host:
            connect_to_host(selected_host)
    elif len(command_parts) == 1:  # 有一个参数
        server_name = command_parts[0]
        host = find_host_by_alias(hosts, server_name)
        if host:
            connect_to_host(host)
        else:
            print(f"未找到别名为 '{server_name}' 的主机，请检查拼写或查看配置。")
            sys.exit(1)
    else:  # 输入参数过多，提示用法
        sys.exit(1)