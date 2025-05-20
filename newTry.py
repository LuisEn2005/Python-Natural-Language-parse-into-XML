import xml.etree.ElementTree as ET
import json

def parse_open_roberta(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        ns = {"roberta": "http://de.fhg.iais.roberta.blockly"}
        instances = root.findall(".//roberta:instance", ns)

        def process_block(block):
            block_data = {
                "type": block.get("type"),
                "attributes": {
                    attr: block.get(attr) for attr in block.attrib if attr not in ["type", "id"]
                },
                "fields": {},
                "values": [],
                "statements": {},
                "mutation": {},
                "repetitions": []
            }

            # Procesar campos (field)
            for field in block.findall("roberta:field", ns):
                block_data["fields"][field.get("name")] = field.text

            # Procesar valores (value) y bloques anidados
            for value in block.findall("roberta:value", ns):
                name = value.get("name")
                nested_block = value.find("roberta:block", ns)
                if nested_block is not None:
                    block_data["values"].append({
                        "name": name,
                        "block": process_block(nested_block)
                    })

            # Procesar declaraciones (statement)
            for statement in block.findall("roberta:statement", ns):
                name = statement.get("name")
                nested_block = statement.find("roberta:block", ns)
                if nested_block is not None:
                    block_data["statements"][name] = process_block(nested_block)

            # Manejo específico de `robControls_loopForever`
            if block.get("type") == "robControls_loopForever":
                do_statement = block.find("roberta:statement[@name='DO']", ns)
                if do_statement is not None:
                    block_data["statements"]["DO"] = []
                for sub_block in do_statement.findall("roberta:block", ns):
                    block_data["statements"]["DO"].append(process_block(sub_block))
                    
            # Procesar mutaciones
            mutation = block.find("roberta:mutation", ns)
            if mutation is not None:
                block_data["mutation"] = mutation.attrib

            # Procesar repeticiones específicas (IFx y DOx)
            repetitions = block.find("roberta:repetitions", ns)
            if repetitions is not None:
                index = 0
                while True:
                    if_name = f"IF{index}"
                    do_name = f"DO{index}"

                    if_block = repetitions.find(f"roberta:value[@name='{if_name}']/roberta:block", ns)
                    do_block = repetitions.find(f"roberta:statement[@name='{do_name}']/roberta:block", ns)

                    if if_block is None and do_block is None:
                        break

                    repetition_data = {}

                    if if_block is not None:
                        repetition_data["condition"] = process_block(if_block)

                    if do_block is not None:
                        repetition_data["action"] = process_block(do_block)

                    block_data["repetitions"].append(repetition_data)

                    index += 1

            return block_data

        ast = []
        for instance in instances:
            for block in instance.findall("roberta:block", ns):
                ast.append(process_block(block))

        return ast

    except ET.ParseError as e:
        print("Error al analizar el XML:", e)
    except FileNotFoundError:
        print("Archivo no encontrado.")
    return None

# Archivo de ejemplo
ast = parse_open_roberta("NEPOprog2.xml")
if ast:
    output_file = "ast.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ast, f, indent=4, ensure_ascii=False)
    print(f"El AST se ha guardado en el archivo {output_file}.")