# 🛠️ Simulador de Compilador Educativo - Open Roberta + Python

Este proyecto presenta el diseño e implementación de un compilador educativo desarrollado en Python. Su propósito es interpretar programas visuales en formato XML generados por la plataforma **Open Roberta**, convirtiéndolos en estructuras intermedias que facilitan la comprensión del proceso de compilación.

## 📚 Descripción

El sistema permite:
- Leer archivos XML exportados desde Open Roberta.
- Analizar bloques visuales como sensores, acciones robóticas y estructuras de control.
- Generar un árbol de sintaxis abstracta (**AST**) estructurado en formato JSON.
- Ayudar a estudiantes a entender cómo los bloques se transforman en estructuras de datos formales.

## 🎯 Objetivos del Proyecto

- Diseñar un analizador de archivos XML basados en Open Roberta.
- Representar visualmente la estructura lógica del código.
- Sentar las bases para la futura generación automática de pseudocódigo o código Python.

## 🧰 Tecnologías Utilizadas

- **Python 3.10+**
- `xml.etree.ElementTree` para el análisis de XML.
- **Open Roberta** como plataforma de origen.
- Representación de AST en **JSON**.

## 📦 Estructura del Proyecto
│
├── main.py # Script principal del compilador
├── parser/
│ ├── init.py
│ ├── xml_reader.py # Lector y analizador de archivos XML
│ └── ast_generator.py # Generador del AST
├── examples/
│ ├── programa1.xml # Archivos XML de ejemplo
│ └── programa2.xml
├── output/
│ └── ast_programa1.json # Resultados del AST
└── README.md

## ▶️ Ejecución del Proyecto

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/simulador-compilador.git
   cd simulador-compilador

