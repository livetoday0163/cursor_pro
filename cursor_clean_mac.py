import os
import shutil
import sys
import getpass
import configparser
import subprocess

def is_root():
    """检查脚本是否以root权限运行"""
    return os.geteuid() == 0

def resource_path(relative_path):
    """获取资源的绝对路径，适用于PyInstaller打包环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是在打包环境中运行，使用当前目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def read_config():
    """读取配置文件"""
    config = configparser.ConfigParser()
    
    # 尝试从脚本所在目录读取配置文件
    config_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config_path = os.path.join(config_dir, 'config_mac.env')
    
    if not os.path.exists(config_path):
        create_default_config(config_path)
    
    config.read(config_path)
    return config

def create_default_config(config_path):
    """创建默认配置文件"""
    config = configparser.ConfigParser()
    username = getpass.getuser()
    default_base_path = os.path.expanduser(f'~/Library/Application Support/Cursor/User')
    
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
    base_path = os.path.expanduser(base_path)  # 确保波浪线被正确解析
    
    print(f"清理 {base_path} 中的文件...")
    
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
    
    # 删除指定文件
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已删除文件: {file_path}")
            else:
                print(f"文件不存在: {file_path}")
        except Exception as e:
            print(f"删除文件 {file_path} 失败: {e}")
    
    # 清空指定文件夹
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
                        print(f"删除 {item_path} 失败: {e}")
                print(f"已清空文件夹: {folder_path}")
            else:
                print(f"文件夹不存在: {folder_path}")
        except Exception as e:
            print(f"清空文件夹 {folder_path} 失败: {e}")
    
    # 删除指定文件夹
    for folder_path in folders_to_delete:
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"已删除文件夹: {folder_path}")
            else:
                print(f"文件夹不存在: {folder_path}")
        except Exception as e:
            print(f"删除文件夹 {folder_path} 失败: {e}")

def main():
    """主函数"""
    if not is_root():
        print("需要root权限来运行此程序")
        print("请使用 sudo 重新运行")
        
        # 判断是否为打包后的应用
        if getattr(sys, 'frozen', False):
            # 如果是打包后的应用，使用完整路径
            app_path = sys.executable
        else:
            # 如果是脚本，使用脚本路径
            app_path = sys.argv[0]
        
        subprocess.call(['sudo', app_path])
        return
    
    print("开始清理 Cursor 应用数据...")
    clean_cursor_files()
    print("清理完成！")
    input("按任意键退出...")

if __name__ == "__main__":
    main() 