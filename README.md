# 🛠️ Procesamiento de Lenguaje Natural a XML - Open Roberta + Python

Este proyecto presenta el diseño e implementación de un conversor de comandos en español a instrucciones XML para Open Roberta siendo desarrollado en Python. Su propósito es interpretar programas visuales en formato XML generados por la plataforma **Open Roberta**, convirtiéndolos en estructuras intermedias que facilitan la comprensión del proceso de compilación.

## 📚 Descripción

El sistema permite:
- Leer archivos de texto con python.
- Analizar variables, instrucciones y condiciones escritas en lenguaje natural humano.
- Generar un archivo XML para ver en Open Roberta.
- Ayudar a estudiantes a entender cómo los bloques se transforman en estructuras de datos formales.

## 🎯 Objetivos del Proyecto

- Diseñar una alternativa para generar código que pueda interpretar Open Roberta Lab.
- Representar visualmente la estructura lógica del código.
- Sentar la habilidad y potencial que merece el código de Python.

## 🧰 Tecnologías Utilizadas

- **Python 3.10+**
- `xml.etree.ElementTree` para la creación de archivos de XML.
- **Open Roberta** como plataforma de origen.
- **REGEX** para aplicar patrones de Expresiones Regulares

- Proyecto: Transformador de Lenguaje Natural a XML para Open Roberta
│
├── Code.txt             # Archivo de entrada con instrucciones en lenguaje natural
├── README.md            # Documentación del proyecto
│
├── Xmlmaker.py          # Script principal: genera el archivo XML final
├── astProcessing.py     # Procesa instrucciones y construye nodos XML
├── symbolTable.py       # Maneja la tabla de símbolos y validación de variables
├── xmlUtils.py          # Funciones auxiliares (IDs únicos, helpers XML)
├── xml a dict.py        # Conversión experimental de XML a diccionario Python


