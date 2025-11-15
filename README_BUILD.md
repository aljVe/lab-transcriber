# Cómo Generar el Ejecutable .exe

Este documento explica cómo compilar Lab Transcriber en un ejecutable .exe para Windows.

## Versión Actual

**v1.3.6** - Incluye soporte para flechas de indicadores alto/bajo (↑↓)

## Requisitos Previos

- **Windows** (el .exe solo se puede crear desde Windows)
- **Python 3.8 o superior** instalado
- **Git** (para clonar el repositorio)

## Pasos para Generar el Ejecutable

### Opción 1: Usando el Script Automático (Recomendado)

1. **Abre una terminal de Windows** (CMD o PowerShell)

2. **Navega a la carpeta del proyecto**:
   ```cmd
   cd C:\ruta\a\lab-transcriber
   ```

3. **Ejecuta el script de compilación**:
   ```cmd
   build_exe.bat
   ```

4. **Espera** a que termine (puede tardar 2-5 minutos)

5. **Encuentra tu ejecutable** en la carpeta `dist\`:
   ```
   dist\LabTranscriber_v136.exe
   dist\config.json
   ```

### Opción 2: Manualmente

1. **Instala PyInstaller**:
   ```cmd
   pip install pyinstaller
   ```

2. **Instala las dependencias**:
   ```cmd
   pip install -r requirements.txt
   ```

3. **Compila usando el archivo .spec**:
   ```cmd
   pyinstaller LabTranscriber.spec --clean
   ```

4. **Copia config.json a dist/**:
   ```cmd
   copy config.json dist\
   ```

## Resultado

Después de la compilación, en la carpeta `dist\` encontrarás:
- `LabTranscriber_v136.exe` - El ejecutable principal
- `config.json` - Archivo de configuración necesario

## Distribución

Para distribuir el programa:

1. Copia **AMBOS archivos** (`LabTranscriber_v136.exe` y `config.json`) a la misma carpeta
2. Comprime en un archivo .zip si es necesario
3. El ejecutable debe estar siempre en la misma carpeta que `config.json`

## Solución de Problemas

### Error: "No se encuentra config.json"
- Asegúrate de que `config.json` esté en la misma carpeta que el ejecutable

### Error: "PyInstaller no está instalado"
- Ejecuta: `pip install pyinstaller`

### Error: "Python no se reconoce como comando"
- Asegúrate de que Python esté instalado y en el PATH del sistema

### El ejecutable es muy grande
- Es normal. PyInstaller empaqueta Python y todas las dependencias (típicamente 20-40 MB)

## Notas Importantes

- **Solo desde Windows**: No puedes crear un .exe desde Linux o macOS
- **Antivirus**: Algunos antivirus pueden marcar el ejecutable como sospechoso (falso positivo). Esto es común con PyInstaller.
- **Versión**: El ejecutable se llama `LabTranscriber_v136.exe` para reflejar la nueva versión con soporte para flechas

## Cambios en v1.3.6

### Nuevas Características
- ✅ Soporte para flechas de indicadores (↑↓▲▼⬆⬇) en valores de laboratorio
- ✅ Gestión inteligente de aliases duplicados mediante validación de unidades
- ✅ Compatibilidad ampliada con formatos de múltiples hospitales
- ✅ Nuevas unidades: 10E3/µL, 10E6/µL, UI/L, µg/dL, s (segundos)
- ✅ Nuevos aliases para nombres de parámetros en formatos específicos hospitalarios

### Mejoras Técnicas
- Parser más robusto con mejor manejo de Unicode
- Validación de unidades más estricta para evitar detecciones incorrectas
- Resolución automática de ambigüedades (ej: Glucosa sangre vs orina)

Esta versión mejora significativamente la compatibilidad con diferentes formatos de laboratorio.
