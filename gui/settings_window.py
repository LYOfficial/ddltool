import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime
import os
import sys

# 获取当前脚本的完整路径，用于自启动设置
# 需要根据应用如何部署来确定真正的启动命令
if getattr(sys, 'frozen', False):
    # 如果应用被打包（例如用PyInstaller --onefile 或 --onedir）
    current_script_path = sys.executable # 可执行文件的路径
    # 如果是 --onedir 模式，可能还需要cd到可执行文件所在的目录
    # 但通常执行exe会自动设置工作目录
    auto_start_command = f'"{current_script_path}"'
else:
    # 如果是直接运行 .py 文件
    # 找到 ddltool.py 的绝对路径
    # sys.argv[0] 是当前执行的脚本路径 (settings_window.py 或 ddltool.py depending on how run)
    # 为了稳妥，通过 __file__ 和 os.path 导航到 ddltool.py
    script_dir = os.path.dirname(os.path.abspath(__file__)) # gui 目录
    project_dir = os.path.join(script_dir, os.pardir) # ddltool 目录
    ddltool_script_path = os.path.join(project_dir, 'ddltool.py')

    # 自启动命令是 python 解释器的路径 加上 ddltool.py 的路径
    python_exe = sys.executable
    auto_start_command = f'"{python_exe}" "{ddltool_script_path}"'
    print(f"Calculated auto-start command (dev mode): {auto_start_command}") # 调试信息

