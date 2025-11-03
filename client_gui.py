import ftplib
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading


class FtpClientGUI(tk.Tk):
    """
    一个支持文件和文件夹传输的图形化FTP客户端。
    """

    def __init__(self):
        super().__init__()
        self.title("FTP 客户端 (支持文件夹传输)")
        self.geometry("900x600")

        self.ftp = None
        self.current_local_path = os.getcwd()

        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_widgets(self):
        # --- 连接信息框架 ---
        conn_frame = ttk.LabelFrame(self, text="连接信息", padding=(10, 5))
        conn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        ttk.Label(conn_frame, text="主机:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(conn_frame, textvariable=self.host_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(conn_frame, text="端口:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.port_var = tk.StringVar(value="2121")
        ttk.Entry(conn_frame, textvariable=self.port_var, width=10).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(conn_frame, text="用户名:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.user_var = tk.StringVar(value="user")
        ttk.Entry(conn_frame, textvariable=self.user_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(conn_frame, text="密码:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.pass_var = tk.StringVar(value="12345")
        ttk.Entry(conn_frame, textvariable=self.pass_var, show="*").grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.connect_btn = ttk.Button(conn_frame, text="连接", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=4, rowspan=2, padx=10, pady=5, sticky="ns")

        conn_frame.columnconfigure(1, weight=1)
        conn_frame.columnconfigure(3, weight=1)

        # --- 文件列表框架 ---
        files_frame = ttk.Frame(self)
        files_frame.pack(expand=True, fill=tk.BOTH, padx=10)

        # 操作按钮框架
        actions_frame = ttk.Frame(files_frame)
        actions_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, anchor='n', pady=20)

        ttk.Button(actions_frame, text="上传 >>", command=self.upload_item).pack(pady=10)
        ttk.Button(actions_frame, text="<< 下载", command=self.download_item).pack(pady=10)
        ttk.Button(actions_frame, text="刷新本地", command=self.refresh_local_files).pack(pady=30)
        ttk.Button(actions_frame, text="刷新远程", command=self.refresh_remote_files).pack(pady=10)

        # 本地文件列表
        local_frame = ttk.LabelFrame(files_frame, text="本地文件")
        local_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.local_tree = ttk.Treeview(local_frame, columns=("filename", "size", "type"), show="headings")
        self.local_tree.heading("filename", text="文件名")
        self.local_tree.heading("size", text="大小")
        self.local_tree.heading("type", text="类型")
        self.local_tree.column("filename", width=200)
        self.local_tree.column("size", width=100, anchor='e')
        self.local_tree.column("type", width=100, anchor='center')
        self.local_tree.pack(expand=True, fill=tk.BOTH)

        # 远程文件列表
        remote_frame = ttk.LabelFrame(files_frame, text="远程服务器文件")
        remote_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.remote_tree = ttk.Treeview(remote_frame, columns=("filename", "size", "type"), show="headings")
        self.remote_tree.heading("filename", text="文件名")
        self.remote_tree.heading("size", text="大小")
        self.remote_tree.heading("type", text="类型")
        self.remote_tree.column("filename", width=200)
        self.remote_tree.column("size", width=100, anchor='e')
        self.remote_tree.column("type", width=100, anchor='center')
        self.remote_tree.pack(expand=True, fill=tk.BOTH)

        # --- 日志信息框架 ---
        log_frame = ttk.LabelFrame(self, text="状态日志", padding=(10, 5))
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.log_text = tk.Text(log_frame, height=5, state='disabled')
        self.log_text.pack(expand=True, fill=tk.BOTH)

        self.refresh_local_files()

    def log(self, message):
        """向日志窗口打印消息"""
        if not message.endswith('\n'):
            message += '\n'
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def toggle_connection(self):
        """切换连接/断开状态"""
        if self.ftp:
            self.disconnect()
        else:
            # 在新线程中执行连接，避免界面卡顿
            threading.Thread(target=self.connect, daemon=True).start()

    def connect(self):
        """连接到FTP服务器"""
        host = self.host_var.get()
        port = int(self.port_var.get())
        user = self.user_var.get()
        password = self.pass_var.get()

        try:
            self.after(0, lambda: self.log(f"正在连接到 {host}:{port}..."))
            ftp_instance = ftplib.FTP()
            ftp_instance.connect(host, port, timeout=10)
            ftp_instance.login(user, password)

            # --- 这是新的、完整的UTF-8解决方案 ---

            # 1. 显式地告诉服务器：请将此连接的控制编码切换到 UTF-8
            #    (这需要服务器端设置了 handler.encoding = "utf-8" 才能成功)
            try:
                ftp_instance.sendcmd('OPTS UTF8 ON')
                self.after(0, lambda: self.log("UTF-8 模式已成功开启。"))
            except ftplib.all_errors as e:
                self.after(0, lambda: self.log(f"警告：服务器可能不支持 UTF-8。 {e}"))

            # 2. 显式地告诉 ftplib 库：在 *发送*(Encode) 和 *接收*(Decode) 时
            #    都必须使用 'utf-8' 编码。
            #    这将修复 'latin-1' 编码错误。
            ftp_instance.encoding = 'utf-8'

            # --- 解决方案结束 ---

            self.ftp = ftp_instance

            self.after(0, lambda: self.log("连接成功！" + self.ftp.getwelcome()))
            self.after(0, lambda: self.connect_btn.config(text="断开"))
            self.after(0, self.refresh_remote_files)

        except ftplib.all_errors as e:
            self.ftp = None
            self.after(0, lambda: self.log(f"连接失败: {e}"))
            self.after(0, lambda: messagebox.showerror("连接错误", f"无法连接到服务器: {e}"))

    def disconnect(self):
        """断开与FTP服务器的连接"""
        if self.ftp:
            try:
                self.ftp.quit()
                self.log("已断开连接。")
            except ftplib.all_errors as e:
                self.log(f"断开时出错: {e}")
        self.ftp = None
        self.connect_btn.config(text="连接")
        # 清空远程文件列表
        for item in self.remote_tree.get_children():
            self.remote_tree.delete(item)

    def refresh_local_files(self):
        """刷新本地文件列表"""
        for item in self.local_tree.get_children():
            self.local_tree.delete(item)
        for item in os.listdir(self.current_local_path):
            full_path = os.path.join(self.current_local_path, item)
            try:
                size = os.path.getsize(full_path)
                item_type = "文件夹" if os.path.isdir(full_path) else "文件"
                self.local_tree.insert("", "end", values=(item, f"{size} B", item_type))
            except OSError:
                pass  # 忽略无法访问的文件

    def refresh_remote_files(self):
        """刷新远程文件列表"""
        if not self.ftp:
            self.log("刷新远程列表失败：未连接。")
            return

        for item in self.remote_tree.get_children():
            self.remote_tree.delete(item)

        try:
            lines = []
            self.ftp.retrlines('LIST', lines.append)
            for line in lines:
                parts = line.split()
                if len(parts) < 9: continue
                permissions, size, filename = parts[0], parts[4], " ".join(parts[8:])
                item_type = "文件夹" if permissions.startswith('d') else "文件"
                self.remote_tree.insert("", "end", values=(filename.strip(), f"{size} B", item_type))
            self.log("远程文件列表已刷新。")
        except ftplib.all_errors as e:
            self.log(f"获取远程列表失败: {e}")
            messagebox.showerror("错误", f"无法获取远程文件列表: {e}")

    def upload_item(self):
        """上传选定的文件或文件夹"""
        selected_item = self.local_tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先在本地文件列表中选择一个文件或文件夹。")
            return

        info = self.local_tree.item(selected_item)['values']
        name, item_type = str(info[0]), str(info[2])
        local_path = os.path.join(self.current_local_path, name)

        if item_type == "文件":
            threading.Thread(target=self._upload_file_thread, args=(local_path, name), daemon=True).start()
        else:  # 是文件夹
            threading.Thread(target=self._upload_folder_thread, args=(local_path, name), daemon=True).start()
#应用层
    def _upload_file_thread(self, local_path, remote_filename):
        if not self.ftp: self.log("上传错误：未连接。"); return
        try:
            self.after(0, lambda: self.log(f"开始上传文件: {remote_filename}..."))
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_filename}', f)
            self.after(0, lambda: self.log(f"上传文件成功: {remote_filename}"))
            self.after(0, self.refresh_remote_files)
        except ftplib.all_errors as e:
            self.after(0, lambda: self.log(f"上传文件失败: {e}"))
            self.after(0, lambda: messagebox.showerror("上传错误", f"上传文件失败: {e}"))

    def _upload_folder_thread(self, local_path, remote_foldername):
        if not self.ftp: self.log("上传错误：未连接。"); return
        try:
            self.after(0, lambda: self.log(f"开始上传文件夹: {remote_foldername}..."))
            self.ftp.mkd(remote_foldername)
            for root, _, files in os.walk(local_path):
                remote_path = os.path.join(remote_foldername, os.path.relpath(root, local_path)).replace("\\", "/")
                if remote_path != remote_foldername:  # 避免重复创建根目录
                    try:
                        self.ftp.mkd(remote_path)
                    except ftplib.all_errors:
                        pass  # 文件夹可能已存在

                for f in files:
                    local_file_path = os.path.join(root, f)
                    remote_file_path = os.path.join(remote_path, f).replace("\\", "/")
                    with open(local_file_path, 'rb') as file_obj:
                        self.ftp.storbinary(f'STOR {remote_file_path}', file_obj)
            self.after(0, lambda: self.log(f"上传文件夹成功: {remote_foldername}"))
            self.after(0, self.refresh_remote_files)
        except ftplib.all_errors as e:
            self.after(0, lambda: self.log(f"上传文件夹失败: {e}"))
            self.after(0, lambda: messagebox.showerror("上传错误", f"上传文件夹失败: {e}"))

    def download_item(self):
        """下载选定的文件或文件夹"""
        selected_item = self.remote_tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先在远程服务器列表中选择一个文件或文件夹。")
            return

        info = self.remote_tree.item(selected_item)['values']
        name, item_type = str(info[0]), str(info[2])
        local_path = os.path.join(self.current_local_path, name)

        if item_type == "文件":
            threading.Thread(target=self._download_file_thread, args=(name, local_path), daemon=True).start()
        else:  # 是文件夹
            threading.Thread(target=self._download_folder_thread, args=(name, local_path), daemon=True).start()

    def _download_file_thread(self, remote_filename, local_path):
        if not self.ftp: self.log("下载错误：未连接。"); return
        try:
            self.after(0, lambda: self.log(f"开始下载文件: {remote_filename}..."))
            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_filename}', f.write)
            self.after(0, lambda: self.log(f"下载文件成功: {remote_filename}"))
            self.after(0, self.refresh_local_files)
        except ftplib.all_errors as e:
            self.after(0, lambda: self.log(f"下载文件失败: {e}"))
            self.after(0, lambda: messagebox.showerror("下载错误", f"下载文件失败: {e}"))

    def _download_folder_thread(self, remote_foldername, local_path):
        if not self.ftp: self.log("下载错误：未连接。"); return
        try:
            self.after(0, lambda: self.log(f"开始下载文件夹: {remote_foldername}..."))
            os.makedirs(local_path, exist_ok=True)
            self._recursive_download(remote_foldername, local_path)
            self.after(0, lambda: self.log(f"下载文件夹成功: {remote_foldername}"))
            self.after(0, self.refresh_local_files)
        except ftplib.all_errors as e:
            self.after(0, lambda: self.log(f"下载文件夹失败: {e}"))
            self.after(0, lambda: messagebox.showerror("下载错误", f"下载文件夹失败: {e}"))

    def _recursive_download(self, remote_path, local_path):
        """递归地下载文件夹内容"""
        # 使用 MLSD 获取更详细的列表信息，遍历当前远程文件夹(remote_path)里的所有内容
        for name, facts in self.ftp.mlsd(remote_path):
            if name in ('.', '..'): continue

            local_item_path = os.path.join(local_path, name)
            remote_item_path = os.path.join(remote_path, name).replace("\\", "/")
            # 2. 判断这个东西是文件夹(dir)还是文件(file)
            if facts['type'] == 'dir':
                os.makedirs(local_item_path, exist_ok=True)
                self._recursive_download(remote_item_path, local_item_path)
            elif facts['type'] == 'file':
                with open(local_item_path, 'wb') as f:
                    self.ftp.retrbinary(f'RETR {remote_item_path}', f.write)

    def on_closing(self):
        """关闭窗口时的处理"""
        self.disconnect()
        self.destroy()


if __name__ == "__main__":
    app = FtpClientGUI()
    app.mainloop()



