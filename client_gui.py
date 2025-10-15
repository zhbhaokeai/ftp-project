# 导入所需的库
import ftplib
import os
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import threading
import re


class FtpClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FTP 客户端")
        self.geometry("900x600")

        self.ftp = None
        self.current_local_path = os.getcwd()

        # --- 创建界面组件 ---
        self._create_widgets()

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
        self.refresh_local_files()

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

        # --- 操作按钮框架 ---
        actions_frame = ttk.Frame(files_frame)
        actions_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(actions_frame, text="上传 >>", command=self.upload_file).pack(pady=10)
        ttk.Button(actions_frame, text="<< 下载", command=self.download_file).pack(pady=10)
        ttk.Button(actions_frame, text="刷新本地", command=self.refresh_local_files).pack(pady=10)
        ttk.Button(actions_frame, text="刷新远程", command=self.refresh_remote_files).pack(pady=10)

        # --- 日志信息框架 ---
        log_frame = ttk.LabelFrame(self, text="状态日志", padding=(10, 5))
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.log_text = tk.Text(log_frame, height=5, state='disabled')
        self.log_text.pack(expand=True, fill=tk.X)

    # --- 核心功能方法 ---

    def log(self, message):
        """向日志文本框中添加一条消息"""
        if not message.endswith('\n'):
            message += '\n'
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def toggle_connection(self):
        if self.ftp:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        host = self.host_var.get()
        port = int(self.port_var.get())
        user = self.user_var.get()
        password = self.pass_var.get()

        try:
            self.log(f"正在连接到 {host}:{port}...")
            self.ftp = ftplib.FTP()
            self.ftp.connect(host, port, timeout=10)
            self.ftp.login(user, password)
            self.ftp.encoding = "utf-8"
            self.log("连接成功！" + self.ftp.getwelcome())
            self.connect_btn.config(text="断开")
            self.refresh_remote_files()
        except ftplib.all_errors as e:
            self.log(f"连接失败: {e}")
            messagebox.showerror("连接错误", f"无法连接到服务器: {e}")
            self.ftp = None

    def disconnect(self):
        if self.ftp:
            try:
                self.ftp.quit()
                self.log("已断开连接。")
            except ftplib.all_errors as e:
                self.log(f"断开时出错: {e}")
        self.ftp = None
        self.connect_btn.config(text="连接")
        for item in self.remote_tree.get_children():
            self.remote_tree.delete(item)

    def refresh_local_files(self):
        for item in self.local_tree.get_children():
            self.local_tree.delete(item)
        for item in os.listdir(self.current_local_path):
            full_path = os.path.join(self.current_local_path, item)
            try:
                size = os.path.getsize(full_path)
                item_type = "文件夹" if os.path.isdir(full_path) else "文件"
                self.local_tree.insert("", "end", values=(item, f"{size} B", item_type))
            except OSError:
                pass

    def refresh_remote_files(self):
        if not self.ftp:
            self.log("刷新远程列表失败：未连接。")
            return
        for item in self.remote_tree.get_children():
            self.remote_tree.delete(item)
        try:
            # 修正: 使用兼容性更好的 'LIST' 命令代替 'MLSD'
            lines = []
            self.ftp.retrlines('LIST', lines.append)
            for line in lines:
                # 解析 LIST 命令返回的复杂字符串
                parts = line.split()
                if len(parts) < 9:
                    continue

                permissions = parts[0]
                size = parts[4]
                # 文件名可能包含空格，所以从第8个元素开始拼接
                filename = " ".join(parts[8:])

                item_type = "文件夹" if permissions.startswith('d') else "文件"
                size_display = f"{size} B"

                self.remote_tree.insert("", "end", values=(filename.strip(), size_display, item_type))
            self.log("远程文件列表已刷新。")
        except ftplib.all_errors as e:
            self.log(f"获取远程列表失败: {e}")
            messagebox.showerror("错误", f"无法获取远程文件列表: {e}")

    def upload_file(self):
        selected_item = self.local_tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先在本地文件列表中选择一个文件。")
            return

        file_info = self.local_tree.item(selected_item)['values']
        filename = str(file_info[0])
        file_type = str(file_info[2])
        if file_type == "文件夹":
            messagebox.showwarning("提示", "暂不支持上传整个文件夹。")
            return

        local_path = os.path.join(self.current_local_path, filename)
        threading.Thread(target=self._upload_thread, args=(local_path, filename), daemon=True).start()

    def _upload_thread(self, local_path, remote_filename):
        if not self.ftp:
            self.log("上传错误：未连接。")
            messagebox.showerror("错误", "未连接到FTP服务器。")
            return
        try:
            self.log(f"开始上传: {remote_filename}...")
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_filename}', f)
            self.log(f"上传成功: {remote_filename}")
            # 使用 after 确保UI更新在主线程中执行
            self.after(0, self.refresh_remote_files)
        except ftplib.all_errors as e:
            self.log(f"上传失败: {e}")
            messagebox.showerror("上传错误", f"上传文件失败: {e}")

    def download_file(self):
        selected_item = self.remote_tree.focus()
        if not selected_item:
            messagebox.showwarning("提示", "请先在远程服务器列表中选择一个文件。")
            return

        file_info = self.remote_tree.item(selected_item)['values']
        filename = str(file_info[0])
        file_type = str(file_info[2])
        if file_type == "文件夹":
            messagebox.showwarning("提示", "暂不支持下载整个文件夹。")
            return

        local_path = os.path.join(self.current_local_path, filename)
        threading.Thread(target=self._download_thread, args=(filename, local_path), daemon=True).start()

    def _download_thread(self, remote_filename, local_path):
        if not self.ftp:
            self.log("下载错误：未连接。")
            messagebox.showerror("错误", "未连接到FTP服务器。")
            return
        try:
            self.log(f"开始下载: {remote_filename}...")
            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_filename}', f.write)
            self.log(f"下载成功: {remote_filename}")
            self.after(0, self.refresh_local_files)
        except ftplib.all_errors as e:
            self.log(f"下载失败: {e}")
            messagebox.showerror("下载错误", f"下载文件失败: {e}")

    def on_closing(self):
        self.disconnect()
        self.destroy()


if __name__ == "__main__":
    app = FtpClientGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


