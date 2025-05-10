# Lab Transcriber

<p align="center">
  <img src="docs/images/logo.png" alt="Lab Transcriber Logo" width="200"/>
</p>

Una aplicación para extraer y estandarizar valores de parámetros clínicos desde informes de laboratorio en formato PDF. El objetivo es ahorrar tiempo a los profesionales sanitarios, evitándoles transcribir manualmente analíticas.

## Características

- Extracción automática de datos de analíticas de laboratorio desde PDFs nativos
- Categorización por sistemas: Bioquímica, Hemograma, Perfil férrico, etc.
- Formato estandarizado para historias clínicas
- Procesamiento por lotes de múltiples archivos
- Validación de unidades y valores
- Detección inteligente de parámetros con fuzzy matching

## Requisitos

- Windows/macOS/Linux
- PDFs con texto seleccionable (no compatible con documentos escaneados)

## Instalación

### Opción 1: Ejecutable para Windows (recomendado)

1. Descargue la [última versión](https://github.com/aljVe/lab-transcriber.git/releases)
2. Descomprima el archivo
3. Asegúrese de que el archivo `config.json` se encuentre en la misma carpeta que el ejecutable
4. Ejecute `LabTranscriber_v135.exe`

### Opción 2: Desde código fuente

Consulte [instrucciones de instalación](INSTALL.md) para más detalles.

## Uso básico

1. Inicie la aplicación
2. Haga clic en "Seleccionar PDFs" para elegir uno o varios informes de laboratorio
3. Los resultados se mostrarán en formato estandarizado
4. Copie los resultados a su historia clínica con el botón "Copiar Resultados"

## Configuración

El archivo `config.json` contiene la configuración de parámetros reconocibles y sus alias. Puede editarlo para añadir nuevos parámetros o modificar los existentes.

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

Creado por Alejandro Venegas Robles. Para dudas o sugerencias contactar con alejandro2196vr@gmail.com
