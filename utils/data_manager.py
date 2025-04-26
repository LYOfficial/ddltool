import json
import os

class DataManager:
    def __init__(self, ddl_file_path, settings_file_path):
        self.ddl_file_path = ddl_file_path
        self.settings_file_path = settings_file_path

    def load_ddl_items(self):
        if not os.path.exists(self.ddl_file_path):
            # print(f"Data file not found: {self.ddl_file_path}") # Debug print
            return [] # 文件不存在，返回空列表

        try:
            with open(self.ddl_file_path, 'r', encoding='utf-8') as f:
                items = json.load(f)
                if not isinstance(items, list): # 检查加载的数据是否为列表
                    print(f"Warning: {self.ddl_file_path} content is not a list. Returning empty list.")
                    return []
                # 可以在这里简单验证每个item是否是字典且有name和date键
                # simple_validation = all(isinstance(item, dict) and 'name' in item and 'date' in item for item in items)
                # if not simple_validation: print("Warning: Some items in ddl_items.json have unexpected format.")
                return items
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {self.ddl_file_path}: {e}")
            return [] # 文件读取或解析错误，返回空列表
        except Exception as e:
            print(f"An unexpected error occurred while loading {self.ddl_file_path}: {e}")
            return []

    def save_ddl_items(self, items):
        try:
            with open(self.ddl_file_path, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=4, ensure_ascii=False) # ensure_ascii=False 支持中文
        except Exception as e:
            print(f"Error saving {self.ddl_file_path}: {e}")

    def load_settings(self):
        # 提供更大的默认值
        default_settings = {
            'window_x': 100,
            'window_y': 50,
            'window_width': 300, # 初始宽度大一些
            'window_height': 150, # 初始高度大一些
            'auto_start': False
            # 可以添加更多设置，例如字体大小 'font_size': 10, 背景色 'bg_color': 'black' 等
        }

        if not os.path.exists(self.settings_file_path):
            # print(f"Settings file not found: {self.settings_file_path}") # Debug print
            return default_settings # 文件不存在，返回默认设置

        try:
            with open(self.settings_file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if not isinstance(settings, dict): # 检查加载的数据是否为字典
                     print(f"Warning: {self.settings_file_path} content is not a dictionary. Returning default settings.")
                     return default_settings
                # 合并加载的设置和默认设置，确保所有键都存在，加载的值优先
                return {**default_settings, **settings}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {self.settings_file_path}: {e}")
            return default_settings # 文件读取或解析错误，返回默认设置
        except Exception as e:
            print(f"An unexpected error occurred while loading {self.settings_file_path}: {e}")
            return default_settings

    def save_settings(self, settings):
        try:
            with open(self.settings_file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False) # ensure_ascii=False 支持中文
        except Exception as e:
            print(f"Error saving {self.settings_file_path}: {e}")