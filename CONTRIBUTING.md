# Guía de contribución

¡Gracias por su interés en contribuir a Lab Transcriber! Esta guía le ayudará a configurar el entorno de desarrollo y a seguir las pautas del proyecto.

## Entorno de desarrollo

1. Clone el repositorio
git clone https://github.com/aljVe/lab-transcriber.git
cd lab-transcriber

2. Cree un entorno virtual
python -m venv venv
En Windows
.\venv\Scripts\activate
En macOS/Linux
source venv/bin/activate

3. Instale las dependencias de desarrollo
pip install -r requirements-dev.txt

## Flujo de trabajo

1. Cree una rama para su función o corrección
git checkout -b feature/nombre-de-la-funcion

2. Realice sus cambios siguiendo las convenciones de código

3. Ejecute pruebas
pytest

4. Envíe un Pull Request con una descripción clara de los cambios

## Convenciones de código

- Siga PEP 8 para el estilo de código Python
- Escriba docstrings para todas las funciones y clases
- Mantenga un límite de línea de 100 caracteres
- Use nombres descriptivos en español para variables y funciones

## Áreas para contribuir

- Mejorar el reconocimiento de parámetros
- Añadir soporte para nuevos formatos de laboratorio
- Optimizar rendimiento
- Mejorar interfaz de usuario
- Documentación y ejemplos

## Pruebas

Todas las contribuciones deben incluir pruebas cuando sea apropiado. Usamos pytest para las pruebas unitarias.
pytest

## Informes de errores

Si encuentra un error, verifique primero si ya existe un informe. De lo contrario, cree un nuevo Issue con:

- Descripción clara del problema
- Pasos para reproducirlo
- Información del sistema (OS, versión de Python)
- Archivos de ejemplo (si es posible)