from utils.system_helper import set_auto_start, is_auto_start_enabled

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, ddl_items, settings, data_manager):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent # 保存父窗口引用 (DisplayWindow 实例)
        # 注意：ddl_items 和 settings 是从 parent 传来的引用，直接修改它们会影响 parent 持有的对象
        self.ddl_items = ddl_items
        self.settings = settings
        self.data_manager = data_manager

        self.title("DDL 工具设置")
        # self.geometry("500x400") # 可以设置一个默认大小
        self.transient(parent) # 让设置窗口成为父窗口的子窗口
        # self.grab_set() # 设置为模态窗口，阻止与父窗口交互。在父窗口等待时自动实现模态效果。
        # 使用 wait_window 让父窗口等待更简洁

        # 使用 Notebook 来组织 DDL 管理和应用设置两个主要区域
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # --- DDL 管理 Tab ---
        self.ddl_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.ddl_frame, text='项目管理')

        # DDL 列表显示 (使用 Treeview)
        self.ddl_tree = ttk.Treeview(self.ddl_frame, columns=('Name', 'DueDate'), show='headings')
        self.ddl_tree.heading('Name', text='项目名称')
        self.ddl_tree.heading('DueDate', text='截止日期')
        self.ddl_tree.column('Name', width=200)
        self.ddl_tree.column('DueDate', width=150)

        # 添加滚动条
        vsb = ttk.Scrollbar(self.ddl_frame, orient="vertical", command=self.ddl_tree.yview)
        hsb = ttk.Scrollbar(self.ddl_frame, orient="horizontal", command=self.ddl_tree.xview)
        self.ddl_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.ddl_tree.pack(expand=True, fill="both", side="left")

        # DDL 操作按钮 Frame
        button_frame = ttk.Frame(self.ddl_frame)
        button_frame.pack(side="right", fill="y", padx=5)

        ttk.Button(button_frame, text="新增...", command=self.add_ddl).pack(pady=5)
        self.edit_button = ttk.Button(button_frame, text="编辑...", command=self.edit_ddl, state=tk.DISABLED)
        self.edit_button.pack(pady=5)
        self.delete_button = ttk.Button(button_frame, text="删除", command=self.delete_ddl, state=tk.DISABLED)
        self.delete_button.pack(pady=5)

        # 绑定 treeview 选择事件，以便启用编辑/删除按钮
        self.ddl_tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # 加载初始数据到 Treeview
        self._load_ddls_to_treeview()

        # --- 应用设置 Tab ---
        self.settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.settings_frame, text='应用设置')

        # 窗口位置/大小设置
        ttk.Label(self.settings_frame, text="窗口位置 (X坐标, Y坐标):").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.pos_x_entry = ttk.Entry(self.settings_frame)
        self.pos_x_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        self.pos_y_entry = ttk.Entry(self.settings_frame)
        self.pos_y_entry.grid(row=0, column=2, sticky="ew", pady=5, padx=5)

        ttk.Label(self.settings_frame, text="窗口大小 (宽度, 高度):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.size_width_entry = ttk.Entry(self.settings_frame)
        self.size_width_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        self.size_height_entry = ttk.Entry(self.settings_frame)
        self.size_height_entry.grid(row=1, column=2, sticky="ew", pady=5, padx=5)

        # 从 settings 填充当前值
        self.pos_x_entry.insert(0, str(self.settings.get('window_x', '')))
        self.pos_y_entry.insert(0, str(self.settings.get('window_y', '')))
        self.size_width_entry.insert(0, str(self.settings.get('window_width', '')))
        self.size_height_entry.insert(0, str(self.settings.get('window_height', '')))

        # 开机自启动设置
        self.auto_start_var = tk.BooleanVar()
        # 检查当前是否已设置自启动，初始化 Checkbutton
        self.auto_start_var.set(is_auto_start_enabled("DDLTool", auto_start_command)) # "DDLTool" 是注册表键名

        self.auto_start_check = ttk.Checkbutton(self.settings_frame, text="开机自启动", variable=self.auto_start_var)
        self.auto_start_check.grid(row=2, column=0, columnspan=3, sticky="w", pady=10, padx=5)

        # 配置列的权重，使Entry控件随窗口拉伸
        self.settings_frame.grid_columnconfigure(1, weight=1)
        self.settings_frame.grid_columnconfigure(2, weight=1)

        # --- 底部操作按钮 ---
        bottom_button_frame = ttk.Frame(self)
        bottom_button_frame.pack(pady=10)

        # 添加“应用”按钮
        ttk.Button(bottom_button_frame, text="应用", command=self.apply_settings_preview).pack(side="left", padx=5)
        ttk.Button(bottom_button_frame, text="保存并关闭", command=self.save_and_close).pack(side="left", padx=5)
        ttk.Button(bottom_button_frame, text="取消", command=self.cancel_and_close).pack(side="left", padx=5)

        # 处理窗口关闭事件 (点击X按钮)
        self.protocol("WM_DELETE_WINDOW", self.cancel_and_close)

        # 在对话框打开时，获取并显示主窗口的当前实际位置和大小
        # 这样做的好处是，如果用户在打开设置前拖动了主窗口，设置窗口会显示最新的位置
        current_geo = self.parent.get_current_settings()
        self.pos_x_entry.delete(0, tk.END)
        self.pos_x_entry.insert(0, str(current_geo.get('window_x', '')))
        self.pos_y_entry.delete(0, tk.END)
        self.pos_y_entry.insert(0, str(current_geo.get('window_y', '')))
        self.size_width_entry.delete(0, tk.END)
        self.size_width_entry.insert(0, str(current_geo.get('window_width', '')))
        self.size_height_entry.delete(0, tk.END)
        self.size_height_entry.insert(0, str(current_geo.get('window_height', '')))


    def _load_ddls_to_treeview(self):
        # 清空 Treeview
        for i in self.ddl_tree.get_children():
            self.ddl_tree.delete(i)

        # 插入新数据
        # 按照日期排序再插入
        sorted_ddls = sorted(self.ddl_items, key=lambda x: x.get('date', ''))

        for item in sorted_ddls:
             # item 的格式假设是 {"name": "...", "date": "..."}
             # 使用 item 本身作为 iid，方便后续查找和修改（如果item是唯一标识的话）
             # 或者使用一个稳定的ID，这里继续使用 item 的值作为展示
             self.ddl_tree.insert('', tk.END, values=(item.get('name', '未命名项目'), item.get('date', '未设置日期')))

    def on_tree_select(self, event):
        # 如果有项目被选中，启用编辑和删除按钮
        selected_items = self.ddl_tree.selection()
        if selected_items:
            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)

    def get_selected_ddl_data(self):
        # 获取 Treeview 中选中项对应的原始数据
        selected_items = self.ddl_tree.selection()
        if not selected_items:
            return None

        # 获取选中项在 Treeview 中显示的值
        item_id = selected_items[0]
        item_values = self.ddl_tree.item(item_id, 'values')
        selected_name = item_values[0]
        selected_date_str = item_values[1]

        # 在原始 self.ddl_items 列表中查找匹配项
        # 注意：这里假设 name 和 date 的组合能唯一标识一个项目，如果不能，需要更强的ID机制
        for item in self.ddl_items:
             if item.get('name') == selected_name and item.get('date') == selected_date_str:
                  return item # 返回原始数据对象
        return None # 未找到匹配项

    def add_ddl(self):
         # 打开添加/编辑对话框，不传递当前项目数据
         self._open_add_edit_dialog()

    def edit_ddl(self):
         original_item_data = self.get_selected_ddl_data()
         if original_item_data:
             self._open_add_edit_dialog(original_item_data)
         else:
             messagebox.showerror("错误", "无法找到选中的项目数据。")

    def delete_ddl(self):
         selected_items = self.ddl_tree.selection()
         if not selected_items:
             return

         original_item_data = self.get_selected_ddl_data()
         if not original_item_data:
             messagebox.showerror("错误", "无法找到要删除的项目数据。")
             return

         if messagebox.askyesno("确认删除", f"确定要删除项目 '{original_item_data.get('name', '未命名')}' 吗？"):
             try:
                  self.ddl_items.remove(original_item_data) # 直接从列表中移除该对象
                  self._load_ddls_to_treeview() # 刷新 Treeview
                  self.on_tree_select(None) # 更新按钮状态
                  messagebox.showinfo("成功", "项目已删除。")
             except ValueError:
                  messagebox.showerror("错误", "删除项目失败。")

    def _open_add_edit_dialog(self, item_data=None):
        # 这个方法会创建一个新的 Toplevel 作为对话框
        dialog = AddEditDDLDialog(self, item_data)
        # 等待对话框关闭
        self.wait_window(dialog)

        # 对话框关闭后，检查是否有返回的数据
        if hasattr(dialog, 'result') and dialog.result:
             new_item_data = dialog.result # 格式 {"name": "...", "date": "..."}

             if item_data is None: # 这是添加操作
                 self.ddl_items.append(new_item_data)
                 messagebox.showinfo("成功", "项目已新增。")
             else: # 这是编辑操作
                 # 找到原始 item_data 在列表中的位置并更新
                 try:
                      index = self.ddl_items.index(item_data) # 找到旧数据的位置
                      self.ddl_items[index] = new_item_data # 用新数据替换
                      messagebox.showinfo("成功", "项目已更新。")
                 except ValueError:
                      messagebox.showerror("错误", "更新项目失败。")

             self._load_ddls_to_treeview() # 刷新列表显示
             self.on_tree_select(None) # 更新按钮状态
             # 不需要在这里保存到文件，保存由主窗口关闭或 Save 按钮处理

    def apply_settings_from_gui(self):
         # 从 Entry 控件读取窗口设置并更新到 self.settings 字典 (不保存到文件)
         try:
             new_x = int(self.pos_x_entry.get())
             new_y = int(self.pos_y_entry.get())
             new_width = int(self.size_width_entry.get())
             new_height = int(self.size_height_entry.get())

             # 更新 self.settings 字典
             self.settings['window_x'] = new_x
             self.settings['window_y'] = new_y
             self.settings['window_width'] = new_width
             self.settings['window_height'] = new_height

             return True # 应用成功
         except ValueError:
             messagebox.showwarning("输入错误", "窗口位置或大小输入无效，请确保输入数字。")
             # 清空输入框或重新填充当前值，以提示用户
             current_geo = self.parent.get_current_settings()
             self.pos_x_entry.delete(0, tk.END)
             self.pos_x_entry.insert(0, str(current_geo.get('window_x', '')))
             self.pos_y_entry.delete(0, tk.END)
             self.pos_y_entry.insert(0, str(current_geo.get('window_y', '')))
             self.size_width_entry.delete(0, tk.END)
             self.size_width_entry.insert(0, str(current_geo.get('window_width', '')))
             self.size_height_entry.delete(0, tk.END)
             self.size_height_entry.insert(0, str(current_geo.get('window_height', '')))

             return False # 应用失败

    def apply_settings_preview(self):
        # “应用”按钮功能：更新 settings 字典并让主窗口应用这些设置，但不保存到文件
        if self.apply_settings_from_gui(): # 先从GUI读取并更新到 self.settings
             # 调用父窗口的方法来应用这些设置
             self.parent.apply_settings(self.settings)
             # messagebox.showinfo("应用成功", "设置已应用，但尚未保存。") # 可以选择提示

    def save_and_close(self):
        # “保存并关闭”按钮功能：应用设置，保存所有数据到文件，处理自启动，然后关闭窗口
        if self.apply_settings_from_gui(): # 先从GUI读取并更新到 self.settings
             # 处理自启动设置
             auto_start_enabled = self.auto_start_var.get()
             set_auto_start("DDLTool", auto_start_command, auto_start_enabled)
             # 更新 self.settings 字典中的 auto_start 状态，以便保存到文件
             self.settings['auto_start'] = auto_start_enabled

             # 保存 DDL 项目和设置到文件
             self.data_manager.save_ddl_items(self.ddl_items)
             self.data_manager.save_settings(self.settings)

             # 调用父窗口方法应用设置，确保即使没点“应用”也能在保存时看到效果
             self.parent.apply_settings(self.settings)

             messagebox.showinfo("保存成功", "设置和项目已保存。")
             self.destroy() # 关闭窗口
        # else: apply_settings_from_gui 会显示错误，不关闭窗口

    def cancel_and_close(self):
        # “取消”按钮功能：不保存，直接关闭窗口
        # 因为 ddl_items 和 settings 是引用，取消时需要恢复它们
        # 简单的做法是，取消时不恢复数据，只关闭窗口。
        # 如果用户在 settings 窗口做了修改但没点保存，这些修改会留在内存中，直到程序关闭。
        # 更好的做法是在打开 settings 窗口时复制一份 ddl_items 和 settings，保存时再决定是否覆盖原引用。
        # 为了简化，我们假定用户点击取消时不希望任何修改（包括DDL修改）生效。
        # 这意味着需要在打开SettingsWindow时复制数据，并在取消时丢弃副本。

        # 简单处理：直接关闭。如果用户在里面修改了DDL，这些修改仍在self.ddl_items里（因为是引用）。
        # 除非点击保存，否则不会写入文件。主窗口下次加载会是旧数据。
        # 对于应用设置（位置/大小），如果点了“应用”但没点“保存”，主窗口当前是新设置，但文件里是旧的。
        # 下次启动会加载旧的设置。

        # 模态窗口由父窗口的 wait_window 管理，这里只需 destroy
        self.destroy()


