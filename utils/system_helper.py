import winreg
import sys
import os

def set_auto_start(app_name, command, enable):
    """
    设置或取消 Windows 注册表中的开机自启动项。

    Args:
        app_name (str): 在注册表中显示的应用程序名称 (例如, "MyApp")。
        command (str): 应用程序启动命令 (例如, "C:\\path\\to\\app.exe" 或 "python.exe \"C:\\path\\to\\script.py\"")。
        enable (bool): True 为开启, False 为关闭。
    """
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        # 打开 Run 注册表键
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)

        if enable:
            # 设置注册表值
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
            print(f"为 '{app_name}' 启用开机自启动，命令: {command}")
        else:
            # 如果值存在则删除
            try:
                winreg.DeleteValue(key, app_name)
                print(f"为 '{app_name}' 禁用开机自启动。")
            except FileNotFoundError:
                # 值不存在，无需删除
                print(f"'{app_name}' 的开机自启动原本就已禁用。")

        winreg.CloseKey(key)
        return True

    except Exception as e:
        print(f"修改开机自启动注册表时出错: {e}")
        print("请确保您拥有必要的权限。")
        return False

def is_auto_start_enabled(app_name, command):
    """
    检查应用程序开机自启动是否已启用，并且注册表中的命令是否匹配预期。

    Args:
        app_name (str): 在注册表中使用的名称。
        command (str): 预期的注册表命令值。

    Returns:
        bool: 如果已启用且命令匹配，则返回 True，否则返回 False。
    """
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        # 打开 Run 注册表键
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)

        try:
            # 读取注册表值
            value, reg_type = winreg.QueryValueEx(key, app_name)
            # 检查值是否存在且与预期命令匹配
            is_enabled = (isinstance(value, str) and value == command and reg_type == winreg.REG_SZ)
            # print(f"Registry value for '{app_name}': '{value}' (Type: {reg_type}), Expected: '{command}'") # Debug print
            return is_enabled

        except FileNotFoundError:
            # 值不存在
            # print(f"Registry value for '{app_name}' not found.") # Debug print
            return False

        finally:
             winreg.CloseKey(key)

    except Exception as e:
        print(f"检查开机自启动注册表时出错: {e}")
        return False

# # Example usage (for testing the module directly) - 保持英文方便调试
# if __name__ == '__main__':
#     test_app_name = "MyTestAppForDDLTool"
#     if getattr(sys, 'frozen', False):
#         test_command = sys.executable
#     else:
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         project_dir = os.path.join(script_dir, os.pardir)
#         ddltool_script_path = os.path.join(project_dir, 'ddltool.py')
#         test_command = f'"{sys.executable}" "{os.path.abspath(ddltool_script_path)}"'
#
#     print(f"Checking auto-start for '{test_app_name}'...")
#     if is_auto_start_enabled(test_app_name, test_command):
#         print(f"Auto-start is currently ENABLED with command: {test_command}")
#         print("Disabling...")
#         set_auto_start(test_app_name, test_command, False)
#         if not is_auto_start_enabled(test_app_name, test_command):
#              print("Successfully disabled.")
#         else:
#              print("Failed to disable.")
#     else:
#         print(f"Auto-start is currently DISABLED or command mismatch. Expected: {test_command}")
#         print("Enabling...")
#         set_auto_start(test_app_name, test_command, True)
#         if is_auto_start_enabled(test_app_name, test_command):
#             print("Successfully enabled.")
#         else:
#             print("Failed to enable.")