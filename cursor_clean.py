import os
import shutil
import ctypes
import sys
import getpass
import configparser

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
    
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已删除文件: {file_path}")
            else:
                print(f"文件不存在: {file_path}")
        except Exception as e:
            print(f"删除文件 {file_path} 失败: {e}")
    
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
    if not is_admin():
        print("请以管理员权限运行此脚本")
        # 如果不是管理员权限，尝试以管理员权限重新运行
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return
    
    print("开始清理 Cursor 应用数据...")
    clean_cursor_files()
    print("清理完成！")
    input("按任意键退出...")

if __name__ == "__main__":
    main() 