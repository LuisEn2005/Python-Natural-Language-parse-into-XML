import xml.etree.ElementTree as ET
from astProcessing import findVar, generate_action_block, generate_turn_block, get_loop_block#, visualize_ast
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

def process_line(line, curr_parent):
    stripped = line.strip()

    try:
        new_loop_parent = get_loop_block(stripped, instance_tag)
        if new_loop_parent is not None:
            return new_loop_parent

        if line.startswith("  "):
            if curr_parent != instance_tag and stripped.startswith("var"):
                raise ValueError("No se permiten declaraciones de variables dentro de un bucle.")
            generate_action_block(stripped, curr_parent)
            generate_turn_block(stripped, curr_parent)
            return curr_parent
        
        findVar(line, block_start_tag)
        generate_action_block(line, instance_tag)
        generate_turn_block(line, instance_tag)
        return instance_tag
    except ValueError as e:
        print(f"Error en línea '{line.strip()}': {e}")

while True:
    line = f.readline()
    if(len(line) == 0):
        break
    curr_parent = process_line(line, curr_parent)

#visualize_ast(output_file="AST_output")

f.close()

# Escribir el árbol XML a un archivo sin la declaración
tree = ET.ElementTree(export_tag)
fileName = str("BucleOutput.xml")
with open(fileName, "wb") as file:
    tree.write(file, encoding="utf-8")  # No se incluye xml_declaration=True

print(f"Archivo XML generado sin declaración: {fileName}")
