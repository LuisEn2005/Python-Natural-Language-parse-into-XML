import xml.etree.ElementTree as ET
import re
from xmlUtils import generate_open_roberta_id
from symbolTable import register_variable, validate_variable_usage

def findVar(line, block_start, variables_declared):
    pattern = r"^var\s+(\w+)\s*=\s*(.+)"
    match = re.search(pattern, line)
    
    if match:
        variable_name = match.group(1)
        variable_value = match.group(2)
        
        # Verifica si el nodo 'variables' necesita ser creado
        if not variables_declared:
            variables = ET.SubElement(block_start, "statement", {"name": "ST"})
            variables_declared = True
            block_start.find("mutation").set("declare", "true")
        else:
            # Recupera la referencia al nodo 'statement' ya existente
            variables = block_start.find("statement[@name='ST']")
        
        # Crear un bloque para la declaración de la variable
        variable_block = ET.SubElement(variables, "block", {
            "type": "robGlobalVariables_declare",
            "id": generate_open_roberta_id(),
            "intask": "true",
            "deletable": "false"
        })

        # Identificar el tipo de variable y configurar los nodos hijos
        if variable_value.startswith("[") and variable_value.endswith("]"):
            # Procesar listas
            items = variable_value.strip("[]").split(",")
            mutation = ET.SubElement(variable_block, "mutation", {
                "next": "true",
                "declaration_type": "Array_Number"
            })
            field_type = "Array_Number"
            block_type = "robLists_create_with"
            field_name = "LIST_TYPE"

            field_var = ET.SubElement(variable_block, "field", {"name": "VAR"})
            field_type_field = ET.SubElement(variable_block, "field", {"name": "TYPE"})
            field_var.text = variable_name
            field_type_field.text = field_type

            value = ET.SubElement(variable_block, "value", {"name": "VALUE"})
            block_value = ET.SubElement(value, "block", {
                "type": block_type,
                "id": generate_open_roberta_id(),
                "intask": "true"
            })

            mutation_items = ET.SubElement(block_value, "mutation", {
                "items": str(len(items)),
                "list_type": "Number"
            })
            field_list_type = ET.SubElement(block_value, "field", {"name": field_name})
            field_list_type.text = "Number"

            for idx, item in enumerate(items):
                value_name = f"ADD{idx}"
                value_element = ET.SubElement(block_value, "value", {"name": value_name})
                item_block = ET.SubElement(value_element, "block", {
                    "type": "math_integer",
                    "id": generate_open_roberta_id(),
                    "intask": "true"
                })
                field_item = ET.SubElement(item_block, "field", {"name": "NUM"})
                field_item.text = item.strip()
        else:
            if variable_value.isdigit():
                mutation = ET.SubElement(variable_block, "mutation", {
                    "next": "true",
                    "declaration_type": "Number"
                })
                field_type = "Number"
                block_type = "math_integer"
                field_name = "NUM"
            
            elif variable_value.lower() in ("true", "false"):
                mutation = ET.SubElement(variable_block, "mutation", {
                    "next": "true",
                    "declaration_type": "Boolean"
                })
                field_type = "Boolean"
                block_type = "logic_boolean"
                field_name = "BOOL"
            register_variable(variable_name, field_type, variable_value)
            # Configuración de nodos comunes
            field_var = ET.SubElement(variable_block, "field", {"name": "VAR"})
            field_type_field = ET.SubElement(variable_block, "field", {"name": "TYPE"})
            field_var.text = variable_name
            field_type_field.text = field_type
            
            value = ET.SubElement(variable_block, "value", {"name": "VALUE"})
            block_value = ET.SubElement(value, "block", {
                "type": block_type,
                "id": generate_open_roberta_id(),
                "intask": "true"
            })
            
            if block_type == "math_integer":
                field_value = ET.SubElement(block_value, "field", {"name": field_name})
                field_value.text = variable_value
            elif block_type == "logic_boolean":
                field_value = ET.SubElement(block_value, "field", {"name": field_name})
                field_value.text = variable_value.upper()
            elif block_type == "robLists_create_with":
                mutation_items = ET.SubElement(block_value, "mutation", {
                    "items": "0",
                    "list_type": "Number"
                })
                field_list_type = ET.SubElement(block_value, "field", {"name": field_name})
                field_list_type.text = "Number"
            elif block_type == "text":
                field_value = ET.SubElement(block_value, "field", {"name": field_name})
                field_value.text = variable_value
            pass

