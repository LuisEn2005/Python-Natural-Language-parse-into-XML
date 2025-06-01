import xml.etree.ElementTree as ET
import random
import string
import re

def generate_open_roberta_id(length=20):
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:',.<>?/"
    return ''.join(random.choice(characters) for _ in range(length))

def findVar(line):
    global variables_declared  # Accede a la variable global
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
        
        elif variable_value == "[]":
            mutation = ET.SubElement(variable_block, "mutation", {
                "next": "true",
                "declaration_type": "Array_Number"
            })
            field_type = "Array_Number"
            block_type = "robLists_create_with"
            field_name = "LIST_TYPE"

        else:
            # Manejo de valores desconocidos como cadenas de texto
            mutation = ET.SubElement(variable_block, "mutation", {
                "next": "true",
                "list_type": "Number"
            })
            field_type = "String"
            block_type = "text"
            field_name = "TEXT"

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



# Crear el elemento raíz con el namespace
namespace = "http://de.fhg.iais.roberta.blockly"
ET.register_namespace('', namespace)  # Registrar el namespace
root = ET.Element("export", xmlns=namespace)

# Crear el nodo 'program'
program = ET.SubElement(root, "program")

# Crear 'block_set' dentro de 'program'
block_set_program = ET.SubElement(program, "block_set", {
    "xmlns": namespace,
    "robottype": "edison",
    "xmlversion": "3.1",
    "description": "",
    "tags": ""
})

# Crear 'instance' dentro de 'block_set' (program)
instance_program = ET.SubElement(block_set_program, "instance", {
    "x": "273",
    "y": "50"
})

# Agregar un bloque a la instancia
block_start = ET.SubElement(instance_program, "block", {
    "type": "robControls_start",
    "id": generate_open_roberta_id(),
    "intask": "true",
    "deletable": "false"

})

# Agregar los elementos secundarios del bloque
variables_declared = False
mutation = ET.SubElement(block_start, "mutation", {"declare": "false"})
field_debug = ET.SubElement(block_start, "field", {"name": "DEBUG"})
field_debug.text = "TRUE"

# Crear 'config'
config = ET.SubElement(root, "config")

# Crear 'block_set' dentro de 'config'
block_set_config = ET.SubElement(config, "block_set", {
    "xmlns": namespace,
    "robottype": "edison",
    "xmlversion": "3.1",
    "description": "",
    "tags": ""
})

# Crear 'instance' dentro de 'block_set' (config)
instance_config = ET.SubElement(block_set_config, "instance", {
    "x": "213",
    "y": "213"
})

# Agregar un bloque de configuración a la instancia
block_brick = ET.SubElement(instance_config, "block", {
    "type": "robBrick_Edison-Brick",
    "id": "1",
    "intask": "true",
    "deletable": "false"
})

f = open("Code.txt", "r")

while True:
    line = f.readline()
    if(len(line) == 0):
        break
    findVar(line)
f.close()

# Escribir el árbol XML a un archivo sin la declaración
tree = ET.ElementTree(root)
with open("Salida.xml", "wb") as file:
    tree.write(file, encoding="utf-8")  # No se incluye xml_declaration=True

print("Archivo XML generado sin declaración: Salida.xml")
