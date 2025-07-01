import xml.etree.ElementTree as ET
from astProcessing import findVar, generate_action_block, generate_turn_block
from symbolTable import validate_variable_usage
from xmlUtils import generate_open_roberta_id

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

def process_line(line):
    try:
        findVar(line, block_start, variables_declared)
        generate_action_block(line, instance_program)
        generate_turn_block(line, instance_program)
    except ValueError as e:
        print(f"Error en línea '{line.strip()}': {e}")

while True:
    line = f.readline()
    if(len(line) == 0):
        break
    process_line(line)
    
f.close()

# Escribir el árbol XML a un archivo sin la declaración
tree = ET.ElementTree(root)
with open("Salida.xml", "wb") as file:
    tree.write(file, encoding="utf-8")  # No se incluye xml_declaration=True

print("Archivo XML generado sin declaración: Salida.xml")
