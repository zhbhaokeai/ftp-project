import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def main():
    """主函数，用于启动FTP服务器"""
    # --- 1. 设置用户和权限 ---
    authorizer = DummyAuthorizer()

    # 添加一个名为'user'的用户
    # 参数: 用户名, 密码, 用户根目录, 权限字符串
    # "e" = 改变目录 (CWD, CDUP)
    # "l" = 列出文件 (LIST, NLST, STAT, MLSD, MLST, SIZE)
    # "r" = 从服务器检索文件 (RETR)
    # "a" = 附加文件数据 (APPE)
    # "d" = 删除文件或目录 (DELE, RMD)
    # "f" = 重命名文件或目录 (RNFR, RNTO)
    # "m" = 创建目录 (MKD)
    # "w" = 向服务器存储文件 (STOR)
    # "M" = 改变文件模式/权限 (SITE CHMOD)
    # "T" = 改变文件修改时间 (SITE MFMT)
    user_home_dir = os.path.join(os.getcwd(), 'ftp_data', 'user')
    os.makedirs(user_home_dir, exist_ok=True)
    authorizer.add_user('user', '12345', user_home_dir, perm='elradfmwMT')

    # 添加匿名用户
    anonymous_home_dir = os.path.join(os.getcwd(), 'ftp_data', 'anonymous')
    os.makedirs(anonymous_home_dir, exist_ok=True)
    # 修正: 为匿名用户也添加明确的、完整的权限
    authorizer.add_anonymous(anonymous_home_dir, perm='elradfmwMT')

    # --- 2. 配置服务器处理器 ---
    handler = FTPHandler
    handler.authorizer = authorizer

    # 设置欢迎语
    handler.banner = "FTP Server is ready."

    # 可选: 开启被动模式(通常需要)
    # handler.passive_ports = range(60000, 65535)

    # --- 3. 启动服务器 ---
    address = ('0.0.0.0', 2121)  # 监听所有网络接口的2121端口
    server = FTPServer(address, handler)

    # 配置服务器参数
    server.max_cons = 256
    server.max_cons_per_ip = 5

    print(f"FTP服务器正在启动，监听地址 {address[0]}:{address[1]}")
    server.serve_forever()


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
