import tkinter as tk
from datetime import datetime, timedelta
import sys # 导入sys用于检查打包状态
import os # 导入os用于获取路径

class DisplayWindow(tk.Tk): # 现在 DisplayWindow 继承自 tk.Tk
    def __init__(self, ddl_items, settings, data_manager):
        tk.Tk.__init__(self)

        self.ddl_items = ddl_items # 列表，每个元素是字典 {"name": "...", "date": "..."}
        self.settings = settings   # 字典
        self.data_manager = data_manager # 数据管理器实例

        self.title("DDL Tool") # 隐藏边框后看不到，但内部名字还在

        # 设置窗口属性：无边框，置顶
        self.overrideredirect(True)
        self.attributes('-topmost', True)

        # 设置初始位置和大小，从 settings 读取，提供一个更大的默认值
        default_width = 300 # 初始宽度大一些
        default_height = 150 # 初始高度大一些
        default_x = 100
        default_y = 50

        win_width = self.settings.get('window_width', default_width)
        win_height = self.settings.get('window_height', default_height)
        win_x = self.settings.get('window_x', default_x)
        win_y = self.settings.get('window_y', default_y)

        # Apply initial geometry and settings
        self.geometry(f"{win_width}x{win_height}+{win_x}+{win_y}")
        self.resizable(False, False) # 不可调整大小

        # 创建显示 Label，设置黑色背景和白色前景
        # justify="left" 文本左对齐
        # anchor="nw" 文本在 Label 内部靠西北（左上）对齐
        self.display_label = tk.Label(self, text="正在载入...", bg="black", fg="white", justify="left", anchor="nw", font=('Arial', 10)) # 设置一个默认字体大小
        self.display_label.pack(expand=True, fill="both")

        # 设置窗口本身的背景色，以防 Label 没有填满
        self.config(bg="black")

        # --- 窗口拖动功能 ---
        # 记录鼠标按下时的窗口内相对位置
        self._drag_x = 0
        self._drag_y = 0
        # 绑定鼠标左键按下事件 (ButtonPress-1) 到 start_drag 方法
        self.bind("<ButtonPress-1>", self.start_drag)
        # 绑定鼠标左键按住移动事件 (B1-Motion) 到 do_drag 方法
        self.bind("<B1-Motion>", self.do_drag)

        # 同时绑定到 Label，让整个窗口区域都可拖动
        self.display_label.bind("<ButtonPress-1>", self.start_drag)
        self.display_label.bind("<B1-Motion>", self.do_drag)

        # 绑定简单的左键单击事件，什么也不做，防止潜在的意外行为
        # 放在拖动绑定之后，如果只单击不拖动，会触发这个。如果单击并拖动，会触发 ButtonPress 和 B1-Motion。
        # 这个绑定理论上不是必须的，但可以用于调试或防止某些窗口管理器行为。
        # user reported issue might be related to focus, topmost, and overrideredirect interaction.
        # Let's add a simple handler that does nothing.
        self.bind("<Button-1>", lambda event: None)
        self.display_label.bind("<Button-1>", lambda event: None)


        # 双击事件绑定将在 ddltool.py 中完成

        # 定时更新显示
        self.schedule_update()

    def start_drag(self, event):
        # 记录鼠标在窗口控件内的相对位置
        self._drag_x = event.x
        self._drag_y = event.y

    def do_drag(self, event):
        # 计算窗口的新位置：鼠标当前屏幕绝对位置 - 鼠标在窗口内的相对位置
        # winfo_x() 和 winfo_y() 获取窗口左上角的屏幕坐标
        x = self.winfo_x() + event.x_root - (self.winfo_x() + self._drag_x) # simplified: x = event.x_root - self._drag_x
        y = self.winfo_y() + event.y_root - (self.winfo_y() + self._drag_y) # simplified: y = event.y_root - self._drag_y
        
        # 简单计算方式
        new_x = event.x_root - self._drag_x
        new_y = event.y_root - self._drag_y
        
        self.geometry(f"+{new_x}+{new_y}") # 只改变位置，不改变大小

        # 可以在拖动停止时（ButtonRelease-1）保存新位置，或者在应用关闭时统一保存
        # 考虑到频繁写入文件不好，我们在关闭时统一保存。
        # 但为了 SettingsWindow 能获取最新位置，我们可以在每次拖动时更新 settings 字典（注意，settings是引用）
        # self.settings['window_x'] = new_x # 不在这里频繁更新settings，而是在关闭或SettingsWindow打开时获取
        # self.settings['window_y'] = new_y

    def update_data_and_settings(self, ddl_items, settings):
         # This method might be called by ddltool.py after settings are saved
         self.ddl_items = ddl_items
         self.settings = settings
         # Note: apply_settings needs to be called separately if settings changed

    def apply_settings(self, settings):
         # 应用从 settings_window 传来的或从文件加载的设置
         self.settings = settings # 更新内部 settings 引用

         win_width = self.settings.get('window_width', self.winfo_width())
         win_height = self.settings.get('window_height', self.winfo_height())
         win_x = self.settings.get('window_x', self.winfo_x())
         win_y = self.settings.get('window_y', self.winfo_y())

         try:
             # 尝试应用新的 geometry
             self.geometry(f"{int(win_width)}x{int(win_height)}+{int(win_x)}+{int(win_y)}")
             # self.display_label.config(font=('Arial', self.settings.get('font_size', 10))) # 如果settings里有字体大小设置
         except Exception as e:
              print(f"Failed to apply window geometry settings: {e}")
              # 如果应用失败，可以回滚到旧值或默认值，并通知用户

         # 应用其他可能的设置，例如字体大小、颜色等（如果添加了这些设置的话）
         # self.display_label.config(bg=self.settings.get('bg_color', 'black'), fg=self.settings.get('fg_color', 'white'))

    def get_current_settings(self):
        # 获取当前窗口的实际位置和大小，用于保存
        current_geometry = self.geometry().split('+')
        current_settings = self.settings.copy() # 复制一份当前的设置

        if len(current_geometry) >= 1:
             size_str = current_geometry[0]
             try:
                 width, height = map(int, size_str.split('x'))
                 current_settings['window_width'] = width
                 current_settings['window_height'] = height
             except ValueError:
                 pass # Handle potential errors

        if len(current_geometry) >= 3:
             try:
                 pos_x = int(current_geometry[1])
                 pos_y = int(current_geometry[2])
                 current_settings['window_x'] = pos_x
                 current_settings['window_y'] = pos_y
             except ValueError:
                 pass # Handle potential errors

        # Auto-start setting is managed by settings_window, assume it's correct in self.settings
        # current_settings['auto_start'] = self.settings.get('auto_start', False) # No, this should come from settings_window or be read from registry

        return current_settings


    def update_display(self):
        # 计算并格式化要显示的文本
        now = datetime.now()
        display_text = "--- 项目截止日期 ---\n"

        # 确保 ddl_items 是列表，并且每个元素有 'name' 和 'date'
        if isinstance(self.ddl_items, list):
            # 过滤掉日期格式不正确的项目，或者标记出来
            valid_ddls = []
            invalid_ddls_text = ""
            for item in self.ddl_items:
                 item_name = item.get('name', '未命名项目')
                 item_date_str = item.get('date')

                 if not item_date_str:
                     invalid_ddls_text += f"- {item_name}: 未设置日期\n"
                     continue

                 try:
                     # 尝试解析日期时间，要求严格格式 'YYYY-MM-DD HH:MM'
                     ddl_time = datetime.strptime(item_date_str, '%Y-%m-%d %H:%M')
                     valid_ddls.append((item_name, ddl_time))
                 except ValueError:
                     invalid_ddls_text += f"- {item_name}: 无效日期格式 '{item_date_str}'\n"
                 except Exception as e:
                     invalid_ddls_text += f"- {item_name}: 处理日期出错 ({e})\n"


            # 按照截止日期排序有效的项目
            # 使用 lambda x: x[1] 按 datetime 对象排序
            sorted_ddls = sorted(valid_ddls, key=lambda x: x[1])

            for item_name, ddl_time in sorted_ddls:
                time_diff: timedelta = ddl_time - now

                if time_diff.total_seconds() < 0:
                    # 已过期
                    days = abs(time_diff.days)
                    seconds_abs = abs(time_diff.seconds) # Use seconds part only for hours/minutes within the last day
                    hours, remainder = divmod(seconds_abs, 3600)
                    # 如果过期超过一天，只显示天数和小时，分钟不那么重要
                    if days > 0:
                         display_text += f"- {item_name}: 已过期 {days}天 {hours}小时\n"
                    else: # 过期不足一天
                         minutes, seconds = divmod(remainder, 60)
                         display_text += f"- {item_name}: 已过期 {hours}小时 {minutes}分钟\n"
                else:
                    # 未过期
                    days = time_diff.days
                    seconds_rem = time_diff.seconds # Use seconds part for remaining time within the current day
                    hours, remainder = divmod(seconds_rem, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    time_str = ""
                    if days > 0:
                        time_str += f"{days}天"
                        # 如果天数大于0，通常只关心天和小时
                        if hours > 0:
                             time_str += f" {hours}小时"
                        time_str += " "
                    elif hours > 0: # 不足一天，但有小时
                        time_str += f"{hours}小时"
                        if minutes > 0:
                            time_str += f" {minutes}分钟"
                        time_str += " "
                    elif minutes > 0: # 不足一小时，但有分钟
                        time_str += f"{minutes}分钟 "
                    elif seconds > 0: # 不足一分钟
                        time_str += f"不足1分钟 "

                    if not time_str.strip(): # 如果时间差非常小 (比如毫秒级)
                         time_str = "很快了！ "

                    display_text += f"- {item_name}: 剩余{time_str.strip()}\n"

            # 添加无效项目信息
            display_text += invalid_ddls_text

        else:
            display_text += "错误：截止日期数据格式不正确。"

        self.display_label.config(text=display_text.strip()) # 更新Label文本

        # 每分钟再次安排更新 (60000毫秒)
        self.after(60000, self.update_display)

    def schedule_update(self):
         # 初始延迟一下，然后开始循环更新
         # 稍微延迟一秒开始，确保窗口显示后再更新内容
         self.after(1000, self.update_display)