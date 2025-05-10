# Instrucciones de Instalación

## Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación desde código fuente

### Windows

1. Clone el repositorio git clone https://github.com/aljVe/lab-transcriber.git
cd lab-transcriber

2. Cree un entorno virtual
python -m venv venv
.\venv\Scripts\activate

3. Instale las dependencias
pip install -r requirements.txt

4. Ejecute la aplicación
python main.py

### macOS/Linux

1. Clone el repositorio
git clone https://github.com/aljVe/lab-transcriber.git
cd lab-transcriber

2. Cree un entorno virtual
python3 -m venv venv
source venv/bin/activate

3. Instale las dependencias
pip install -r requirements.txt

4. Ejecute la aplicación
python main.py

## Crear ejecutable

Si desea crear su propio ejecutable:

### Windows
pip install pyinstaller
pyinstaller --onefile --windowed main.py --name "LabTranscriber_v135"

El ejecutable se creará en la carpeta `dist`. Recuerde copiar el archivo `config.json` junto al ejecutable.

### macOS
pip install pyinstaller
pyinstaller --onefile --windowed main.py --name "LabTranscriber_v135"

## Problemas comunes

### Error: No se encontró config.json

Asegúrese de que el archivo `config.json` se encuentre en la misma carpeta que el ejecutable o el script principal.

### Error: El programa no reconoce parámetros en PDFs escaneados

La aplicación solo funciona con PDFs nativos (con texto seleccionable), no con documentos escaneados.