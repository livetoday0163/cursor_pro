import os
import shutil
import ctypes
import sys
import getpass
import configparser
import json
import time
import random
import string
import hashlib
import uuid
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

def is_admin():
    """检查脚本是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def read_config():
    """读取配置文件"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.env')
    
    if not os.path.exists(config_path):
        create_default_config(config_path)
    
    config.read(config_path)
    return config

def create_default_config(config_path):
    """创建默认配置文件"""
    config = configparser.ConfigParser()
    username = getpass.getuser()
    default_base_path = os.path.join('C:\\Users', username, 'AppData\\Roaming\\Cursor\\User')
    
    config['PATHS'] = {
        'base_path': default_base_path
    }
    
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    
    print(f"已创建默认配置文件: {config_path}")
    print(f"默认路径设置为: {default_base_path}")

def clean_cursor_files():
    """清理Cursor应用的文件和文件夹"""
    # 读取配置文件
    config = read_config()
    base_path = config['PATHS']['base_path']
    
    result_message = f"清理 {base_path} 中的文件...\n"
    
    files_to_delete = [
        os.path.join(base_path, 'globalStorage', 'state.vscdb'),
        os.path.join(base_path, 'globalStorage', 'state.vscdb.backup')
    ]
    
    folders_to_clean = [
        os.path.join(base_path, 'History')
    ]
    
    folders_to_delete = [
        os.path.join(base_path, 'workspaceStorage')
    ]
    
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                result_message += f"已删除文件: {file_path}\n"
            else:
                result_message += f"文件不存在: {file_path}\n"
        except Exception as e:
            result_message += f"删除文件 {file_path} 失败: {e}\n"
    
    for folder_path in folders_to_clean:
        try:
            if os.path.exists(folder_path):
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    except Exception as e:
                        result_message += f"删除 {item_path} 失败: {e}\n"
                result_message += f"已清空文件夹: {folder_path}\n"
            else:
                result_message += f"文件夹不存在: {folder_path}\n"
        except Exception as e:
            result_message += f"清空文件夹 {folder_path} 失败: {e}\n"
    
    for folder_path in folders_to_delete:
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                result_message += f"已删除文件夹: {folder_path}\n"
            else:
                result_message += f"文件夹不存在: {folder_path}\n"
        except Exception as e:
            result_message += f"删除文件夹 {folder_path} 失败: {e}\n"
    
    result_message += "清理完成！"
    return result_message

def get_config_path():
    """根据不同操作系统返回配置文件路径"""
    if sys.platform == "darwin":  # macOS
        base_path = Path("~/Library/Application Support/Cursor/User/globalStorage")
    elif sys.platform == "win32":  # Windows
        base_path = Path(os.environ.get("APPDATA", "")) / "Cursor/User/globalStorage"
    else:  # Linux 和其他类Unix系统
        base_path = Path("~/.config/Cursor/User/globalStorage")
    
    return Path(os.path.expanduser(str(base_path))) / "storage.json"

