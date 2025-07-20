import xml.etree.ElementTree as ET
from astProcessing import findVar, generate_action_block, generate_turn_block, get_loop_block, get_if_or_elif_statement #, visualize_ast
from symbolTable import validate_variable_usage
from xmlUtils import generate_open_roberta_id

# Crear el elemento raíz con el namespace
namespace = "http://de.fhg.iais.roberta.blockly"
ET.register_namespace('', namespace)  # Registrar el namespace
export_tag = ET.Element("export", xmlns=namespace)

# Crear el nodo 'program'
program_tag = ET.SubElement(export_tag, "program")

# Crear 'block_set' dentro de 'program'
block_set_tag = ET.SubElement(program_tag, "block_set", {
    "xmlns": namespace,
    "robottype": "edison",
    "xmlversion": "3.1",
    "description": "",
    "tags": ""
})

# Crear 'instance' dentro de 'block_set' (program)
instance_tag = ET.SubElement(block_set_tag, "instance", {
    "x": "273",
    "y": "50"
})

curr_parent = instance_tag

# Agregar un bloque a la instancia
block_start_tag = ET.SubElement(instance_tag, "block", {
    "type": "robControls_start",
    "id": generate_open_roberta_id(),
    "intask": "true",
    "deletable": "false"
})
mutation = ET.SubElement(block_start_tag, "mutation", {"declare": "false"})
field_debug = ET.SubElement(block_start_tag, "field", {"name": "DEBUG"})
field_debug.text = "TRUE"

# Crear 'config'
config_tag = ET.SubElement(export_tag, "config")

# Crear 'block_set' dentro de 'config'
block_set_config = ET.SubElement(config_tag, "block_set", {
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

def get_indent_level(line):
    return len(line) - len(line.lstrip(" "))

state = {
    "current_if_block": None,
    "elif_count": 0
}

parent_stack = [(0, instance_tag,)]

def process_line(line, curr_parent):    
    global parent_stack

    indent = get_indent_level(line)
    stripped = line.strip()

    while parent_stack and indent < parent_stack[-1][0]:
        parent_stack.pop()

    curr_parent = parent_stack[-1][1]
    try:
        if_statement = get_if_or_elif_statement(stripped, curr_parent, state)
        if if_statement is not None:
            parent_stack.append((indent + 2, if_statement))
            return
        
        # loop
        new_loop_parent = get_loop_block(stripped, curr_parent)
        if new_loop_parent is not None:
            parent_stack.append((indent + 2, new_loop_parent))
            return
        
        if curr_parent != instance_tag and stripped.startswith("var"):
            raise ValueError("No se permiten declaraciones de variables al indentar.")
        
        generate_action_block(stripped, curr_parent)
        generate_turn_block(stripped, curr_parent)

    except ValueError as e:
        print(f"Error en línea '{line.strip()}': {e}")

while True:
    line = f.readline()
    if(len(line) == 0):
        break
    findVar(line, block_start_tag)
    curr_parent = process_line(line, curr_parent)


#visualize_ast(output_file="AST_output")

f.close()

# Escribir el árbol XML a un archivo sin la declaración
tree = ET.ElementTree(export_tag)
fileName = str("IfsOutput.xml")
with open(fileName, "wb") as file:
    tree.write(file, encoding="utf-8")  # No se incluye xml_declaration=True

print(f"Archivo XML generado sin declaración: {fileName}")
