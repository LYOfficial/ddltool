import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, colorchooser, font as tkFont
from datetime import datetime
import os
import sys

# Needs tkcalendar: pip install tkcalendar
from tkcalendar import DateEntry
# Needs ttkthemes: pip install ttkthemes
# from ttkthemes import ThemedTk # Not used directly here, used by parent

# Get the command for auto-start (handles script vs frozen mode)
from utils.system_helper import set_auto_start, is_auto_start_enabled, get_auto_start_command

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, ddl_items, settings, data_manager):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent # Save parent window reference (DisplayWindow instance)
        # Note: ddl_items and settings are references from parent, direct modifications
        # will affect parent's objects. This is intended for the "Apply" button.
        self.ddl_items = ddl_items
        self.settings = settings

        self.data_manager = data_manager

        self.title("DDL 工具设置")
        # self.geometry("500x400") # Can set a default size
        self.transient(parent) # Make settings window a child of parent window
        self.grab_set() # Make modal, blocks interaction with parent window
        self.resizable(False, False) # Make window not resizable

        # Use Notebook to organize DDL management and Application settings areas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # --- DDL Management Tab ---
        self.ddl_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.ddl_frame, text='项目管理')

        # DDL list display (using Treeview)
        self.ddl_tree = ttk.Treeview(self.ddl_frame, columns=('Name', 'DueDate'), show='headings')
        self.ddl_tree.heading('Name', text='项目名称')
        self.ddl_tree.heading('DueDate', text='截止日期')
        self.ddl_tree.column('Name', width=200, anchor='w') # Left aligned
        self.ddl_tree.column('DueDate', width=150, anchor='center') # Centered

        # Add scrollbars
        vsb = ttk.Scrollbar(self.ddl_frame, orient="vertical", command=self.ddl_tree.yview)
        hsb = ttk.Scrollbar(self.ddl_frame, orient="horizontal", command=self.ddl_tree.xview)
        self.ddl_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.ddl_tree.pack(expand=True, fill="both", side="left")

        # DDL operation buttons Frame
        button_frame = ttk.Frame(self.ddl_frame)
        button_frame.pack(side="right", fill="y", padx=5)

        ttk.Button(button_frame, text="新增...", command=self.add_ddl).pack(pady=5, fill="x")
        self.edit_button = ttk.Button(button_frame, text="编辑...", command=self.edit_ddl, state=tk.DISABLED)
        self.edit_button.pack(pady=5, fill="x")
        self.delete_button = ttk.Button(button_frame, text="删除", command=self.delete_ddl, state=tk.DISABLED)
        self.delete_button.pack(pady=5, fill="x")

        # Bind treeview selection event to enable edit/delete buttons
        self.ddl_tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Load initial data into Treeview
        self._load_ddls_to_treeview()

        # --- Application Settings Tab ---
        self.settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.settings_frame, text='外观设置')

        # Use grid layout for settings area
        row = 0

        # Window position/size settings
        ttk.Label(self.settings_frame, text="窗口位置 (X, Y):").grid(row=row, column=0, sticky="w", pady=2, padx=5)
        self.pos_x_entry = ttk.Entry(self.settings_frame)
        self.pos_x_entry.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        self.pos_y_entry = ttk.Entry(self.settings_frame)
        self.pos_y_entry.grid(row=row, column=2, sticky="ew", pady=2, padx=5)
        row += 1

        ttk.Label(self.settings_frame, text="窗口大小 (宽, 高):").grid(row=row, column=0, sticky="w", pady=2, padx=5)
        self.size_width_entry = ttk.Entry(self.settings_frame)
        self.size_width_entry.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        self.size_height_entry = ttk.Entry(self.settings_frame)
        self.size_height_entry.grid(row=row, column=2, sticky="ew", pady=2, padx=5)
        row += 1

        # Font settings
        ttk.Label(self.settings_frame, text="字体家族:").grid(row=row, column=0, sticky="w", pady=2, padx=5)
        # Provide a dropdown list to select system fonts
        available_fonts = sorted(tkFont.families())
        self.font_family_combo = ttk.Combobox(self.settings_frame, values=available_fonts, state='readonly')
        self.font_family_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2, padx=5)
        row += 1

        ttk.Label(self.settings_frame, text="字体大小:").grid(row=row, column=0, sticky="w", pady=2, padx=5)
        self.font_size_spinbox = ttk.Spinbox(self.settings_frame, from_=6, to=72, width=5)
        self.font_size_spinbox.grid(row=row, column=1, sticky="w", pady=2, padx=5)
        row += 1

        ttk.Label(self.settings_frame, text="字体粗细:").grid(row=row, column=0, sticky="w", pady=2, padx=5)
        self.font_weight_combo = ttk.Combobox(self.settings_frame, values=('normal', 'bold'), state='readonly', width=8)
        self.font_weight_combo.grid(row=row, column=1, sticky="w", pady=2, padx=5)
        row += 1

        # Font color and background color settings
        ttk.Label(self.settings_frame, text="字体颜色:").grid(row=row, column=0, sticky="w", pady=2, padx=5)
        self.fg_color_button = ttk.Button(self.settings_frame, text="选择颜色", command=self.choose_fg_color)
        self.fg_color_button.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        # Color preview Label
        self.fg_color_preview = tk.Label(self.settings_frame, text="■", width=2, relief="sunken")
        self.fg_color_preview.grid(row=row, column=2, sticky="w", pady=2, padx=5)
        row += 1

        ttk.Label(self.settings_frame, text="背景颜色:").grid(row=row, column=0, sticky="w", pady=2, padx=5)
        self.bg_color_button = ttk.Button(self.settings_frame, text="选择颜色", command=self.choose_bg_color)
        self.bg_color_button.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        # Color preview Label
        self.bg_color_preview = tk.Label(self.settings_frame, text="■", width=2, relief="sunken")
        self.bg_color_preview.grid(row=row, column=2, sticky="w", pady=2, padx=5)
        row += 1

        # Transparency setting
        ttk.Label(self.settings_frame, text="窗口透明度 (0.0-1.0):").grid(row=row, column=0, sticky="w", pady=2, padx=5)
        self.alpha_spinbox = ttk.Spinbox(self.settings_frame, from_=0.0, to=1.0, increment=0.05, width=5, format="%.2f")
        self.alpha_spinbox.grid(row=row, column=1, sticky="w", pady=2, padx=5)
        row += 1

        # Theme setting
        ttk.Label(self.settings_frame, text="主题:").grid(row=row, column=0, sticky="w", pady=2, padx=5)
        # Get available themes from the parent (ThemedTk instance)
        # Wrap in try-except in case ttkthemes is not fully functional or parent is not ThemedTk
        available_themes = []
        if hasattr(self.parent, 'get_themes'):
             try:
                  available_themes = sorted(self.parent.get_themes())
             except Exception as e:
                  print(f"Error getting themes from parent: {e}")
                  available_themes = ['clam', 'default'] # Provide basic fallbacks
        else:
             available_themes = ['clam', 'default'] # Provide basic fallbacks


        self.theme_combo = ttk.Combobox(self.settings_frame, values=available_themes, state='readonly')
        self.theme_combo.grid(row=row, column=1, columnspan=2, sticky="ew", pady=2, padx=5)
        row += 1


        # Auto-start setting
        self.auto_start_var = tk.BooleanVar()
        # Checkbutton variable is linked in _load_current_settings_to_gui
        self.auto_start_check = ttk.Checkbutton(self.settings_frame, text="开机自启动")
        self.auto_start_check.grid(row=row, column=0, columnspan=3, sticky="w", pady=10, padx=5)
        row += 1


        # Configure column weights to make Entry/Combobox widgets expand
        self.settings_frame.grid_columnconfigure(1, weight=1)
        self.settings_frame.grid_columnconfigure(2, weight=1)

        # --- Populate GUI with current settings ---
        self._load_current_settings_to_gui()

        # --- Bottom operation buttons ---
        bottom_button_frame = ttk.Frame(self)
        bottom_button_frame.pack(pady=10)

        # Add "Apply" button
        ttk.Button(bottom_button_frame, text="应用", command=self.apply_settings_preview).pack(side="left", padx=5)
        ttk.Button(bottom_button_frame, text="保存并关闭", command=self.save_and_close).pack(side="left", padx=5)
        ttk.Button(bottom_button_frame, text="取消", command=self.cancel_and_close).pack(side="left", padx=5)

        # Handle window closing event (clicking the X button)
        self.protocol("WM_DELETE_WINDOW", self.cancel_and_close)


    def _load_current_settings_to_gui(self):
        # Load settings from self.settings dictionary into GUI controls
        # Window position/size gets actual current values from parent window, others from settings dict
        current_geo = self.parent.get_current_settings() # Get actual current settings from main window

        self.pos_x_entry.delete(0, tk.END)
        self.pos_x_entry.insert(0, str(current_geo.get('window_x', '')))
        self.pos_y_entry.delete(0, tk.END)
        self.pos_y_entry.insert(0, str(current_geo.get('window_y', '')))
        self.size_width_entry.delete(0, tk.END)
        self.size_width_entry.insert(0, str(current_geo.get('window_width', '')))
        self.size_height_entry.delete(0, tk.END)
        self.size_height_entry.insert(0, str(current_geo.get('window_height', '')))

        # Font settings
        font_family = self.settings.get('font_family', 'Arial')
        if font_family in self.font_family_combo['values']:
             self.font_family_combo.set(font_family)
        else:
             # If saved font is not available, use default 'Arial' or the first available
             if 'Arial' in self.font_family_combo['values']:
                  self.font_family_combo.set('Arial')
             elif self.font_family_combo['values']:
                  self.font_family_combo.set(self.font_family_combo['values'][0])


        self.font_size_spinbox.set(self.settings.get('font_size', 10))

        font_weight = self.settings.get('font_weight', 'normal')
        if font_weight in self.font_weight_combo['values']:
             self.font_weight_combo.set(font_weight)
        else:
             self.font_weight_combo.set('normal')


        # Color settings
        fg_color = self.settings.get('fg_color', 'white')
        bg_color = self.settings.get('bg_color', 'black')
        # Validate color strings? Tkinter usually handles valid color names or #RRGGBB
        self.fg_color_preview.config(bg=fg_color)
        self.bg_color_preview.config(bg=bg_color)

        # Transparency
        self.alpha_spinbox.set(self.settings.get('alpha', 1.0))

        # Theme
        theme_name = self.settings.get('theme', 'arc')
        if theme_name in self.theme_combo['values']:
             self.theme_combo.set(theme_name)
        elif self.theme_combo['values']:
             self.theme_combo.set(self.theme_combo['values'][0]) # Fallback to first available theme
        else:
             self.theme_combo.set('') # No themes available?


        # Auto-start setting
        auto_start_cmd = get_auto_start_command() # Get the correct command for current execution mode
        self.auto_start_var.set(is_auto_start_enabled("DDLTool", auto_start_cmd))
        self.auto_start_check.config(variable=self.auto_start_var) # Associate variable with Checkbutton


    def _load_ddls_to_treeview(self):
        # Clear Treeview
        for i in self.ddl_tree.get_children():
            self.ddl_tree.delete(i)

        # Insert new data
        # Sort by date
        # Filter out items that are not dictionaries or missing keys before sorting
        valid_ddl_items = [item for item in self.ddl_items if isinstance(item, dict) and 'name' in item and 'date' in item]

        sorted_ddls = sorted(valid_ddl_items, key=lambda x: x.get('date', '')) # Use empty string as default key for missing dates

        for item in sorted_ddls:
             # item format: {"name": "...", "date": "..."}
             # Store the original item dictionary reference as the item's tag.
             # This makes it easy to retrieve the original data object for editing/deletion.
             self.ddl_tree.insert('', tk.END, values=(item.get('name', '未命名项目'), item.get('date', '未设置日期')), tags=(item,))


    def on_tree_select(self, event):
        # If an item is selected, enable edit and delete buttons
        selected_items = self.ddl_tree.selection()
        if selected_items:
            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)

    def get_selected_ddl_data(self):
        # Get the original data object for the selected item (using tag)
        selected_items = self.ddl_tree.selection()
        if not selected_items:
            return None

        item_id = selected_items[0]
        # Retrieve the tag, which is the original dictionary object
        # Check if tags exist and are not empty
        tags = self.ddl_tree.item(item_id, 'tags')
        if tags and tags[0]:
            return tags[0] # Return the stored object reference
        return None # No valid tag found


    def add_ddl(self):
         # Open add/edit dialog, without passing existing item data
         self._open_add_edit_dialog()

    def edit_ddl(self):
         original_item_data = self.get_selected_ddl_data()
         if original_item_data:
             self._open_add_edit_dialog(original_item_data)
         else:
             messagebox.showwarning("提示", "请先在列表中选择一个项目进行编辑。")

    def delete_ddl(self):
         selected_items = self.ddl_tree.selection()
         if not selected_items:
             messagebox.showwarning("提示", "请先在列表中选择一个项目进行删除。")
             return

         original_item_data = self.get_selected_ddl_data()
         if not original_item_data:
             messagebox.showerror("错误", "无法找到要删除的项目数据。") # Should not happen if get_selected_ddl_data works
             return

         if messagebox.askyesno("确认删除", f"确定要删除项目 '{original_item_data.get('name', '未命名')}' 吗？"):
             try:
                  # Find the exact object reference in the original list and remove it
                  # Using item_data reference directly assumes it's still in the list
                  self.ddl_items.remove(original_item_data) # Remove by object identity

                  self._load_ddls_to_treeview() # Refresh Treeview display
                  self.on_tree_select(None) # Update button states (disables Edit/Delete)
                  # messagebox.showinfo("成功", "项目已删除（需保存设置生效）。")
             except ValueError:
                  messagebox.showerror("错误", "删除项目失败：在数据列表中未找到匹配项。") # Indicates an issue with the item reference
             except Exception as e:
                  messagebox.showerror("错误", f"删除项目失败: {e}")

    def _open_add_edit_dialog(self, item_data=None):
        dialog = AddEditDDLDialog(self, item_data)
        # wait_window makes the dialog modal and blocks here until dialog is destroyed
        self.wait_window(dialog)

        # After dialog closes, check if result was set (Save button was clicked)
        if hasattr(dialog, 'result') and dialog.result:
             new_item_data = dialog.result # Format: {"name": "...", "date": "..."}

             if item_data is None: # This was an Add operation
                 self.ddl_items.append(new_item_data)
                 messagebox.showinfo("成功", "项目已新增（需保存设置生效）。")
             else: # This was an Edit operation
                 # Find the original item in the list by reference and update it
                 try:
                      # index() finds the position of the exact object reference
                      index = self.ddl_items.index(item_data)
                      self.ddl_items[index] = new_item_data # Replace old object with new data object
                      messagebox.showinfo("成功", "项目已更新（需保存设置生效）。")
                 except ValueError:
                      messagebox.showerror("错误", "更新项目失败：在数据列表中未找到原始项目。") # Indicates an issue with the item reference
                 except Exception as e:
                     messagebox.showerror("错误", f"更新项目失败: {e}")


             self._load_ddls_to_treeview() # Refresh Treeview display
             self.on_tree_select(None) # Update button states (disables Edit/Delete)


    def choose_fg_color(self):
        # Open color chooser, returns (RGB tuple, #HEX string)
        initial_color = self.fg_color_preview.cget('bg') # Get current color for initial display
        color_code = colorchooser.askcolor(color=initial_color, title="选择字体颜色")
        if color_code and color_code[1]: # If user selected a color and didn't cancel
            selected_color_hex = color_code[1]
            self.fg_color_preview.config(bg=selected_color_hex)

    def choose_bg_color(self):
        # Open color chooser, returns (RGB tuple, #HEX string)
        initial_color = self.bg_color_preview.cget('bg') # Get current color
        color_code = colorchooser.askcolor(color=initial_color, title="选择背景颜色")
        if color_code and color_code[1]: # If user selected a color and didn't cancel
            selected_color_hex = color_code[1]
            self.bg_color_preview.config(bg=selected_color_hex)


    def apply_settings_from_gui(self):
         # Read settings from GUI controls and update self.settings dictionary (does NOT save to file)
         updated_settings = self.settings.copy() # Create a copy to modify
         valid_input = True

         # Window position and size
         try:
             updated_settings['window_x'] = int(self.pos_x_entry.get())
             updated_settings['window_y'] = int(self.pos_y_entry.get())
             updated_settings['window_width'] = int(self.size_width_entry.get())
             updated_settings['window_height'] = int(self.size_height_entry.get())
             # Basic validation for size
             if updated_settings['window_width'] <= 0 or updated_settings['window_height'] <= 0:
                  messagebox.showwarning("输入错误", "窗口大小必须大于零。")
                  valid_input = False
         except ValueError:
             messagebox.showwarning("输入错误", "窗口位置或大小输入无效，请确保输入整数。")
             valid_input = False

         # Font settings
         selected_font_family = self.font_family_combo.get()
         if selected_font_family: # Ensure a font is selected
             updated_settings['font_family'] = selected_font_family
         else:
             messagebox.showwarning("输入错误", "请选择一个字体家族。")
             valid_input = False

         selected_font_weight = self.font_weight_combo.get()
         if selected_font_weight in ('normal', 'bold'): # Explicitly check valid weights
             updated_settings['font_weight'] = selected_font_weight
         else:
              messagebox.showwarning("输入错误", "请选择字体粗细 (normal 或 bold)。")
              valid_input = False

         try:
             font_size = int(self.font_size_spinbox.get())
             if font_size > 0:
                  updated_settings['font_size'] = font_size
             else:
                 messagebox.showwarning("输入错误", "字体大小必须大于零。")
                 valid_input = False
         except ValueError:
              messagebox.showwarning("输入错误", "字体大小输入无效，请确保输入整数。")
              valid_input = False


         # Color settings (read from the background color of the preview Labels)
         updated_settings['fg_color'] = self.fg_color_preview.cget('bg')
         updated_settings['bg_color'] = self.bg_color_preview.cget('bg')

         # Transparency setting
         try:
             alpha_value = float(self.alpha_spinbox.get())
             if 0.0 <= alpha_value <= 1.0:
                 updated_settings['alpha'] = alpha_value
             else:
                 messagebox.showwarning("输入错误", "透明度必须在 0.0 到 1.0 之间。")
                 valid_input = False
         except ValueError:
              messagebox.showwarning("输入错误", "透明度输入无效，请确保输入数字。")
              valid_input = False

         # Theme setting
         selected_theme = self.theme_combo.get()
         if selected_theme and selected_theme in self.theme_combo['values']:
             updated_settings['theme'] = selected_theme
         else:
              messagebox.showwarning("输入错误", "请选择一个有效的主题。")
              valid_input = False


         if valid_input:
             # If all inputs are valid, update the self.settings dictionary with the new values
             self.settings.update(updated_settings)
             return True # Applied settings successfully
         else:
              # If validation failed, revert GUI inputs to current self.settings values (before invalid input)
              self._load_current_settings_to_gui() # Revert GUI to current self.settings state
              return False # Failed to apply settings due to invalid input


    def apply_settings_preview(self):
        # "Apply" button function: updates settings dict and makes the parent window apply them, but does NOT save to file
        if self.apply_settings_from_gui(): # First, read from GUI and update self.settings
             # Call parent window methods to apply these settings
             # Set theme first as it might affect how other settings are applied
             try:
                  # Assuming parent has a set_theme method from ThemedTk
                  self.parent.set_theme(self.settings.get('theme', 'arc'))
             except Exception as e:
                  print(f"Warning: Failed to apply theme '{self.settings.get('theme', 'arc')}' in preview: {e}")
                  # Fallback if theme application fails
                  try:
                       self.parent.set_theme('clam')
                       self.settings['theme'] = 'clam' # Update settings to reflect fallback
                       messagebox.showwarning("主题错误", "选定的主题加载失败，已应用默认主题。")
                       self._load_current_settings_to_gui() # Refresh GUI with fallback theme
                  except Exception as e2:
                       print(f"Warning: Fallback theme 'clam' also failed: {e2}")
                       messagebox.showwarning("主题错误", "无法加载任何主题。")


             self.parent.apply_settings(self.settings) # Apply other settings (geometry, color, font, alpha)
             # messagebox.showinfo("应用成功", "设置已应用，但尚未保存。") # Can optionally show a message

    def save_and_close(self):
        # "Save and Close" button function: apply settings, save all data to files, handle auto-start, then close window
        if self.apply_settings_from_gui(): # First, read from GUI and update self.settings
             # Process auto-start setting
             auto_start_enabled = self.auto_start_var.get()
             current_auto_start_command = get_auto_start_command() # Get the correct command for current execution mode
             set_auto_start("DDLTool", current_auto_start_command, auto_start_enabled)
             # Update the auto_start state in self.settings dictionary to be saved
             self.settings['auto_start'] = auto_start_enabled


             # Save DDL items and settings to files
             self.data_manager.save_ddl_items(self.ddl_items)
             self.data_manager.save_settings(self.settings)

             # Call parent window methods to apply settings one last time before closing
             # Set theme first
             try:
                  self.parent.set_theme(self.settings.get('theme', 'arc'))
             except Exception as e:
                  print(f"Warning: Failed to apply theme '{self.settings.get('theme', 'arc')}' on save: {e}")
                  try: self.parent.set_theme('clam')
                  except: pass # Ignore if even fallback fails


             self.parent.apply_settings(self.settings)

             messagebox.showinfo("保存成功", "设置和项目已保存。")
             self.destroy() # Close the window
        # else: apply_settings_from_gui will show error, window stays open

    def cancel_and_close(self):
        # "Cancel" button function: does NOT save to files, just closes the window
        # Changes made to ddl_items and settings (which are references) will persist in the parent's objects in memory.
        # Only the *file* save is skipped.
        # Applied settings preview will remain visible in the main window until application restart.
        self.grab_release() # Release modal grab
        self.destroy()


