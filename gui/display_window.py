import tkinter as tk
from tkinter import font as tkFont # 引入字体模块
from datetime import datetime, timedelta
import sys
import os
# 需要安装 ttkthemes: pip install ttkthemes
from ttkthemes import ThemedTk
# 引入 Tkinter Menu
from tkinter import Menu


class DisplayWindow(ThemedTk): # 现在 DisplayWindow 继承自 ThemedTk
    def __init__(self, ddl_items, settings, data_manager):
        # 从设置中获取主题，如果设置中没有，使用默认主题
        theme_name = settings.get('theme', 'arc') # 默认主题为 'arc'
        try:
            ThemedTk.__init__(self, theme=theme_name)
        except Exception as e:
            print(f"警告: 加载主题 '{theme_name}' 失败. 退回至 'clam'. 错误: {e}")
            ThemedTk.__init__(self, theme='clam') # 如果指定主题加载失败，回退到 'clam'
            settings['theme'] = 'clam' # Update settings, will be saved later

        self.ddl_items = ddl_items
        self.settings = settings
        self.data_manager = data_manager

        self.title("DDL 工具")

        # 设置窗口属性：无边框，置顶
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        # 窗口背景色将在 apply_settings 中设置

        # --- 窗口内容布局 ---
        # 使用 Frame 包含所有内容，方便管理背景色和绑定拖动事件
        self.main_frame = tk.Frame(self) # Initial background color set in apply_settings
        self.main_frame.pack(expand=True, fill="both")

        # 居中的标题 Label
        self.title_label = tk.Label(self.main_frame, text="项目截止日期") # Color, font set in apply_settings
        self.title_label.place(relx=0.5, rely=0, anchor='n') # Place at top center

        # 显示 DDL 列表的 Label
        self.ddl_list_label = tk.Label(self.main_frame, text="正在载入...", justify="left", anchor="nw") # Color, font set in apply_settings
        # Place below title, fill remaining space, leaving some padding
        # padx/pady added to place call for inner padding
        self.ddl_list_label.place(relx=0, rely=0, relwidth=1, relheight=1, y=25, bordermode='inside') # y=25 pushes it down

        # Apply initial settings (position, size, colors, font, alpha etc.)
        self.apply_settings(self.settings) # Frame and Labels are created now, safe to call

        # --- 窗口拖动功能 ---
        self._drag_x = 0
        self._drag_y = 0
        # Bind drag events to the main frame
        self.main_frame.bind("<ButtonPress-1>", self.start_drag)
        self.main_frame.bind("<B1-Motion>", self.do_drag)
        # Also bind to labels to make whole area draggable
        self.title_label.bind("<ButtonPress-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.do_drag)
        self.ddl_list_label.bind("<ButtonPress-1>", self.start_drag)
        self.ddl_list_label.bind("<B1-Motion>", self.do_drag)

        # --- 右键菜单 ---
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="设置...", command=self.open_settings)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="关闭", command=self.close_application)

        # Bind right-click event to show the menu
        self.bind("<Button-3>", self.show_context_menu)
        self.main_frame.bind("<Button-3>", self.show_context_menu)
        self.title_label.bind("<Button-3>", self.show_context_menu)
        self.ddl_list_label.bind("<Button-3>", self.show_context_menu)


        # Double-click event binding is handled in ddltool.py (bound to main_frame)
        # Single-click dummy binding to prevent issues
        self.bind("<Button-1>", lambda event: None)
        self.main_frame.bind("<Button-1>", lambda event: None)
        self.title_label.bind("<Button-1>", lambda event: None)
        self.ddl_list_label.bind("<Button-1>", lambda event: None)


        # 定时更新显示
        self.schedule_update()


    def open_settings(self):
        # This method is called by the context menu
        # Need to trigger the same logic as double click in ddltool.py
        # We can't directly call the function in ddltool.py from here.
        # A simple way is to define the handler in ddltool.py and pass it to DisplayWindow.
        # Or, define the logic here and call it from both double click and menu.
        # Let's keep the logic in ddltool.py and trigger it via a virtual event or a method call if we pass the function.
        # Or, let's just move the logic for opening settings here.

        # Trigger the double-click handler defined in ddltool.py by generating the event
        # This is a bit hacky, calling the function directly might be cleaner
        # Let's make open_settings_window in ddltool.py a standalone function and call it
        # Or pass the open_settings_window function as an argument to DisplayWindow.
        # Passing the function is cleaner. Let's assume ddltool.py passes open_settings_window as an argument.
        # (Need to update ddltool.py constructor call)

        # Correction: Let's assume the ddltool.py sets the double-click binding *after* creating DisplayWindow
        # The open_settings_window function in ddltool.py already has access to ddl_items, settings, data_manager.
        # We just need a way for DisplayWindow to call it.
        # We can pass the function reference during initialization.

        # For simplicity FOR NOW, let's assume open_settings_window is accessible globally or passed.
        # A better way is to pass a callback function during init.
        # Assuming open_settings_window from ddltool.py is accessible
        # self.master.open_settings_window(self, self.ddl_items, self.settings, self.data_manager)
        # Or even simpler, let the context menu item call a method in ddltool.py via the parent reference if possible.
        # The open_settings_window is local to main() in ddltool.py.
        # Let's make open_settings a method of DisplayWindow that the context menu calls,
        # and this method will internally call the open_settings_window function passed from ddltool.py.

        # Re-architecting: Let's add a callback for opening settings to DisplayWindow.__init__
        # For now, let's try calling the function defined in ddltool.py assuming it's somehow accessible
        # This is not clean. Let's pass the function reference.

        # Okay, let's assume ddltool.py passes the open_settings_window function reference
        # Update __init__ signature and call below:
        # DisplayWindow(ddl_items, settings, data_manager, open_settings_callback)
        # self.open_settings_callback = open_settings_callback
        # self.open_settings_callback(self, self.ddl_items, self.settings, self.data_manager)

        # Simpler approach: The settings window itself takes parent, ddl_items, settings, data_manager.
        # DisplayWindow doesn't need to know the internal details of open_settings_window.
        # It just needs to trigger the creation of a SettingsWindow.
        # Let's create the SettingsWindow directly here.
        # Ensure only one settings window is open.
        if not hasattr(self, '_settings_win') or not tk.Toplevel.winfo_exists(self._settings_win):
             # Get current settings (especially geo) to pass to the settings window
             current_display_settings = self.get_current_settings()
             self.settings.update(current_display_settings) # Update the settings dict reference

             self._settings_win = SettingsWindow(self, self.ddl_items, self.settings, self.data_manager)
             # Make settings window modal relative to display window
             self._settings_win.transient(self)
             self._settings_win.grab_set()
             self.wait_window(self._settings_win) # Wait here until settings window is destroyed

             # After settings window closes, settings and ddl_items are updated in memory.
             # SettingsWindow's Save/Apply should have called self.apply_settings() and self.update_display().
             # But let's ensure display is updated after wait_window returns anyway.
             self.update_display()
             # And apply settings again, especially geometry and theme if they were changed via Save
             self.apply_settings(self.settings) # Use the potentially updated settings


        else:
             # If settings window already exists, bring it to front
             self._settings_win.lift()
             self._settings_win.focus_force()


    def close_application(self):
        # This method is called by the context menu's "关闭" command
        # Trigger the window closing protocol to ensure data is saved
        self.protocol("WM_DELETE_WINDOW", self.close_application) # Re-bind to itself if needed, though WM_DELETE_WINDOW is usually sufficient
        self.destroy() # This will trigger the WM_DELETE_WINDOW protocol handler (on_closing in ddltool.py)


    def show_context_menu(self, event):
        # Display the context menu at the mouse position
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Make sure to close the menu if the user clicks elsewhere
            self.context_menu.grab_release()


    def _update_label_font(self):
        # 根据设置创建并应用字体
        font_family = self.settings.get('font_family', 'Arial') # 默认字体
        font_size = self.settings.get('font_size', 10) # 默认大小
        font_weight = self.settings.get('font_weight', 'normal') # 默认粗细

        try:
             # Check if font exists or is available
             app_font = tkFont.Font(family=font_family, size=font_size, weight=font_weight)
             self.title_label.config(font=app_font)
             self.ddl_list_label.config(font=app_font)
        except tkFont.TclError as e:
             print(f"警告: 应用字体 '{font_family}' 大小 {font_size} 粗细 {font_weight} 失败. 错误: {e}. 使用默认字体.")
             # Apply default font
             default_font = tkFont.Font(family='Arial', size=10, weight='normal')
             self.title_label.config(font=default_font)
             self.ddl_list_label.config(font=default_font)
             # Optionally update settings with defaults or notify user


    def start_drag(self, event):
        # Record mouse position relative to window corner
        widget = event.widget
        self._drag_x = event.x + widget.winfo_rootx() - self.winfo_rootx()
        self._drag_y = event.y + widget.winfo_rooty() - self.winfo_rooty()


    def do_drag(self, event):
        # Calculate new window position
        new_x = event.x_root - self._drag_x
        new_y = event.y_root - self._drag_y

        self.geometry(f"+{new_x}+{new_y}") # Change position only


    def apply_settings(self, settings):
         # Apply settings received from settings window or loaded from file
         self.settings = settings # Update internal settings reference

         # Apply window size and position
         win_width = self.settings.get('window_width', self.winfo_width())
         win_height = self.settings.get('window_height', self.winfo_height())
         win_x = self.settings.get('window_x', self.winfo_x())
         win_y = self.settings.get('window_y', self.winfo_y())

         try:
             # Ensure values are integers and size is positive
             win_width = max(int(win_width), 1) # Minimum size 1 pixel
             win_height = max(int(win_height), 1)

             # Estimate minimum height needed for title + padding
             # You might need to calculate this dynamically based on font size
             min_content_height = 25 # Approximation for title height + padding
             if win_height < min_content_height:
                  win_height = min_content_height

             self.geometry(f"{win_width}x{win_height}+{int(win_x)}+{int(win_y)}")
         except Exception as e:
              print(f"应用窗口几何设置失败: {e}")
              # Fallback or error handling

         # Apply color settings
         bg_color = self.settings.get('bg_color', 'black')
         fg_color = self.settings.get('fg_color', 'white')
         # Validate colors? Tkinter handles many formats.
         self.config(bg=bg_color) # Window background
         self.main_frame.config(bg=bg_color) # Frame background
         self.title_label.config(bg=bg_color, fg=fg_color) # Label colors
         self.ddl_list_label.config(bg=bg_color, fg=fg_color) # Label colors

         # Apply font settings
         self._update_label_font()

         # Apply transparency setting
         alpha = self.settings.get('alpha', 1.0) # Default opaque
         try:
             alpha = max(0.0, min(1.0, float(alpha))) # Clamp alpha between 0.0 and 1.0
             self.attributes('-alpha', alpha)
         except Exception as e:
              print(f"应用透明度设置失败: {e}")

         # Theme is applied in __init__ or explicitly via set_theme call from settings_window


    def get_current_settings(self):
        # Get actual current window position and size, and other settings for saving
        current_settings = self.settings.copy() # Copy current settings

        # Get current actual window dimensions and position
        try:
             current_settings['window_width'] = self.winfo_width()
             current_settings['window_height'] = self.winfo_height()
             current_settings['window_x'] = self.winfo_x()
             current_settings['window_y'] = self.winfo_y()
        except Exception as e:
             print(f"获取当前窗口几何信息失败: {e}")
             # Use values from self.settings if unable to get current winfo


        # Other settings (color, font, alpha, auto_start, theme etc.) are already in self.settings dict
        # auto_start is managed by settings_window, assume it's correct in self.settings when settings_window is open


        return current_settings


    def update_display(self):
        # Calculate and format the text to be displayed
        now = datetime.now()
        display_items_text = "" # Text for the DDL list label

        if isinstance(self.ddl_items, list):
            valid_ddls = []
            invalid_ddls_text = ""
            for item in self.ddl_items:
                 item_name = item.get('name', '未命名项目')
                 item_date_str = item.get('date')

                 if not item_date_str:
                     invalid_ddls_text += f"- {item_name}: 未设置日期\n"
                     continue

                 try:
                     ddl_time = datetime.strptime(item_date_str, '%Y-%m-%d %H:%M')
                     valid_ddls.append((item_name, ddl_time))
                 except ValueError:
                     invalid_ddls_text += f"- {item_name}: 无效日期格式 '{item_date_str}'\n"
                 except Exception as e:
                     invalid_ddls_text += f"- {item_name}: 处理日期出错 ({e})\n"


            # Sort valid items by due date
            sorted_ddls = sorted(valid_ddls, key=lambda x: x[1])

            for item_name, ddl_time in sorted_ddls:
                time_diff: timedelta = ddl_time - now

                # Format due date (YYYY-MM-DD HH:MM or MM-DD HH:MM if same year)
                current_year = now.year
                ddl_year = ddl_time.year

                if current_year != ddl_year:
                    ddl_date_formatted = ddl_time.strftime('%Y-%m-%d %H:%M')
                else:
                    ddl_date_formatted = ddl_time.strftime('%m-%d %H:%M')


                # Format time left
                if time_diff.total_seconds() < 0:
                    # Overdue
                    total_seconds_overdue = abs(time_diff.total_seconds())
                    days_overdue = int(total_seconds_overdue // (24 * 3600))
                    hours_overdue = int((total_seconds_overdue % (24 * 3600)) // 3600)
                    minutes_overdue = int((total_seconds_overdue % 3600) // 60)

                    time_left_str = ""
                    if days_overdue > 0:
                         time_left_str += f"已过期 {days_overdue}天 "
                         if hours_overdue > 0: time_left_str += f"{hours_overdue}小时"
                    elif hours_overdue > 0:
                         time_left_str += f"已过期 {hours_overdue}小时 "
                         if minutes_overdue > 0: time_left_str += f"{minutes_overdue}分钟"
                    elif minutes_overdue > 0:
                         time_left_str += f"已过期 {minutes_overdue}分钟"
                    elif total_seconds_overdue > 0:
                         time_left_str += "已过期不足1分钟"
                    else:
                         time_left_str = "已过期"


                    display_items_text += f"- {item_name} ({ddl_date_formatted}) : {time_left_str.strip()}\n"

                else:
                    # Not overdue
                    days = time_diff.days
                    seconds_rem = time_diff.seconds
                    hours, remainder = divmod(seconds_rem, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    time_str = ""
                    if days > 0:
                        time_str += f"{days}天"
                        if hours > 0:
                             time_str += f" {hours}小时"
                    elif hours > 0:
                        time_str += f"{hours}小时"
                        if minutes > 0:
                            time_str += f" {minutes}分钟"
                    elif minutes > 0:
                        time_str += f"{minutes}分钟"
                    elif seconds > 0:
                        time_str += f"不足1分钟"

                    if not time_str.strip():
                         time_str = "很快了！"

                    display_items_text += f"- {item_name} ({ddl_date_formatted}) : 剩余{time_str.strip()}\n"

            # Add invalid items information
            if invalid_ddls_text:
                 if display_items_text: # Add separator if there are valid items
                     display_items_text += "\n---\n"
                 display_items_text += invalid_ddls_text

        else:
            display_items_text += "错误：截止日期数据格式不正确。"

        self.ddl_list_label.config(text=display_items_text.strip()) # Update Label text

        # Schedule the next update in 60000 milliseconds (1 minute)
        self.after(60000, self.update_display)

    def schedule_update(self):
         # Initial delay, then start the update loop
         self.after(1000, self.update_display) # Delay 1 second for first update