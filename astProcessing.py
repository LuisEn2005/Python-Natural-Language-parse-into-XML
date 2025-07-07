import xml.etree.ElementTree as ET
import re
from xmlUtils import generate_open_roberta_id
from symbolTable import register_variable, validate_variable_usage
from graphviz import Digraph

AST = []
""" def visualize_ast(ast_nodes = AST, output_file="ast"):
    dot = Digraph(comment="AST", format="png")
    dot.attr(rankdir="TB")  # De arriba hacia abajo

    node_count = 0
    def add_node(dot, node, parent_id=None):
        nonlocal node_count
        node_id = f"node{node_count}"
        node_count += 1

        # Etiqueta del nodo
        if isinstance(node, VariableNode):
            label = f"VAR\\n{node.name} = {node.value}\\n<{node.var_type}>"
        elif isinstance(node, ActionNode):
            label = f"{node.action_type}\\nDir: {node.direction}\\nSpd: {node.speed}"
            if node.distance is not None:
                label += f"\\nDist: {node.distance}"
            if node.degree is not None:
                label += f"\\nDeg: {node.degree}"
        else:
            label = node.node_type

        dot.node(node_id, label, shape="box", style="filled", fillcolor="lightblue")

        if parent_id:
            dot.edge(parent_id, node_id)

        # Recurde sobre hijos (si implementas nodos compuestos en el futuro)
        for child in node.children:
            add_node(dot, child, node_id)

    # Agregar nodos raíz del AST
    for ast_node in ast_nodes:
        add_node(dot, ast_node)

    # Renderizar el archivo .png
    dot.render(filename=output_file, cleanup=True)
    print(f"AST visualizado en: {output_file}.png") """


class ASTNode:
    def __init__(self, node_type, children=None, value=None):
        self.node_type = node_type  # Tipo de nodo: "Variable", "Action", etc.
        self.children = children or []  # Hijos del nodo
        self.value = value  # Información adicional (e.g., nombre de variable, tipo, valor)

    def __repr__(self):
        return f"{self.node_type}({self.value}, Children: {len(self.children)})"

# Nodo específico para declaraciones de variables
class VariableNode(ASTNode):
    def __init__(self, name, var_type, value):
        super().__init__("Variable")
        self.name = name
        self.var_type = var_type
        self.value = value

    def __repr__(self):
        return f"VariableNode({self.name}: {self.var_type} = {self.value})"

# Nodo específico para acciones de movimiento
class ActionNode(ASTNode):
    def __init__(self, action_type, direction, speed, distance=None, degree=None):
        super().__init__("Action")
        self.action_type = action_type
        self.direction = direction
        self.speed = speed
        self.distance = distance
        self.degree = degree

    def __repr__(self):
        base = f"ActionNode({self.action_type}, {self.direction}, Speed: {self.speed}"
        if self.distance is not None:
            base += f", Distance: {self.distance}"
        if self.degree is not None:
            base += f", Degree: {self.degree}"
        return base + ")"

def setVarStatement(block_start):
    # Verifica si el nodo 'variables' necesita ser creado
    variables = block_start.find("statement[@name='ST']")
    if variables is None:
        variables = ET.SubElement(block_start, "statement", {"name": "ST"})
        block_start.find("mutation").set("declare", "true")

    return variables

def findVar(line, block_start):
    pattern = r"^var\s+(\w+)\s*=\s*(.+)"
    pattern_bool = r"^var\s+(\w+)\s*=\s*(\w+)\s*(==|!=|<|<=|>|>=)\s*(\w+)"
    pattern_math = r"^var\s+(\w+)\s*=\s*(\w+|\d+)\s*([\+\-\*/\^])\s*(\w+|\d+)"
    match = re.search(pattern, line)
    match_bool = re.search(pattern_bool, line)
    match_math = re.search(pattern_math, line)
    field_type = None
    block_type = None
    variables = setVarStatement(block_start)
    
    if match_bool:
        cmp_var(variables, match_bool)
    elif match_math:
        math_var(variables, match_math)
    elif match:
        variable_name = match.group(1)
        variable_value = match.group(2)
        
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

        register_variable(variable_name, field_type, variable_value)
        AST.append(VariableNode(variable_name, field_type, variable_value))
    return 