def is_cursor_running():
    """检查 Cursor 是否正在运行（不依赖第三方库）"""
    try:
        if sys.platform == "win32":
            # Windows
            output = subprocess.check_output('tasklist', shell=True, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
            return any(proc.lower().startswith('cursor') for proc in output.split('\n'))
        else:
            # Unix-like systems (Linux, macOS)
            output = subprocess.check_output(['ps', 'aux'], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
            return any('cursor' in line.lower() for line in output.split('\n'))
    except subprocess.SubprocessError:
        return False  # 如果执行命令失败，假设进程未运行
    except Exception as e:
        return False

# 移除警告对话框，直接执行函数
def check_cursor_process(func):
    """装饰器：检查 Cursor 进程，但不显示警告"""
    def wrapper(*args, **kwargs):
        # 直接执行函数，不显示警告
        return func(*args, **kwargs)
    return wrapper

def kill_cursor_processes():
    """终止所有 Cursor 相关进程"""
    result_message = ""
    try:
        if sys.platform == "win32":
            # Windows
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'Cursor.exe'], 
                             check=False, 
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
                subprocess.run(['taskkill', '/F', '/IM', 'cursor.exe'], 
                             check=False,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
            except subprocess.SubprocessError:
                result_message += "无法找到 Cursor 进程或没有权限终止进程\n"
        else:
            # Unix-like systems (Linux, macOS)
            try:
                # 使用 pgrep 查找进程
                pids = subprocess.check_output(['pgrep', '-i', 'cursor'], 
                                            stderr=subprocess.DEVNULL).decode().split()
                for pid in pids:
                    try:
                        os.kill(int(pid), 15)  # SIGTERM
                        time.sleep(0.1)
                        try:
                            os.kill(int(pid), 0)  # 检查进程是否还存在
                            os.kill(int(pid), 9)  # SIGKILL
                        except ProcessLookupError:
                            pass  # 进程已经终止
                    except ProcessLookupError:
                        continue  # 跳过已经不存在的进程
            except subprocess.CalledProcessError:
                result_message += "未找到 Cursor 进程\n"
            except PermissionError:
                result_message += "没有权限终止进程\n"
        
        result_message += "已尝试终止所有 Cursor 进程"
    except Exception as e:
        result_message += f"终止进程时出错: {str(e)}\n"
    
    return result_message

@check_cursor_process
def reset_machine_ids():
    """重置机器 ID"""
    CONFIG_PATH = get_config_path()
    result_message = ""
    try:
        if not CONFIG_PATH.exists():
            result_message = f"配置文件不存在: {CONFIG_PATH}"
            return result_message
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 删除遥测 ID
        data.pop("telemetry.macMachineId", None)
        data.pop("telemetry.machineId", None)
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        result_message = "已成功重置机器 ID"
    except Exception as e:
        result_message = f"重置机器 ID 时出错: {str(e)}"
    
    return result_message

@check_cursor_process
def generate_random_machine_ids():
    """生成随机的机器 ID"""
    CONFIG_PATH = get_config_path()
    result_message = ""
    try:
        if not CONFIG_PATH.exists():
            result_message = f"配置文件不存在: {CONFIG_PATH}"
            return result_message
        
        # 生成随机字符串并计算其哈希值
        def generate_random_hash():
            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            random_str += str(uuid.uuid4())  # 添加 UUID 增加随机性
            return hashlib.sha256(random_str.encode()).hexdigest()
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 生成新的 ID
        data["telemetry.macMachineId"] = generate_random_hash()
        data["telemetry.machineId"] = generate_random_hash()
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        result_message = "已生成新的机器 ID：\n"
        result_message += f"Mac机器ID: {data['telemetry.macMachineId']}\n"
        result_message += f"机器ID: {data['telemetry.machineId']}"
    except Exception as e:
        result_message = f"生成机器 ID 时出错: {str(e)}"
    
    return result_message

@check_cursor_process
def break_claude_37_limit():
    """突破Claude 3.7 Sonnet限制"""
    CONFIG_PATH = get_config_path()
    result_message = ""
    try:
        if not CONFIG_PATH.exists():
            result_message = f"配置文件不存在: {CONFIG_PATH}"
            return result_message
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 设置突破限制的关键值
        data["cursor.paid"] = True
        data["cursor.openaiFreeTier"] = True
        data["cursor.proTier"] = True
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        result_message = "已成功设置突破 Claude 3.7 Sonnet 限制"
    except Exception as e:
        result_message = f"突破限制时出错: {str(e)}"
    
    return result_message

class CursorEnhanceTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Cursor 增强工具")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        self.setup_ui()
    
    def setup_ui(self):
        # 设置主框架
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(main_frame, text="Cursor 增强工具", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 功能按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="1. 重置机器码", command=self.reset_machine_code).pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="2. 突破 Claude 3.7 Sonnet 限制并清理数据", command=self.break_limit_and_clean).pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="3. 终止 Cursor 进程", command=self.kill_process).pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="4. 退出", command=self.root.quit).pack(fill=tk.X, pady=5)
        
        # 结果文本框
        result_frame = ttk.LabelFrame(main_frame, text="操作结果")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(result_frame, wrap=tk.WORD, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_result(self, message):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, message)
    
    def reset_machine_code(self):
        self.status_var.set("正在重置机器码...")
        self.root.update()
        
        # 先终止Cursor进程
        kill_result = kill_cursor_processes()
        
        # 生成随机机器ID
        result = generate_random_machine_ids()
        
        self.show_result(f"{kill_result}\n\n{result}")
        self.status_var.set("重置机器码完成")
    
    def break_limit_and_clean(self):
        """突破限制并清理数据（合并选项2和3）"""
        self.status_var.set("正在突破限制并清理数据...")
        self.root.update()
        
        # 先终止Cursor进程
        kill_result = kill_cursor_processes()
        
        # 突破限制
        limit_result = break_claude_37_limit()
        
        # 清理文件
        clean_result = clean_cursor_files()
        
        self.show_result(f"{kill_result}\n\n{limit_result}\n\n{clean_result}")
        self.status_var.set("突破限制和清理数据完成")
    
    def kill_process(self):
        self.status_var.set("正在终止 Cursor 进程...")
        self.root.update()
        
        result = kill_cursor_processes()
        
        self.show_result(result)
        self.status_var.set("进程终止完成")

def main():
    """主函数"""
    if not is_admin():
        messagebox.showerror("权限错误", "请以管理员权限运行此脚本")
        # 如果不是管理员权限，尝试以管理员权限重新运行
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return
    
    root = tk.Tk()
    app = CursorEnhanceTool(root)
    root.mainloop()

if __name__ == "__main__":
    main() 