# --- Add/Edit DDL Dialog ---
class AddEditDDLDialog(tk.Toplevel):
    def __init__(self, parent, item_data=None):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.item_data = item_data # If editing, pass existing data
        self.result = None # Used to store the result {"name": ..., "date": ...}

        if item_data:
             self.title("编辑项目")
        else:
             self.title("新增项目")

        self.transient(parent)
        self.grab_set() # Modal dialog
        self.resizable(False, False) # Dialog not resizable
        self.attributes('-topmost', True) # <--- FIX: Force this dialog to stay on top

        # --- Input Fields ---
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(expand=True, fill="both")

        # 项目名称
        ttk.Label(form_frame, text="项目名称:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5, padx=5)

        # 截止日期 (使用 tkcalendar 的 DateEntry)
        ttk.Label(form_frame, text="截止日期:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        # locale='zh_CN' If system supports Chinese locale, might show Chinese calendar
        # date_pattern ensures saved string format is correct
        self.date_entry = DateEntry(form_frame, selectmode='day', date_pattern='yyyy-mm-dd', locale='zh_CN', font='Arial 10')
        self.date_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=5, padx=5)

        # 截止时间 (使用 Spinbox 选择小时和分钟)
        ttk.Label(form_frame, text="截止时间:").grid(row=2, column=0, sticky="w", pady=5, padx=5)

        time_frame = ttk.Frame(form_frame) # Use a Frame to contain hour and minute spinboxes
        time_frame.grid(row=2, column=1, columnspan=2, sticky="w", pady=5, padx=5)

        # Use values for fixed selection, or from_/to_/increment for range
        # format="%02.0f" ensures two digits with leading zero
        self.hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, width=3, format="%02.0f", wrap=True) # wrap=True cycles at max/min
        self.hour_spinbox.pack(side="left")
        ttk.Label(time_frame, text=":").pack(side="left") # Separator
        self.minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, width=3, format="%02.0f", wrap=True)
        self.minute_spinbox.pack(side="left")

        # If editing mode, populate fields with existing data
        if item_data:
             self.name_entry.insert(0, item_data.get('name', ''))
             # Attempt to parse datetime string and populate DateEntry and Spinboxes
             try:
                 dt_str = item_data.get('date', '')
                 if dt_str:
                     dt_obj = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
                     # Populate DateEntry
                     self.date_entry.set_date(dt_obj.date()) # set_date() takes a datetime.date object
                     # Populate time spinboxes
                     self.hour_spinbox.set(f"{dt_obj.hour:02d}") # set() takes a string
                     self.minute_spinbox.set(f"{dt_obj.minute:02d}")
                 else:
                      # If date string is empty or invalid, set default date (e.g., today) and time
                      self.date_entry.set_date(datetime.now().date()) # Default to today
                      self.hour_spinbox.set("00")
                      self.minute_spinbox.set("00")

             except (ValueError, TypeError) as e:
                 print(f"Error parsing item date for editing: {e}")
                 messagebox.showwarning("日期解析错误", f"无法解析项目 '{item_data.get('name', '未命名')}' 的原始日期格式，请重新设置。\n原始日期: {item_data.get('date', '无')}")
                 # Set default values to allow user to re-enter
                 self.date_entry.set_date(datetime.now().date())
                 self.hour_spinbox.set("00")
                 self.minute_spinbox.set("00")


        # --- Buttons ---
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="保存", command=self.on_save).pack(side="left", expand=True, padx=5)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side="left", expand=True, padx=5)

        # Make the dialog modal
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.name_entry.focus_set() # Set focus to the name entry field

        # Center the dialog over its parent window
        self.update_idletasks() # Ensure window dimensions are calculated
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        # Calculate center position
        center_x = parent_x + (parent_width // 2) - (dialog_width // 2)
        center_y = parent_y + (parent_height // 2) - (dialog_height // 2)

        self.geometry(f'+{center_x}+{center_y}')


    def on_save(self):
        name = self.name_entry.get().strip()

        # Get the selected date
        try:
            selected_date_obj = self.date_entry.get_date() # Returns a datetime.date object
            date_str = selected_date_obj.strftime('%Y-%m-%d') # Format as YYYY-MM-DD
        except Exception as e:
             messagebox.showwarning("输入错误", f"获取日期时出错: {e}")
             return

        # Get and validate time
        try:
             hour_str = self.hour_spinbox.get()
             minute_str = self.minute_spinbox.get()
             # Attempt to convert to integer to validate
             hour = int(hour_str)
             minute = int(minute_str)
             # Check range explicitly (Spinbox range is a soft limit if manual input is possible)
             if not (0 <= hour <= 23 and 0 <= minute <= 59):
                 raise ValueError("Hour or minute out of range")

             time_str = f"{hour:02d}:{minute:02d}" # Format as HH:MM

        except ValueError:
             messagebox.showwarning("输入错误", "时间输入无效，请确保小时和分钟是有效的数字。")
             return
        except Exception as e:
             messagebox.showwarning("输入错误", f"获取时间时出错: {e}")
             return


        if not name:
             messagebox.showwarning("输入错误", "项目名称不能为空。")
             return

        # Combine date and time string in the required format 'YYYY-MM-DD HH:MM'
        datetime_str_to_save = f"{date_str} {time_str}"

        # Data is valid, store result and close
        self.result = {"name": name, "date": datetime_str_to_save}
        self.grab_release() # Release modal grab
        self.destroy()

    def on_cancel(self):
        self.result = None # Cancel operation, no data returned
        self.grab_release() # Release modal grab
        self.destroy()