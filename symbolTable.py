symbol_table = {}
from logger import log_message

def register_variable(name, var_type, value):
    if name in symbol_table:
        log_message("ERROR", f"Variable '{name}' ya declarada.")
        return False
    symbol_table[name] = {"type": var_type, "value": value}
    return True

def lookup_variable(name):
    if name not in symbol_table:
        log_message("ERROR", f"Variable '{name}' no declarada.")
        return None
    return symbol_table[name]

def validate_variable_usage(var_name, expected_type):
    var = lookup_variable(var_name)
    if var is None:
        # lookup ya registra el error
        return False
    if var["type"] != expected_type:
        log_message("ERROR", f"Se esperaba una variable de tipo '{expected_type}' pero se encontró '{var['type']}' para '{var_name}'.")
        return False
    return True
