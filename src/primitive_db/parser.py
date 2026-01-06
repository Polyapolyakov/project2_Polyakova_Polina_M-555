
import re


from .constants import ERROR_MESSAGES


def parse_insert_values(values_str):
    values_str = values_str.strip()
    if values_str.startswith('(') and values_str.endswith(')'):
        values_str = values_str[1:-1]
    
    values = []
    current = ""
    in_quotes = False
    quote_char = None
    
    for char in values_str:
        if char in ('"', "'") and (not in_quotes or quote_char == char):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            else:
                in_quotes = False
                quote_char = None
            current += char
        elif char == ',' and not in_quotes:
            values.append(current.strip())
            current = ""
        else:
            current += char
    
    if current:
        values.append(current.strip())
    
    return values


def parse_where_clause(where_str):
    if not where_str:
        return None
    
    pattern = r'^\s*(\w+)\s*=\s*(.+)\s*$'
    match = re.match(pattern, where_str)
    
    if not match:
        return None
    
    column = match.group(1)
    value_str = match.group(2).strip()
    
    value = parse_value(value_str)
    
    return {column: value}


def parse_set_clause(set_str):
    pattern = r'^\s*(\w+)\s*=\s*(.+)\s*$'
    match = re.match(pattern, set_str)
    
    if not match:
        return None
    
    column = match.group(1)
    value_str = match.group(2).strip()
    
    value = parse_value(value_str)
    
    return {column: value}


def parse_value(value_str):
    value_str = value_str.strip()
    
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    if value_str.lower() == 'true':
        return True
    if value_str.lower() == 'false':
        return False
    
    try:
        return int(value_str)
    except ValueError:
        pass
    
    return value_str


def parse_insert_command(args):
    if len(args) < 4 or args[0].lower() != 'into' or args[2].lower() != 'values':
        return None, ERROR_MESSAGES["parse_error"].format(error="Некорректный формат команды INSERT")
    
    table_name = args[1]
    values_str = ' '.join(args[3:])
    values = parse_insert_values(values_str)
    
    return table_name, values


def parse_select_command(args):
    if len(args) < 2 or args[0].lower() != 'from':
        return None, None, ERROR_MESSAGES["parse_error"].format(error="Некорректный формат команды SELECT")
    
    table_name = args[1]
    where_clause = None
    
    # Проверяем наличие WHERE
    if len(args) > 3 and args[2].lower() == 'where':
        where_str = ' '.join(args[3:])
        where_clause = parse_where_clause(where_str)
        if where_clause is None:
            return table_name, None, ERROR_MESSAGES["parse_error"].format(error="Некорректное WHERE условие")
    
    return table_name, where_clause, None


def parse_update_command(args):
    if len(args) < 6 or args[1].lower() != 'set' or 'where' not in [arg.lower() for arg in args]:
        return None, None, None, ERROR_MESSAGES["parse_error"].format(error="Некорректный формат команды UPDATE")
    
    table_name = args[0]
    
    set_index = args.index('set') if 'set' in args else args.index('SET')
    where_index = args.index('where') if 'where' in args else args.index('WHERE')
    
    set_str = ' '.join(args[set_index + 1:where_index])
    set_clause = parse_set_clause(set_str)
    if set_clause is None:
        return None, None, None, ERROR_MESSAGES["parse_error"].format(error="Некорректное SET условие")
    
    where_str = ' '.join(args[where_index + 1:])
    where_clause = parse_where_clause(where_str)
    if where_clause is None:
        return None, None, None, ERROR_MESSAGES["parse_error"].format(error="Некорректное WHERE условие")
    
    return table_name, set_clause, where_clause, None


def parse_delete_command(args):
    if len(args) < 3 or args[0].lower() != 'from' or args[2].lower() != 'where':
        return None, None, ERROR_MESSAGES["parse_error"].format(error="Некорректный формат команды DELETE")
    
    table_name = args[1]
    where_str = ' '.join(args[3:])
    where_clause = parse_where_clause(where_str)
    
    if where_clause is None:
        return table_name, None, ERROR_MESSAGES["parse_error"].format(error="Некорректное WHERE условие")
    
    return table_name, where_clause, None
