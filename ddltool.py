import tkinter as tk
import os
import sys
import json # 导入json，虽然主要通过data_manager用

# 从我们自己写的模块导入
from gui.display_window import DisplayWindow
from gui.settings_window import SettingsWindow
from utils.data_manager import DataManager
# system_helper 不在这里直接使用，由 settings_window 使用

def main():
    # 确定数据文件路径
    # 将data文件夹放在用户AppData目录下更规范，这里简化放在脚本同级目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True) # 确保data文件夹存在
    ddl_file = os.path.join(data_dir, 'ddl_items.json')
    settings_file = os.path.join(data_dir, 'settings.json')

    # 初始化数据管理器
    data_manager = DataManager(ddl_file, settings_file)
    # 加载初始数据和设置
    ddl_items = data_manager.load_ddl_items()
    settings = data_manager.load_settings()

    # 创建主应用窗口 (DisplayWindow 现在继承自 tk.Tk)
    # ddl_items 和 settings 作为引用传递，settings_window 将直接修改它们
    display_window = DisplayWindow(ddl_items, settings, data_manager)

    # 绑定双击事件打开设置窗口
    # 事件绑定到 display_window 实例本身
    display_window.bind("<Double-1>", lambda event: open_settings_window(display_window, ddl_items, settings, data_manager))
    # 同时绑定到 display_window 内部的 label，确保点击 label 也能触发
    display_window.display_label.bind("<Double-1>", lambda event: open_settings_window(display_window, ddl_items, settings, data_manager))

    # 处理窗口关闭事件
    def on_closing():
        # 在关闭前保存数据和设置
        # 从 display_window 获取当前的 settings (可能用户拖动改变了位置)
        current_settings = display_window.get_current_settings() # DisplayWindow 中添加此方法
        data_manager.save_settings(current_settings)
        # DDL items 在 settings_window 保存修改后就已经更新并保存了，这里可以再保存一次以防万一，
        # 或者依赖 settings_window 的保存，取决于设计。我们依赖 settings_window 的保存。
        # data_manager.save_ddl_items(ddl_items) 

        display_window.destroy()

    display_window.protocol("WM_DELETE_WINDOW", on_closing)

    # 这是一个简单的打开设置窗口函数
    def open_settings_window(parent_window, ddl_items, settings, data_manager):
         # 确保同时只有一个设置窗口
         # 检查 settings_win 属性是否存在且窗口仍然存在
         if not hasattr(open_settings_window, 'settings_win') or not tk.Toplevel.winfo_exists(open_settings_window.settings_win):
            # 在打开设置窗口前，从主窗口获取当前设置（特别是位置/大小）
            current_display_settings = parent_window.get_current_settings()
            # 将当前设置合并到 settings 字典中，传递给设置窗口
            settings.update(current_display_settings)

            open_settings_window.settings_win = SettingsWindow(parent_window, ddl_items, settings, data_manager)
            # 设置窗口关闭后，settings 和 ddl_items 已经被修改（因为传递的是引用），
            # 并且 settings_window 的“保存”按钮会负责保存到文件。
            # 这里父窗口等待即可。
            parent_window.wait_window(open_settings_window.settings_win)
            # wait_window 返回后，表示设置窗口已关闭。
            # 此时 ddl_items 和 settings 已经被 settings_window 修改和保存过了。
            # DisplayWindow 需要根据修改后的 settings 更新自己的外观（如果用户点了应用或保存）。
            # SettingsWindow 的 Save/Apply 按钮会调用 DisplayWindow 的 apply_settings。
            # 所以这里不需要额外操作，除非你想确保任何情况下都刷新显示。
            # Let's ensure display updates after settings window closes, just in case
            parent_window.update_display() # 刷新 DDL 列表显示
            # geometry settings are applied directly by the settings window's "Apply" or "Save" button

         else:
             # 如果已存在，就把它提到最前面并给予焦点
             open_settings_window.settings_win.lift()
             open_settings_window.settings_win.focus_force()


    # 运行主循环
    display_window.mainloop()

if __name__ == "__main__":
    main()