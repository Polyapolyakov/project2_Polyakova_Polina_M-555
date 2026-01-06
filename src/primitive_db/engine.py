
import shlex


from .utils import load_metadata, save_metadata, load_table_data, save_table_data, delete_table_file
from .core import (
    create_table, drop_table, list_tables, get_table_info,
    insert, select, update, delete, format_table_data,
    clear_select_cache, get_cache_statistics
)
from .parser import (
    parse_insert_command, parse_select_command,
    parse_update_command, parse_delete_command
)
from .constants import HELP_MESSAGE, ERROR_MESSAGES, COMMANDS


def print_help():
    print(HELP_MESSAGE)


def parse_command(user_input):
    try:
        parts = shlex.split(user_input)
        if not parts:
            return None, []
        return parts[0].lower(), parts[1:]
    except ValueError as e:
        return None, [ERROR_MESSAGES["parse_error"].format(error=e)]


def run():
    print("\n***Операции с данными***")
    print_help()
    
    while True:
        try:
            metadata = load_metadata()
            user_input = input(">>>Введите команду: ").strip()
            if not user_input:
                continue
            command, args = parse_command(user_input)
            
            if command == "exit":
                print("Выход из программы...")
                break
                
            elif command == "help":
                print_help()
                
            elif command == "clear_cache":
                clear_select_cache()
                print("Кэш запросов очищен.")
                
            elif command == "cache_stats":
                stats = get_cache_statistics()
                print(f"Статистика кэша:")
                print(f"  Размер: {stats['size']} записей")
                if stats['keys']:
                    print(f"  Ключи: {', '.join(stats['keys'][:5])}")
                    if len(stats['keys']) > 5:
                        print(f"  ... и еще {len(stats['keys']) - 5} ключей")
                else:
                    print("  Кэш пуст")
                
            elif command == "create_table":
                if len(args) < 2:
                    print(ERROR_MESSAGES["insufficient_args"].format(
                        usage="create_table <имя> <столбец1:тип> ..."
                    ))
                    continue
                
                table_name = args[0]
                columns = args[1:]
                
                new_metadata, message = create_table(metadata, table_name, columns)
                print(message)
                
                if table_name in new_metadata:
                    save_metadata(new_metadata)
                    save_table_data(table_name, [])
                    metadata = new_metadata
                    
            elif command == "drop_table":
                if len(args) < 1:
                    print(ERROR_MESSAGES["insufficient_args"].format(
                        usage="drop_table <имя_таблицы>"
                    ))
                    continue
                
                table_name = args[0]
                
                result = drop_table(metadata, table_name)
                if result:
                    new_metadata, message = result
                    print(message)
                    
                    if table_name not in new_metadata:
                        save_metadata(new_metadata)
                        delete_table_file(table_name)
                        metadata = new_metadata
                else:
                    continue
                    
            elif command == "list_tables":
                result = list_tables(metadata)
                print(result)
                
            elif command == "info":
                if len(args) < 1:
                    print(ERROR_MESSAGES["insufficient_args"].format(
                        usage="info <имя_таблицы>"
                    ))
                    continue
                
                table_name = args[0]
                info, error = get_table_info(metadata, table_name)
                
                if error:
                    print(error)
                else:
                    print(info)
                    
            elif command == "insert":
                table_name, values = parse_insert_command(args)
                if table_name is None:
                    print(values)
                    continue
                
                if table_name not in metadata:
                    print(ERROR_MESSAGES["table_not_found"].format(table_name=table_name))
                    continue
                
                table_data = load_table_data(table_name)
                
                record, message = insert(metadata, table_name, values)
                if record:
                    table_data.append(record)
                    save_table_data(table_name, table_data)
                    print(message)
                else:
                    print(message)
                    
            elif command == "select":
                table_name, where_clause, error = parse_select_command(args)
                if error:
                    print(error)
                    continue
                
                if table_name not in metadata:
                    print(ERROR_MESSAGES["table_not_found"].format(table_name=table_name))
                    continue
                
                table_data = load_table_data(table_name)
                
                if where_clause:
                    result_data = select(table_data, where_clause, use_cache=True)
                else:
                    result_data = table_data
                
                columns = metadata[table_name]["columns"]
                formatted = format_table_data(columns, result_data)
                print(formatted)
                
            elif command == "update":
                table_name, set_clause, where_clause, error = parse_update_command(args)
                if error:
                    print(error)
                    continue
                
                if table_name not in metadata:
                    print(ERROR_MESSAGES["table_not_found"].format(table_name=table_name))
                    continue
                
                table_data = load_table_data(table_name)
                
                updated_data, count = update(table_data, set_clause, where_clause)
                
                if count > 0:
                    save_table_data(table_name, updated_data)
                    print(f'Запись(и) ({count} шт.) в таблице "{table_name}" успешно обновлена(ы).')
                    clear_select_cache()
                else:
                    print('Записи для обновления не найдены.')
                    
            elif command == "delete":
                table_name, where_clause, error = parse_delete_command(args)
                if error:
                    print(error)
                    continue
                
                if table_name not in metadata:
                    print(ERROR_MESSAGES["table_not_found"].format(table_name=table_name))
                    continue
                
                table_data = load_table_data(table_name)
                
                result = delete(table_data, where_clause)
                if result:
                    updated_data, count, message = result
                    
                    if count > 0:
                        save_table_data(table_name, updated_data)
                        print(message)
                        clear_select_cache()
                    else:
                        print('Записи для удаления не найдены.')
                else:
                    continue
                    
            else:
                print(ERROR_MESSAGES["unknown_command"].format(command=command))
                print_help()
                
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем.")
            break
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")


def main():
    ran()
