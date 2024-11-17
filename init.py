import subprocess
import os
import sys


def parse_ssh_config(config_path):
    # 解析 .ssh/config 文件，提取主机别名、IP 地址、端口和用户
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
        if host_data:  # 添加最后一个主机数据
            hosts.append(host_data)
    return hosts


def display_hosts(hosts):
    # 列出所有主机的别名和 IP，并让用户选择
    print("可用的服务器列表:")
    alias_map = {}
    for idx, host in enumerate(hosts, start=1):
        alias = host.get("alias", "Unknown")
        hostname = host.get("hostname", "Unknown")
        user = host.get("user", "root")
        print(f"{idx}. {alias} - {hostname} ({user})")
        alias_map[str(idx)] = host  # 映射序号到主机
        alias_map[alias] = host  # 映射别名到主机

    print("0. 退出")  # 添加退出选项
    while True:
        choice = input("请输入您想要连接的服务器编号、主机别名，或输入 '0'、'exit'、'q' 退出: ").strip().lower()

        if choice in {"0", "exit", "q"}:
            print("程序已退出。")
            return None  # 退出
        elif choice in alias_map:
            return hosts.index(alias_map[choice])  # 返回对应的索引
        else:
            print("无效的输入，请重新输入。")


def connect_to_host(host):
    # 使用 PowerShell 连接到所选服务器并分配伪终端，添加 HostKeyAlgorithms 参数
    hostname = host.get("hostname")
    port = host.get("port", "22")
    user = host.get("user", "root")
    command = f'powershell -NoExit ssh -t -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -p {port} {user}@{hostname}'

    try:
        process = subprocess.Popen(command, shell=True)
        process.communicate()  # 等待进程完成
    except Exception as e:
        print(f"连接服务器时发生错误: {e}")
        sys.exit(1)  # 异常情况下直接退出


if __name__ == "__main__":
    config_path = os.path.expanduser("~/.ssh/config")
    if not os.path.exists(config_path):
        print(f"未找到 SSH 配置文件: {config_path}")
    else:
        hosts = parse_ssh_config(config_path)
        if not hosts:
            print("未找到任何主机配置")
        else:
            while True:
                selected_index = display_hosts(hosts)
                if selected_index is None:  # 用户选择退出
                    break
                else:
                    connect_to_host(hosts[selected_index])  # 连接服务器后直接退出程序
                    break  # 连接完成后退出主循环

