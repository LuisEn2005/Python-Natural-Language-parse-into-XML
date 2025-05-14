import xml.etree.ElementTree as ET
import tkinter
import ast

def safe_find(element, path, namespaces):
    try:
        return element.find(path, namespaces)
    except AttributeError:
        return None

def extract_numeric_value(block, value_name, namespaces):
    value_field = safe_find(block, f"./ns:value[@name='{value_name}']", namespaces)
    if value_field is not None:
        num_field = value_field.find(".//ns:field[@name='NUM']", namespaces)
        return num_field.text if num_field is not None else "N/A"
    return "N/A"

def robSensors(block, tipo, namespaces):
    if(tipo == 'infrared_getSample'):
        mode_field = safe_find(block, "./ns:field[@name='MODE']", namespaces)
        mode_value = mode_field.text if mode_field is not None else "N/A"
        print(f"[Sensor] Modo: {mode_value}")

        sensorport_field = safe_find(block, "./ns:field[@name='SENSORPORT']", namespaces)
        sensorport_value = sensorport_field.text if sensorport_field is not None else "N/A"
        print(f"[Sensor] Puerto: {sensorport_value}")

        slot_field = safe_find(block, "./ns:field[@name='SLOT']", namespaces)
        slot_value = slot_field.text if slot_field is not None else "N/A"
        print(f"[Sensor] Ranura: {slot_value}")

        mutation = safe_find(block, "./ns:mutation", namespaces)
        mode_attribute = mutation.attrib.get("mode") if mutation is not None else "N/A"
        print(f"[Sensor] Modo (atributo): {mode_attribute}")


def robControls(block, tipo, namespaces):
    if(tipo == 'start'):
        debug_field = safe_find(block, "./ns:statement[@name='DO']", namespaces)
        debug_value = debug_field.text if debug_field is not None else "N/A"
        print(f"DEBUG: {debug_value}")
        
    elif(tipo == 'loopForever'):
        statement_field = safe_find(block, "./ns:statement[@name='DO']", namespaces)
        if statement_field is not None:
            print("[LoopForever] Bloque contiene acciones en 'DO'")
        else:
            print("[LoopForever] No se encontraron acciones en 'DO'")
    elif(tipo == 'if'):
        condition_field = safe_find(block, "./ns:value[@name='IF0']", namespaces)
        statement_field = safe_find(block, "./ns:statement[@name='DO']", namespaces)
        if condition_field is not None:
            print("[If] Condición encontrada para evaluar")
        else:
            print("[If] No se encontró condición en 'IF0'")

            
def robActions(block, tipo, namespaces):
    if(tipo == 'motorDiff_on_for'):
        direction_field = safe_find(block, "./ns:field[@name='DIRECTION']", namespaces)
        direction_value = direction_field.text if direction_field is not None else "N/A"
        print(f"[Motor] Direccion: {direction_value}")
        power_value = safe_find(block, "./ns:value[@name='POWER']", namespaces)
        if power_value is not None:
            #num_field = power_value.find(".//ns:field[@name='NUM']", namespaces)
            power = extract_numeric_value(block, "POWER", namespaces)
            print(f"[Motor] Potencia: {power}")

        distance_field = safe_find(block, "./ns:value[@name='DISTANCE']", namespaces)
        if distance_field is not None:
            #num_field = distance_field.find(".//ns:field[@name='NUM']", namespaces)
            distance = extract_numeric_value(block,"DISTANCE", namespaces)
            print(f"[Motor] Distancia: {distance}")
    if(tipo == 'motorDiff_on_stop'):
        print("[Motor] Detener motores. Acción ejecutada.")

def process_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    namespace = root.tag.split('}')[0].strip('{')
    namespaces = {'ns': namespace}

    blocks = root.findall(".//ns:block", namespaces)

    for block in blocks:
        block_type = block.attrib.get("type")
        #print(f"tipo de bloque: {block_type}")
        if(block_type.startswith("robControls_")):
            control = block_type.split("_",1)[1]
            robControls(block, control, namespaces)
        if(block_type.startswith("robActions_")):
            action = block_type.split("_",1)[1]
            robActions(block, action, namespaces)
        if(block_type.startswith("robSensors_")):
            sensor = block_type.split("_",1)[1]
            robSensors(block, sensor, namespaces)


process_xml("./NEPOprog.xml")