import xml.etree.ElementTree as ET
from astProcessing import findVar, generate_action_block, generate_turn_block, get_loop_block, get_if_or_elif_statement
from logger import messages, log_message
from xmlUtils import generate_open_roberta_id

# Crear el elemento raíz con el namespace
namespace = "http://de.fhg.iais.roberta.blockly"
ET.register_namespace('', namespace)
export_tag = ET.Element("export", xmlns=namespace)

# Crear nodos iniciales
program_tag = ET.SubElement(export_tag, "program")
block_set_tag = ET.SubElement(program_tag, "block_set", {
    "xmlns": namespace, "robottype": "edison", "xmlversion": "3.1", "description": "", "tags": ""
})
instance_tag = ET.SubElement(block_set_tag, "instance", { "x": "273", "y": "50" })

curr_parent = instance_tag

block_start_tag = ET.SubElement(instance_tag, "block", {
    "type": "robControls_start", "id": generate_open_roberta_id(), "intask": "true", "deletable": "false"
})
ET.SubElement(block_start_tag, "mutation", {"declare": "false"})
ET.SubElement(block_start_tag, "field", {"name": "DEBUG"}).text = "TRUE"

config_tag = ET.SubElement(export_tag, "config")
block_set_config = ET.SubElement(config_tag, "block_set", {
    "xmlns": namespace, "robottype": "edison", "xmlversion": "3.1", "description": "", "tags": ""
})
instance_config = ET.SubElement(block_set_config, "instance", {"x": "213", "y": "213"})
ET.SubElement(instance_config, "block", {
    "type": "robBrick_Edison-Brick", "id": "1", "intask": "true", "deletable": "false"
})

def get_indent_level(line):
    return len(line) - len(line.lstrip(" "))

state = {
    "current_if_block": None,
    "elif_count": 0
}

parent_stack = [(0, instance_tag)]

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
            return curr_parent

        new_loop_parent = get_loop_block(stripped, curr_parent)
        if new_loop_parent is not None:
            parent_stack.append((indent + 2, new_loop_parent))
            return curr_parent

        if curr_parent != instance_tag and stripped.startswith("var"):
            log_message("ERROR", f"No se permiten declaraciones de variables con indentación: '{line.strip()}'")
            return curr_parent

        generate_action_block(stripped, curr_parent)
        generate_turn_block(stripped, curr_parent)

    except ValueError as e:
        log_message("ERROR", f"Error en línea '{line.strip()}': {e}")
    return curr_parent


with open("Code.txt", "r") as f:
    for line in f:
        findVar(line, block_start_tag)
        curr_parent = process_line(line, curr_parent)

# Mostrar mensajes
if messages:
    print("\nResumen de mensajes:")
    for level, msg in messages:
        print(f"[{level}] {msg}")
    if any(level == "ERROR" for level, _ in messages):
        print("\nSe encontraron errores. El archivo XML podría ser inválido.")
else:
    print("No se encontraron errores ni advertencias.")

# Guardar XML
tree = ET.ElementTree(export_tag)
fileName = "IfsOutput.xml"
with open(fileName, "wb") as file:
    tree.write(file, encoding="utf-8")

print(f"Archivo XML generado: {fileName}")
