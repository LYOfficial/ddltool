import tkinter as tk
import os
import sys
import json # 导入json

# 从我们自己写的模块导入
from gui.display_window import DisplayWindow # DisplayWindow 现在继承自 ThemedTk
from gui.settings_window import SettingsWindow
from utils.data_manager import DataManager
# system_helper 不在这里直接使用，由 settings_window 使用

def main():
    # 确定数据文件路径 - DataManager 会处理 PyInstaller 打包的情况
    data_manager = DataManager()

    # 加载初始数据和设置
    ddl_items = data_manager.load_ddl_items()
    settings = data_manager.load_settings()

    # 创建主应用窗口 (DisplayWindow 现在继承自 ThemedTk)
    # ddl_items 和 settings 作为引用传递，settings_window 将直接修改它们
    # DisplayWindow 会在初始化时读取 settings 中的主题并应用
    display_window = DisplayWindow(ddl_items, settings, data_manager)

    # 绑定双击事件打开设置窗口
    # 集中绑定到 main_frame，因为它覆盖了整个可点击区域
    if display_window.main_frame: # Ensure frame is created
        # Left double click to open settings
        display_window.main_frame.bind("<Double-1>", lambda event: open_settings_window(display_window, ddl_items, settings, data_manager))
        # Right click to show menu (handled inside DisplayWindow)
        # display_window.main_frame.bind("<Button-3>", lambda event: display_window.show_context_menu(event)) # Binding handled inside DisplayWindow

    else: # Fallback binding if main_frame creation failed or structure changed
        display_window.bind("<Double-1>", lambda event: open_settings_window(display_window, ddl_items, settings, data_manager))
        # Fallback for right click if main_frame is not available
        # display_window.bind("<Button-3>", lambda event: display_window.show_context_menu(event)) # Binding handled inside DisplayWindow


    # 处理窗口关闭事件 (点击窗口右上角的X按钮)
    def on_closing():
        # 在关闭前保存数据和设置
        # 从 display_window 获取当前的 settings (可能用户拖动改变了位置，应用了临时设置)
        current_settings = display_window.get_current_settings() # DisplayWindow 中添加此方法
        data_manager.save_settings(current_settings)
        # DDL items 在 settings_window 保存修改后就已经更新并保存了，这里可以再保存一次以防万一，
        # 或者依赖 settings_window 的保存。我们依赖 settings_window 的保存。
        # data_manager.save_ddl_items(ddl_items)

        display_window.destroy()

    display_window.protocol("WM_DELETE_WINDOW", on_closing)

    # 这是一个简单的打开设置窗口函数
    def open_settings_window(parent_window, ddl_items, settings, data_manager):
         # 确保同时只有一个设置窗口
         if not hasattr(open_settings_window, 'settings_win') or not tk.Toplevel.winfo_exists(open_settings_window.settings_win):
            # 在打开设置窗口前，从主窗口获取当前设置（特别是位置/大小）
            # 用户可能通过拖动改变了位置，这些改变需要同步到设置窗口的输入框
            current_display_settings = parent_window.get_current_settings()
            # 将当前设置合并到 settings 字典中，传递给 settings_window
            settings.update(current_display_settings) # 更新传递的 settings 字典

            # Create and show settings window
            open_settings_window.settings_win = SettingsWindow(parent_window, ddl_items, settings, data_manager)
            # Let parent window wait for settings window to close. This makes the settings window modal.
            # wait_window handles grab_set/grab_release automatically.
            parent_window.wait_window(open_settings_window.settings_win)
            # wait_window returns after settings window is closed.
            # Settings have been applied and saved by settings_window's Save/Apply logic.
            # DDL list changes are also in memory and saved.
            # Refresh main window display to show any DDL list changes.
            parent_window.update_display() # Refresh DDL list display
            # Apply settings again just in case (e.g., if theme changed, might need re-apply)
            # display_window.apply_settings(display_window.settings) # settings should already be updated by settings_window

         else:
             # 如果已存在，就把它提到最前面并给予焦点
             open_settings_window.settings_win.lift()
             open_settings_window.settings_win.focus_force()


    # 运行主循环
    display_window.mainloop()

if __name__ == "__main__":
    main()