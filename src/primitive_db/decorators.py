
import time


from functools import wraps
from .constants import ERROR_MESSAGES


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            error_msg = str(e)
            if "table" in error_msg.lower() or "таблиц" in error_msg.lower():
                return None, ERROR_MESSAGES["table_not_found"].format(table_name=error_msg)
            return None, f'Ошибка ключа: {error_msg}'
        except ValueError as e:
            return None, f'Ошибка значения: {e}'
        except FileNotFoundError as e:
            return None, ERROR_MESSAGES["file_not_found"].format(file=e)
        except TypeError as e:
            return None, f'Ошибка типа данных: {e}'
        except Exception as e:
            return None, f'Неожиданная ошибка в функции {func.__name__}: {e}'
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) > 1:
                target = args[1]
                prompt = f'Вы уверены, что хотите выполнить "{action_name}" таблицы "{target}"? [y/n]: '
            else:
                prompt = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            
            response = input(prompt).strip().lower()
            if response != 'y':
                print("Операция отменена.")
                return None, "Операция отменена пользователем."
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        elapsed = end_time - start_time
        
        print(f'Функция {func.__name__} выполнилась за {elapsed:.3f} секунд')
        return result
    
    return wrapper


def create_cacher():
    cache = {}
    
    def cache_result(key, value_func, *args, **kwargs):
        if key in cache:
            return cache[key]
        
        result = value_func(*args, **kwargs)
        cache[key] = result
        return result
    
    def clear_cache():
        cache.clear()
    
    def get_cache_stats():
        return {
            'size': len(cache),
            'keys': list(cache.keys())
        }
    
    cache_result.clear = clear_cache
    cache_result.stats = get_cache_stats
    
    return cache_result


cacher = create_cacher()
