
import json
import os

from pathlib import Path
from .constants import METADATA_FILE, DATA_DIR, TABLE_DATA_EXTENSION


def ensure_data_dir():
    Path(DATA_DIR).mkdir(exist_ok=True)


def load_metadata(filepath=METADATA_FILE):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка: Файл {filepath} поврежден. Создан новый.")
        return {}


def save_metadata(data, filepath=METADATA_FILE):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        return False


def load_table_data(table_name):
    ensure_data_dir()
    filepath = f"{DATA_DIR}/{table_name}{TABLE_DATA_EXTENSION}"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Ошибка: Файл {filepath} поврежден. Создан новый.")
        return []


def save_table_data(table_name, data):
    ensure_data_dir()
    filepath = f"{DATA_DIR}/{table_name}{TABLE_DATA_EXTENSION}"
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении данных таблицы {table_name}: {e}")
        return False


def delete_table_file(table_name):
    filepath = f"{DATA_DIR}/{table_name}{TABLE_DATA_EXTENSION}"
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Ошибка при удалении файла таблицы {table_name}: {e}")
    return False
