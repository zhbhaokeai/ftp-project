# 导入所需的库
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def main():
    """
    主函数，用于设置并启动FTP服务器
    """
    # --- 步骤 1: 设置用户权限和目录 ---

    # 创建一个虚拟授权器
    authorizer = DummyAuthorizer()

    # 添加一个名为 'user' 的用户
    # 参数: 用户名, 密码, 主目录, 权限 'elradfmwMT' 代表完全权限
    user_dir = os.path.join(os.getcwd(), "ftp_data", "user")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    authorizer.add_user("user", "12345", user_dir, perm="elradfmwMT")

    # 添加一个匿名用户
    # 为匿名用户指定一个只读文件夹
    anonymous_dir = os.path.join(os.getcwd(), "ftp_data", "anonymous")
    if not os.path.exists(anonymous_dir):
        os.makedirs(anonymous_dir)
    authorizer.add_anonymous(anonymous_dir, perm="elr")  # 匿名用户只有列出和读取权限

    # --- 步骤 2: 设置服务器处理器 ---

    # 实例化FTP处理器
    handler = FTPHandler
    handler.authorizer = authorizer

    # 修正: 将欢迎语改为纯英文，以避免任何编码问题
    handler.banner = "FTP Server is ready."

    # 告诉处理器，所有通信都使用UTF-8
    handler.encoding = "utf-8"

    # --- 步骤 3: 启动服务器 ---

    # 定义服务器监听的地址和端口
    address = ("0.0.0.0", 2121)

    # 创建服务器实例
    server = FTPServer(address, handler)

    # 设置最大连接数
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # 启动服务器并开始监听
    print(f"FTP服务器正在启动，监听地址 {address[0]}:{address[1]}")
    server.serve_forever()


if __name__ == "__main__":
    main()
