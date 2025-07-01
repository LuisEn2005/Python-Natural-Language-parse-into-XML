symbol_table = {}

def register_variable(name, var_type, value):
    if name in symbol_table:
        raise ValueError(f"Variable '{name}' ya declarada.")
    symbol_table[name] = {"type": var_type, "value": value}

def lookup_variable(name):
    if name not in symbol_table:
        raise ValueError(f"Variable '{name}' no declarada.")
    return symbol_table[name]

def validate_variable_usage(var_name, expected_type):
    var = lookup_variable(var_name)
    if var["type"] != expected_type:
        raise ValueError(f"Se esperaba una variable de tipo '{expected_type}' pero se encontró '{var['type']}' para '{var_name}'.")