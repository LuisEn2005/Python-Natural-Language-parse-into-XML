try:
    import xmltodict
except ImportError:
    print("La biblioteca 'xmltodict' no está instalada. Instálala con 'pip install xmltodict'.")
    exit()

import json

def xml_to_json(xml_file_path, json_file_path):
    try:
        # Leer el archivo XML
        with open(xml_file_path, 'r') as xml_file:
            xml_data = xml_file.read()

        # Convertir XML a un diccionario
        dict_data = xmltodict.parse(xml_data)

        # Convertir diccionario a JSON
        json_data = json.dumps(dict_data, indent=4)

        # Guardar el JSON en un archivo
        with open(json_file_path, 'w') as json_file:
            json_file.write(json_data)

        print(f"Archivo convertido y guardado como: {json_file_path}")
    except Exception as e:
        print(f"Error durante la conversión: {e}")

# Llamar a la función
xml_to_json('NEPOprog2.xml', 'archivo.json')
