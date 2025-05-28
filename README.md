# Lab Transcriber

<p align="center">
  <img src="docs/images/logo.png" alt="Lab Transcriber Logo" width="200"/>
</p>

Una aplicación para extraer y estandarizar valores de parámetros clínicos desde informes de laboratorio en formato PDF. El objetivo es ahorrar tiempo a los profesionales sanitarios, evitándoles transcribir manualmente analíticas.

## Características

- **Extracción automática de datos**: Extrae de forma automática los datos de las analíticas de laboratorio desde archivos PDF nativos, eliminando la necesidad de transcripción manual y minimizando errores.
- **Categorización por sistemas**: Organiza los parámetros extraídos por sistemas (Bioquímica, Hemograma, Perfil férrico, etc.), facilitando la revisión y el análisis de los resultados.
- **Formato estandarizado para historias clínicas**: Presenta los datos en un formato claro y estandarizado, listo para ser incorporado en las historias clínicas electrónicas, mejorando la interoperabilidad y la consistencia de la información.
- **Procesamiento por lotes**: Permite procesar múltiples informes de laboratorio en una sola operación, optimizando el tiempo y el flujo de trabajo de los profesionales sanitarios.
- **Validación de unidades y valores**: Realiza validaciones automáticas de las unidades y los rangos de los valores extraídos, ayudando a identificar posibles errores o inconsistencias en los datos.
- **Detección inteligente de parámetros con fuzzy matching**: Reconoce parámetros incluso si sus nombres en el PDF no coinciden exactamente con los nombres configurados. Esto aumenta la robustez de la extracción de datos y la capacidad de la aplicación para adaptarse a diferentes formatos de informes.

## Requisitos

- Windows/macOS/Linux
- PDFs con texto seleccionable (no compatible con documentos escaneados)

## Instalación

### Opción 1: Ejecutable para Windows (recomendado)

1. Descargue la [última versión](https://github.com/aljVe/lab-transcriber.git/releases) del archivo ZIP.
2. Descomprima el archivo ZIP. El archivo `config.json` necesario para la aplicación se encuentra incluido dentro del ZIP.
3. Asegúrese de que el archivo `config.json` se encuentre en la misma carpeta que el ejecutable.
4. Ejecute `LabTranscriber_v135.exe`.

### Opción 2: Desde código fuente

Esta opción requiere tener Python instalado. La instalación de las dependencias se gestiona mediante `pip` utilizando el archivo `requirements.txt`.
Consulte las [instrucciones de instalación detalladas (`INSTALL.md`)](INSTALL.md) para más información.

## Uso básico

0. **Importante**: Revise y comprenda el archivo `config.json`. Este archivo define los parámetros que la aplicación puede reconocer y cómo se extraen. Asegúrese de que esté configurado correctamente para sus necesidades antes de procesar los informes.
1. Inicie la aplicación.
2. Haga clic en "Seleccionar PDFs" para elegir uno o varios informes de laboratorio.
3. Los resultados se mostrarán en la interfaz en un formato estandarizado, listos para ser revisados.
4. Copie los resultados a su historia clínica o sistema de gestión utilizando el botón "Copiar Resultados".

## Configuración

El archivo `config.json` es crucial para el funcionamiento de Lab Transcriber, ya que define los parámetros que la aplicación puede reconocer y cómo debe procesarlos. Puede editar este archivo (`config.json`) para añadir nuevos parámetros, modificar los existentes o ajustar los criterios de búsqueda.

La estructura básica del `config.json` consiste en una lista de objetos, donde cada objeto representa un parámetro clínico. Cada parámetro tiene los siguientes atributos principales:

-   `"nombre"`: El nombre principal y estandarizado del parámetro que se usará en los resultados.
-   `"alias"`: Una lista de nombres alternativos o abreviaturas que pueden aparecer en los informes PDF (por ejemplo, "Hematíes", "Hties", "Eritrocitos"). La aplicación utilizará estos alias para encontrar el parámetro en el texto del PDF.
-   `"categoria"`: La categoría a la que pertenece el parámetro (por ejemplo, "Hemograma", "Bioquímica", "Perfil Férrico").
-   `"unidades"`: Las unidades esperadas para el valor del parámetro (por ejemplo, "mg/dL", "10^3/uL", "%").

A continuación, se muestra un pequeño ejemplo de la estructura de un parámetro dentro de `config.json`:

```json
[
  {
    "nombre": "Glucosa Basal",
    "alias": ["Glucosa", "GLU", "Glucemia en ayunas"],
    "categoria": "Bioquímica",
    "unidades": "mg/dL"
  },
  {
    "nombre": "Hematocrito",
    "alias": ["HCT", "Hematocrito", "Hto"],
    "categoria": "Hemograma",
    "unidades": "%"
  }
  // ... más parámetros
]
```

**Nota importante:** Después de modificar el archivo `config.json`, es necesario reiniciar la aplicación Lab Transcriber para que los cambios surtan efecto.

## Contribuciones

¡Las contribuciones de la comunidad son bienvenidas y muy apreciadas! Si tienes ideas para mejorar Lab Transcriber, nuevas características que te gustaría ver, o has encontrado algún error, no dudes en colaborar.

El proceso general para contribuir es:

1.  Haz un "fork" del repositorio.
2.  Crea una nueva rama para tus cambios (`git checkout -b feature/nueva-caracteristica`).
3.  Realiza tus modificaciones y haz "commit" de ellas (`git commit -am 'Añade nueva característica'`).
4.  Sube tus cambios a tu "fork" (`git push origin feature/nueva-caracteristica`).
5.  Abre un "Pull Request" para que tus cambios puedan ser revisados e integrados.

Para pautas más detalladas sobre cómo contribuir, incluyendo estándares de código y el proceso de revisión, por favor consulta nuestro archivo [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [`LICENSE`](LICENSE) para más detalles.

## Autor

Creado por Alejandro Venegas Robles. Para dudas o sugerencias contactar con alejandro2196vr@gmail.com