def generate_action_block(line, instance_program):
    # Patrones para acciones con y sin distancia
    pattern_with_distance = r"Move\s+(Forward|Backward)\s+(\w+|\d+)\s+at\s+(\w+|\d+)"
    pattern_without_distance = r"Move\s+(Forward|Backward)\s+at\s+(\w+|\d+)"
    
    match = re.match(pattern_with_distance, line, re.I)
    has_distance = True

    if not match:  # Si no coincide con distancia, intentar sin distancia
        match = re.match(pattern_without_distance, line, re.I)
        has_distance = False
    
    if not match:
        return  # No se encontró una acción válida
    
    # Capturar valores según el patrón que coincida
    direction = match.group(1).upper()
    speed = match.group(3 if has_distance else 2)
    distance = match.group(2) if has_distance else None  # Distancia será None si no está presente

    if not speed.isdigit():
        validate_variable_usage(speed, "Number")
    if has_distance and not distance.isdigit():
        validate_variable_usage(distance, "Number")
    
    # Crear el bloque principal
    if(has_distance):
        block_action = ET.SubElement(instance_program, "block", {
            "type": "robActions_motorDiff_on_for",
            "id": generate_open_roberta_id(),
            "intask": "true"
        })
    else:
        block_action = ET.SubElement(instance_program, "block", {
            "type": "robActions_motorDiff_on",
            "id": generate_open_roberta_id(),
            "intask": "true"
        })
    
    # Configurar dirección
    if direction == "FORWARD":
        ET.SubElement(block_action, "field", {"name": "DIRECTION"}).text = "FOREWARD"
    elif direction == "BACKWARD":
        if(has_distance):
            ET.SubElement(block_action, "field", {"name": "DIRECTION"}).text = "BACKWARDS"
        ET.SubElement(block_action, "field", {"name": "DIRECTION"}).text = "BACKWARD"

    # Configurar potencia (speed)
    value_speed = ET.SubElement(block_action, "value", {"name": "POWER"})
    if speed.isdigit():
        speed_block = ET.SubElement(value_speed, "block", {
            "type": "math_integer",
            "id": generate_open_roberta_id(),
            "intask": "true"
        })
        ET.SubElement(speed_block, "field", {"name": "NUM"}).text = speed
    else:
        speed_block = ET.SubElement(value_speed, "block", {
            "type": "variables_get",
            "id": generate_open_roberta_id(),
            "intask": "true"
        })
        ET.SubElement(speed_block, "field", {"name": "VAR"}).text = speed

    # Configurar distancia (solo si está presente)
    if has_distance:
        value_distance = ET.SubElement(block_action, "value", {"name": "DISTANCE"})
        if distance.isdigit():
            distance_block = ET.SubElement(value_distance, "block", {
                "type": "math_integer",
                "id": generate_open_roberta_id(),
                "intask": "true"
            })
            ET.SubElement(distance_block, "field", {"name": "NUM"}).text = distance
        else:
            distance_block = ET.SubElement(value_distance, "block", {
                "type": "variables_get",
                "id": generate_open_roberta_id(),
                "intask": "true"
            })
            ET.SubElement(distance_block, "field", {"name": "VAR"}).text = distance

def generate_turn_block(line, instance_program):
    pattern_with_distance = r"Turn\s+(Right|Left)\s+(\w+|\d+)\s+at\s+(\w+|\d+)"
    pattern_without_distance = r"Turn\s+(Right|Left)\s+at\s+(\w+|\d+)"
    
    match = re.match(pattern_with_distance, line, re.I)
    has_degree = True

    if not match:  # Si no coincide con distancia, intentar sin distancia
        match = re.match(pattern_without_distance, line, re.I)
        has_degree = False
    
    if not match:
        return  # No se encontró una acción válida
    
    # Capturar valores según el patrón que coincida
    direction = match.group(1).upper()
    speed = match.group(3 if has_degree else 2)
    degree = match.group(2) if has_degree else None  # Distancia será None si no está presente
    
    if not speed.isdigit():
        validate_variable_usage(speed)  # Verifica que `speed` esté declarada.
    if has_degree and not degree.isdigit():
        validate_variable_usage(degree)
    
    # Crear el bloque principal
    if(has_degree):
        block_action = ET.SubElement(instance_program, "block", {
            "type": "robActions_motorDiff_turn_for",
            "id": generate_open_roberta_id(),
            "intask": "true"
        })
    else:
        block_action = ET.SubElement(instance_program, "block", {
            "type": "robActions_motorDiff_turn",
            "id": generate_open_roberta_id(),
            "intask": "true"
        })
    
    # Configurar dirección
    if direction == "RIGHT":
        ET.SubElement(block_action, "field", {"name": "DIRECTION"}).text = "RIGHT"
    elif direction == "LEFT":
        ET.SubElement(block_action, "field", {"name": "DIRECTION"}).text = "LEFT"

    # Configurar potencia (speed)
    value_speed = ET.SubElement(block_action, "value", {"name": "POWER"})
    if speed.isdigit():
        speed_block = ET.SubElement(value_speed, "block", {
            "type": "math_integer",
            "id": generate_open_roberta_id(),
            "intask": "true"
        })
        ET.SubElement(speed_block, "field", {"name": "NUM"}).text = speed
    else:
        speed_block = ET.SubElement(value_speed, "block", {
            "type": "variables_get",
            "id": generate_open_roberta_id(),
            "intask": "true"
        })
        ET.SubElement(speed_block, "field", {"name": "VAR"}).text = speed

    # Configurar distancia (solo si está presente)
    if has_degree:
        value_degree = ET.SubElement(block_action, "value", {"name": "DEGREE"})
        if degree.isdigit():
            degree_block = ET.SubElement(value_degree, "block", {
                "type": "math_integer",
                "id": generate_open_roberta_id(),
                "intask": "true"
            })
            ET.SubElement(degree_block, "field", {"name": "NUM"}).text = degree
        else:
            degree_block = ET.SubElement(value_degree, "block", {
                "type": "variables_get",
                "id": generate_open_roberta_id(),
                "intask": "true"
            })
            ET.SubElement(degree_block, "field", {"name": "VAR"}).text = degree