def cmp_var(variables, match_bool):
    variable_name = match_bool.group(1)
    first_var = match_bool.group(2)
    operator = match_bool.group(3)
    second_var = match_bool.group(4)


    validate_variable_usage(first_var, "Number")
    validate_variable_usage(second_var, "Number")

    opName = None

    if(operator == "=="):
        opName = "EQ"
    elif(operator == "!="):
        opName = "NEQ"
    elif(operator == "<"):
        opName = "LT"
    elif(operator == "<="):
        opName = "LTE"
    elif(operator == ">"):
        opName = "GT"
    elif(operator == ">="):
        opName = "GTE"
    if opName is None:
        raise ValueError(f"Operador de comparación inválido: {operator}")
    
    variable_block = ET.SubElement(variables, "block", {
        "type": "robGlobalVariables_declare",    
        "id": generate_open_roberta_id(),
        "intask": "true",
        "deletable": "false"
    })

    mutation = ET.SubElement(variable_block, "mutation", {
        "next": "true",
        "declaration_type": "Boolean"
    })

    block_type = "logic_compare"

    field_var = ET.SubElement(variable_block, "field", {"name": "VAR"})
    field_type_field = ET.SubElement(variable_block, "field", {"name": "TYPE"})
    field_var.text = variable_name
    field_type_field.text = "Boolean"

    value = ET.SubElement(variable_block, "value", {"name": "VALUE"})
    block_value = ET.SubElement(value, "block", {
        "type": block_type,
        "id": generate_open_roberta_id(),
        "intask": "true"
    })
    field_value = ET.SubElement(block_value, "field", {"name": "OP"})
    
    field_value.text = opName
    valueA = ET.SubElement(block_value, "value", {"name": "A"})
    block_valueA = ET.SubElement(valueA, "block", {
        "type": "variables_get",
        "id": generate_open_roberta_id(),
        "intask": "true"
    })
    mutation_block = ET.SubElement(block_valueA, "mutation", {"datatype": "Number"})
    field_value_block = ET.SubElement(block_valueA, "field", {"name": "VAR"})
    field_value_block.text = first_var

    valueB = ET.SubElement(block_value, "value", {"name": "B"})
    block_valueB = ET.SubElement(valueB, "block", {
        "type": "variables_get",
        "id": generate_open_roberta_id(),
        "intask": "true"
    })
    mutation_block = ET.SubElement(block_valueB, "mutation", {"datatype": "Number"})
    field_value_block = ET.SubElement(block_valueB, "field", {"name": "VAR"})
    field_value_block.text = second_var
    
    register_variable(variable_name, "Boolean", f"{first_var} {operator} {second_var}")

def math_var(variables, match_math):
    variable_name = match_math.group(1)
    first_var = match_math.group(2)
    operator = match_math.group(3)
    second_var = match_math.group(4)
    opName = None

    if(operator == '+'):
        opName = "ADD"
    elif(operator == '-'):
        opName = "MINUS"
    elif(operator == '*'):
        opName = "MULTIPLY"
    elif(operator == '/'):
        opName = "DIVIDE"
    elif(operator == '^'):
        opName = "POWER"

    variable_block = ET.SubElement(variables, "block", {
        "type": "robGlobalVariables_declare",    
        "id": generate_open_roberta_id(),
        "intask": "true",
        "deletable": "false"
    })
    mutation = ET.SubElement(variable_block, "mutation", {
        "next": "true",
        "declaration_type": "Number"
    })
    block_type = "math_arithmetic"

    field_var = ET.SubElement(variable_block, "field", {"name": "VAR"})
    field_type_field = ET.SubElement(variable_block, "field", {"name": "TYPE"})
    field_var.text = variable_name
    field_type_field.text = "Number"

    value = ET.SubElement(variable_block, "value", {"name": "VALUE"})
    block_value = ET.SubElement(value, "block", {
        "type": block_type,
        "id": generate_open_roberta_id(),
        "intask": "true"
    })
    field_value = ET.SubElement(block_value, "field", {"name": "OP"})
    field_value.text = opName
    valueA = ET.SubElement(block_value, "value", {"name": "A"})
    block_valueA = ET.SubElement(valueA, "block", {
        "type": "variables_get",
        "id": generate_open_roberta_id(),
        "intask": "true"
    })
    mutation_block = ET.SubElement(block_valueA, "mutation", {"datatype": "Number"})
    field_value_block = ET.SubElement(block_valueA, "field", {"name": "VAR"})
    field_value_block.text = first_var

    valueB = ET.SubElement(block_value, "value", {"name": "B"})
    block_valueB = ET.SubElement(valueB, "block", {
        "type": "variables_get",
        "id": generate_open_roberta_id(),
        "intask": "true"
    })
    mutation_block = ET.SubElement(block_valueB, "mutation", {"datatype": "Number"})
    field_value_block = ET.SubElement(block_valueB, "field", {"name": "VAR"})
    field_value_block.text = second_var
    
    register_variable(variable_name, "Number", f"{first_var} {operator} {second_var}")

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
    AST.append(ActionNode("Move", direction, speed, distance=distance))
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
    AST.append(ActionNode("Turn", direction, speed, degree=degree))
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