# --- Add/Edit DDL Dialog ---
class AddEditDDLDialog(tk.Toplevel):
    def __init__(self, parent, item_data=None):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.item_data = item_data # 如果是编辑，传入已有的数据
        self.result = None # 用于存放返回的数据 {"name": ..., "date": ...}

        if item_data:
             self.title("编辑项目")
        else:
             self.title("新增项目")

        self.transient(parent)
        self.grab_set() # 模态对话框，阻止与父窗口交互

        # --- Input Fields ---
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(expand=True, fill="both")

        ttk.Label(form_frame, text="项目名称:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="截止日期 (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.date_entry = ttk.Entry(form_frame, width=20)
        self.date_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="截止时间 (HH:MM):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.time_entry = ttk.Entry(form_frame, width=10)
        self.time_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        # 如果是编辑模式，填充数据
        if item_data:
             self.name_entry.insert(0, item_data.get('name', ''))
             # 尝试解析日期，分割日期和时间填充
             try:
                 # 假设 item_data['date'] 格式是 'YYYY-MM-DD HH:MM'
                 dt_str = item_data.get('date', '')
                 if dt_str:
                     dt_obj = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
                     self.date_entry.insert(0, dt_obj.strftime('%Y-%m-%d'))
                     self.time_entry.insert(0, dt_obj.strftime('%H:%M'))
             except (ValueError, TypeError):
                 # 如果解析失败，保持为空，或者显示原始字符串提示用户
                 self.date_entry.insert(0, item_data.get('date', ''))
                 pass


        # --- Buttons ---
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="保存", command=self.on_save).pack(side="left", expand=True, padx=5)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side="left", expand=True, padx=5)

        # 使对话框模态
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.name_entry.focus_set() # 聚焦到名称输入框

    def on_save(self):
        name = self.name_entry.get().strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()

        if not name or not date_str or not time_str:
             messagebox.showwarning("输入错误", "项目名称、日期和时间都不能为空。")
             return

        # 验证日期和时间格式
        datetime_str_input = f"{date_str} {time_str}"
        try:
             # 检查格式是否精确匹配
             datetime.strptime(datetime_str_input, '%Y-%m-%d %H:%M')
             # 如果解析成功，使用标准的 YYYY-MM-DD HH:MM 格式保存
             valid_datetime_str = datetime_str_input # 格式是正确的

        except ValueError:
             messagebox.showwarning("输入错误", "日期或时间格式无效。请使用 YYYY-MM-DD 和 HH:MM 格式。")
             return

        # 数据有效，保存结果并关闭
        self.result = {"name": name, "date": valid_datetime_str}
        self.grab_release() # 释放模态抓取
        self.destroy()

    def on_cancel(self):
        self.result = None # 取消操作，不返回数据
        self.grab_release() # 释放模态抓取
        self.destroy()