import json
import os
import sys

# Define data folder name
DATA_FOLDER_NAME = 'data'
DDL_FILE_NAME = 'ddl_items.json'
SETTINGS_FILE_NAME = 'settings.json'

def get_app_base_path():
    """
    Gets the base directory where the application is running from.
    Handles both running from script and PyInstaller bundle.
    """
    if getattr(sys, 'frozen', False):
        # Running from a PyInstaller bundle
        # In --onefile mode, files are extracted to a temp dir accessible relative to sys.executable
        # In --onedir mode, files are in the same directory as sys.executable
        # os.path.dirname(sys.executable) is the directory containing the executable
        return os.path.dirname(sys.executable)
    else:
        # Running from script (.py file)
        # __file__ is the path to the current script (data_manager.py in utils folder)
        # os.path.dirname(os.path.abspath(__file__)) gives the directory of this script (ddltool/utils)
        # os.path.join(..., os.pardir) goes up one level (ddltool) which is the project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(script_dir, os.pardir)
        return project_root


class DataManager:
    def __init__(self):
        # Get the base path for data files
        app_base_path = get_app_base_path()
        data_dir_path = os.path.join(app_base_path, DATA_FOLDER_NAME)

        # Ensure data directory exists
        os.makedirs(data_dir_path, exist_ok=True)

        self.ddl_file_path = os.path.join(data_dir_path, DDL_FILE_NAME)
        self.settings_file_path = os.path.join(data_dir_path, SETTINGS_FILE_NAME)

        # print(f"Data file path: {self.ddl_file_path}") # Debug print
        # print(f"Settings file path: {self.settings_file_path}") # Debug print


    def load_ddl_items(self):
        if not os.path.exists(self.ddl_file_path):
            return [] # File not found, return empty list

        try:
            with open(self.ddl_file_path, 'r', encoding='utf-8') as f:
                items = json.load(f)
                if not isinstance(items, list):
                    print(f"Warning: {self.ddl_file_path} content is not a list. Returning empty list.")
                    return []
                # simple validation
                # items = [item for item in items if isinstance(item, dict) and 'name' in item and 'date' in item]
                return items
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {self.ddl_file_path}: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while loading {self.ddl_file_path}: {e}")
            return []

    def save_ddl_items(self, items):
        try:
            with open(self.ddl_file_path, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=4, ensure_ascii=False) # ensure_ascii=False supports Chinese
        except Exception as e:
            print(f"Error saving {self.ddl_file_path}: {e}")

    def load_settings(self):
        # Add new default settings
        default_settings = {
            'window_x': 100,
            'window_y': 50,
            'window_width': 300,
            'window_height': 150,
            'auto_start': False,
            'font_family': 'Arial', # Default font
            'font_size': 10,       # Default size
            'font_weight': 'normal', # Default weight
            'fg_color': 'white',   # Default foreground color (white)
            'bg_color': 'black',   # Default background color (black)
            'alpha': 1.0,          # Default transparency (opaque)
            'theme': 'arc'         # Default theme (requires ttkthemes)
        }

        if not os.path.exists(self.settings_file_path):
            return default_settings

        try:
            with open(self.settings_file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if not isinstance(settings, dict):
                     print(f"Warning: {self.settings_file_path} content is not a dictionary. Returning default settings.")
                     return default_settings
                # Merge loaded settings and default settings. Loaded values overwrite defaults.
                merged_settings = default_settings.copy()
                merged_settings.update(settings) # Loaded settings overwrite defaults
                return merged_settings

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {self.settings_file_path}: {e}")
            return default_settings
        except Exception as e:
            print(f"An unexpected error occurred while loading {self.settings_file_path}: {e}")
            return default_settings


    def save_settings(self, settings):
        try:
            with open(self.settings_file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {self.settings_file_path}: {e}")