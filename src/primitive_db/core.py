
from prettytable import PrettyTable
from .decorators import handle_db_errors, confirm_action, log_time, cacher
from .constants import VALID_DATA_TYPES, ERROR_MESSAGES, SUCCESS_MESSAGES


def validate_column_definitions(columns):
    validated_columns = []
    
    for col_def in columns:
        if ":" not in col_def:
            raise ValueError(ERROR_MESSAGES["invalid_column_format"].format(value=col_def))
        
        col_name, col_type = col_def.split(":", 1)
        col_name = col_name.strip()
        col_type = col_type.strip().lower()
        
        if not col_name:
            raise ValueError(f'Некорректное имя столбца в "{col_def}"')
        
        if col_type not in VALID_DATA_TYPES:
            valid_types_str = ", ".join(VALID_DATA_TYPES)
            raise ValueError(ERROR_MESSAGES["invalid_data_type"].format(
                value=col_def, valid_types=valid_types_str
            ))
        
        validated_columns.append({"name": col_name, "type": col_type})
    
    return validated_columns, None


def validate_value_type(value, expected_type):
    if expected_type == "int":
        return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
    elif expected_type == "str":
        return isinstance(value, str)
    elif expected_type == "bool":
        return isinstance(value, bool) or value.lower() in ["true", "false"]
    return False


def convert_value(value, expected_type):
    if expected_type == "int":
        return int(value)
    elif expected_type == "str":
        return str(value)
    elif expected_type == "bool":
        if isinstance(value, bool):
            return value
        return value.lower() == "true"
    return value


@handle_db_errors
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        raise ValueError(ERROR_MESSAGES["table_exists"].format(table_name=table_name))
    
    validated_columns, error = validate_column_definitions(columns)
    if error:
        raise ValueError(error)
    
    table_columns = [{"name": "ID", "type": "int"}]
    table_columns.extend(validated_columns)
    
    metadata[table_name] = {
        "columns": table_columns,
        "data": []
    }
    
    columns_str = ", ".join([f'{col["name"]}:{col["type"]}' for col in table_columns])
    
    return metadata, SUCCESS_MESSAGES["table_created"].format(
        table_name=table_name, columns=columns_str
    )


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(ERROR_MESSAGES["table_not_found"].format(table_name=table_name))
    
    del metadata[table_name]
    return metadata, SUCCESS_MESSAGES["table_dropped"].format(table_name=table_name)


@handle_db_errors
def list_tables(metadata):
    if not metadata:
        return "В базе данных нет таблиц."
    
    tables = list(metadata.keys())
    if len(tables) == 1:
        return f"- {tables[0]}"
    else:
        return "\n".join([f"- {table}" for table in tables])


@handle_db_errors
def get_table_info(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(ERROR_MESSAGES["table_not_found"].format(table_name=table_name))
    
    table_info = metadata[table_name]
    columns_str = ", ".join([f'{col["name"]}:{col["type"]}' for col in table_info["columns"]])
    count = len(table_info["data"])
    
    info = f"Таблица: {table_name}\n"
    info += f"Столбцы: {columns_str}\n"
    info += f"Количество записей: {count}"
    
    return info, None


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise KeyError(ERROR_MESSAGES["table_not_found"].format(table_name=table_name))
    
    table_info = metadata[table_name]
    columns = table_info["columns"][1:]
    data = table_info["data"]
    
    if len(values) != len(columns):
        raise ValueError(ERROR_MESSAGES["values_count_mismatch"].format(
            expected=len(columns), actual=len(values)
        ))
    
    validated_values = []
    for i, (value, column) in enumerate(zip(values, columns)):
        col_name = column["name"]
        col_type = column["type"]
        
        if not validate_value_type(value, col_type):
            raise ValueError(ERROR_MESSAGES["invalid_type"].format(
                column=col_name, expected_type=col_type
            ))
        
        converted_value = convert_value(value, col_type)
        validated_values.append(converted_value)
    
    if data:
        last_id = max([record["ID"] for record in data])
        new_id = last_id + 1
    else:
        new_id = 1
    
    record = {"ID": new_id}
    for i, column in enumerate(columns):
        record[column["name"]] = validated_values[i]
    
    data.append(record)
    
    return record, SUCCESS_MESSAGES["record_inserted"].format(
        record_id=new_id, table_name=table_name
    )


@handle_db_errors
@log_time
def select(table_data, where_clause=None, use_cache=True):
    """Выбирает записи из таблицы."""
    if where_clause is None:
        return table_data
    
    if use_cache:
        cache_key = f"select_where_{hash(str(where_clause))}"
        
        def get_filtered_data():
            filtered = []
            for record in table_data:
                match = True
                for column, value in where_clause.items():
                    if str(record.get(column, "")) != str(value):
                        match = False
                        break
                if match:
                    filtered.append(record)
            return filtered
        
        return cacher(cache_key, get_filtered_data)
    else:
        filtered = []
        for record in table_data:
            match = True
            for column, value in where_clause.items():
                if str(record.get(column, "")) != str(value):
                    match = False
                    break
            if match:
                filtered.append(record)
        
        return filtered


@handle_db_errors
def update(table_data, set_clause, where_clause):
    updated_count = 0
    
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if str(record.get(column, "")) != str(value):
                match = False
                break
        
        if match:
            for column, new_value in set_clause.items():
                if column in record:
                    record[column] = new_value
            updated_count += 1
    
    return table_data, updated_count


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    to_delete = []
    
    for i, record in enumerate(table_data):
        match = True
        for column, value in where_clause.items():
            if str(record.get(column, "")) != str(value):
                match = False
                break
        
        if match:
            to_delete.append(i)
    
    deleted_ids = []
    for index in sorted(to_delete, reverse=True):
        deleted_ids.append(table_data[index]["ID"])
        del table_data[index]
    deleted_count = len(to_delete)
    if deleted_ids:
        ids_str = ", ".join(map(str, deleted_ids))
        return table_data, deleted_count, f'Удалены записи с ID: {ids_str}'
    
    return table_data, deleted_count, SUCCESS_MESSAGES["records_deleted"].format(
        count=deleted_count, table_name="таблицы"
    )


def format_table_data(columns, data):
    if not data:
        return "В таблице нет записей."
    
    table = PrettyTable()
    
    column_names = [col["name"] for col in columns]
    table.field_names = column_names
    
    for record in data:
        row = []
        for col_name in column_names:
            value = record.get(col_name, "")
            row.append(value)
        table.add_row(row)
    
    table.align = "l"
    
    return str(table)


def clear_select_cache():
    cacher.clear()


def get_cache_statistics():
    return cacher.stats()
