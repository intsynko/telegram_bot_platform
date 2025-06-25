import re


def check_condition(data, condition):
    path, operator, value = split_condition(condition)

    return eval(f'{get_value_by_path(data, path)} {operator} {value}')


def get_value_by_path(data: dict, path: str):
    for item in path.split('.'):
        if item.startswith('\'') and item.endswith('\''):
            item = item[1:-1]
        data = data.get(item, {})
    if data == {}:
        return None
    return data


def split_condition(condition):
    in_variable = False
    for index, char in enumerate(condition):
        if not in_variable:
            if char == "'":
                in_variable = True
            if char == " ":
                break
        else:
            if char == "'":
                in_variable = False
        continue
    return condition[:index], *condition[index+1:].split(' ')


def format_str(pattern: str, data: dict):
    paths = re.findall(r"{{.+}}", pattern)
    for path in paths:
        pattern = pattern.replace(path, get_value_by_path(data, path[2:-2]) or "")
    return pattern
