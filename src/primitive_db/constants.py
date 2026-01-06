VALID_DATA_TYPES = {"int", "str", "bool"}

METADATA_FILE = "db_meta.json"
DATA_DIR = "data"
TABLE_DATA_EXTENSION = ".json"

HELP_MESSAGE = """
***Операции с данными***
Функции:
<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...)-
создать запись
<command> select from <имя_таблицы> where <столбец> = <значение>-
прочитать записи по условию
<command> select from <имя_таблицы> - прочитать все записи
<command> update <имя_таблицы> set <столбец1> = <новое_значение1>
where <столбец_условия> = <значение_условия> - обновить запись
<command> delete from <имя_таблицы> where <столбец> = <значение>-
удалить запись
<command> info <имя_таблицы> - вывести информацию о таблице
<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип>-
создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу
<command> clear_cache - очистить кэш запросов
<command> cache_stats - показать статистику кэша

Общие команды:
<command> exit - выход из программы
<command> help - справочная информация
"""

ERROR_MESSAGES = {
    "table_not_found": 'Ошибка: Таблица "{table_name}" не существует.',
    "table_exists": 'Ошибка: Таблица "{table_name}" уже существует.',
    "invalid_column_format": ('Некорректное значение: "{value}". '
                              'Ожидается формат "имя:тип"'),
    "invalid_data_type": ('Некорректный тип данных в "{value}". '
                         'Допустимые типы: {valid_types}'),
    "values_count_mismatch": ('Ошибка: Ожидается {expected} значений, '
                             'получено {actual}'),
    "invalid_type": ('Ошибка: Неверный тип для столбца "{column}". '
                     'Ожидается {expected_type}'),
    "file_not_found": "Файл не найден: {file}",
    "parse_error": "Ошибка разбора команды: {error}",
    "unknown_command": 'Функции "{command}" нет. Попробуйте снова.',
    "insufficient_args": "Ошибка: Недостаточно аргументов. Использование: {usage}",
}

SUCCESS_MESSAGES = {
    "table_created": 'Таблица "{table_name}" успешно создана со столбцами: {columns}',
    "table_dropped": 'Таблица "{table_name}" успешно удалена.',
    "record_inserted": ('Запись с ID={record_id} успешно '
                        'добавлена в таблицу "{table_name}".'),
    "records_updated": ('Запись(и) ({count} шт.) в таблице "{table_name}" '
                       'успешно обновлена(ы).'),
    "records_deleted": ('Запись(и) ({count} шт.) успешно удалена(ы) '
                       'из таблицы "{table_name}".'),
    "cache_cleared": "Кэш запросов очищен.",
    "operation_cancelled": "Операция отменена пользователем.",
}

COMMANDS = {
    "exit", "help", "clear_cache", "cache_stats",
    "create_table", "drop_table", "list_tables", "info",
    "insert", "select", "update", "delete"
}
