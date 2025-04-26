import winreg
import sys
import os
# Need get_app_base_path from data_manager to find ddltool.py if not frozen
from utils.data_manager import get_app_base_path # Import the helper function

def get_auto_start_command():
    """
    Determines the command needed to start the application.
    This handles whether the application is run as a script or a PyInstaller executable.
    """
    if getattr(sys, 'frozen', False):
        # Running from a PyInstaller bundle. The command is just the executable path.
        return f'"{sys.executable}"'
    else:
        # Running from script. The command is the python executable + script path.
        # We need the path to ddltool.py, which is in the project root directory.
        app_base_path = get_app_base_path()
        ddltool_script_path = os.path.join(app_base_path, 'ddltool.py')
        return f'"{sys.executable}" "{ddltool_script_path}"'


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
        # Open the Run registry key for the current user
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)

        if enable:
            # Set the registry value (string type)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
            print(f"为 '{app_name}' 启用开机自启动，命令: {command}")
        else:
            # Try to delete the registry value if it exists
            try:
                winreg.DeleteValue(key, app_name)
                print(f"为 '{app_name}' 禁用开机自启动。")
            except FileNotFoundError:
                # The value doesn't exist, nothing to delete
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
        bool: If enabled and command matches, True, otherwise False.
    """
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        # Open the Run registry key for reading
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)

        try:
            # Read the registry value by name
            value, reg_type = winreg.QueryValueEx(key, app_name)
            # Check if the value exists, is a string, and matches the expected command
            is_enabled = (isinstance(value, str) and value == command and reg_type == winreg.REG_SZ)
            # print(f"Registry value for '{app_name}': '{value}' (Type: {reg_type}), Expected: '{command}'") # Debug print
            return is_enabled

        except FileNotFoundError:
            # The value does not exist in the registry
            # print(f"Registry value for '{app_name}' not found.") # Debug print
            return False

        finally:
             # Ensure the key is closed
             winreg.CloseKey(key)

    except Exception as e:
        print(f"检查开机自启动注册表时出错: {e}")
        # If there's an error opening the key, assume it's not enabled or check failed
        return False