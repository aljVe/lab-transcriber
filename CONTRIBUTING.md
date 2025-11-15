# Guía de Contribución

¡Gracias por tu interés en contribuir a Lab Transcriber! Este documento proporciona directrices para contribuir al proyecto.

## 🎯 Formas de Contribuir

### 🐛 Reportar Bugs
- Usa la sección de [Issues](https://github.com/aljVe/lab-transcriber/issues)
- Describe claramente el problema
- Incluye pasos para reproducirlo
- Adjunta ejemplos de PDFs problemáticos (sin datos sensibles)
- Especifica tu versión del programa y sistema operativo

### 💡 Sugerir Mejoras
- Abre un Issue con la etiqueta "enhancement"
- Explica el caso de uso
- Proporciona ejemplos si es posible

### 🏥 Añadir Soporte para Nuevos Hospitales
Si tu hospital usa un formato diferente:
1. Extrae el texto del PDF usando el programa
2. Identifica qué parámetros no se detectan
3. Abre un Issue con ejemplos de formato
4. O mejor aún, añade los aliases necesarios en `config.json` y envía un PR

### 💻 Contribuir Código
1. Fork el repositorio
2. Crea una rama desde `main`: `git checkout -b feature/mi-mejora`
3. Realiza tus cambios
4. Asegúrate de que el código sigue el estilo existente
5. Commit con mensajes descriptivos
6. Push a tu fork y abre un Pull Request

## 📋 Estándares de Código

### Python
- Seguir PEP 8 en lo posible
- Usar type hints cuando sea apropiado
- Documentar funciones complejas
- Mantener compatibilidad con Python 3.8+
- Límite de línea: 120 caracteres (flexible)

### Commits
Formato de mensajes de commit:
```
Tipo: Descripción breve

Descripción más detallada si es necesario.

- Punto específico 1
- Punto específico 2
```

**Tipos:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Ejemplos:**
```
feat: Añadir soporte para unidad nmol/L

fix: Corregir detección de glucosa en formato de Hospital X

docs: Actualizar README con instrucciones de instalación
```

## 🔧 Configuración del Entorno de Desarrollo

### Requisitos
```bash
# 1. Clone el repositorio
git clone https://github.com/aljVe/lab-transcriber.git
cd lab-transcriber

# 2. Cree un entorno virtual
python -m venv venv

# 3. Active el entorno
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# 4. Instale dependencias
pip install -r requirements.txt
```

### Ejecutar desde Código
```bash
python __main__.py
```

### Ejecutar con Debug
```bash
python __main__.py --log-level DEBUG
```

## 📝 Actualizar config.json

Al añadir nuevos parámetros:

### 1. Añade aliases
```json
{
  "aliases": {
    "Nuevo Parámetro": ["NUEVO PARAMETRO", "Alias 1", "Alias 2"]
  }
}
```

### 2. Especifica unidades esperadas
```json
{
  "expected_units": {
    "Nuevo Parámetro": "mg/dl"
  }
}
```

Para múltiples unidades:
```json
{
  "expected_units": {
    "Nuevo Parámetro": ["mg/dl", "g/L", "mmol/L"]
  }
}
```

### 3. Asigna categoría
```json
{
  "category_map": {
    "Bioquímica": [..., "Nuevo Parámetro"]
  }
}
```

### 4. Prueba con PDFs reales
Antes de enviar el PR, prueba con PDFs reales del hospital correspondiente.

## 🐛 Debug y Troubleshooting

### Ubicación de Logs
- **Windows:** `%APPDATA%\LabTranscriber\labtranscriber.log`
- **macOS:** `~/Library/Application Support/LabTranscriber/labtranscriber.log`
- **Linux:** `~/.local/share/LabTranscriber/labtranscriber.log`

### Extraer Texto de PDF para Debug
```python
from extractor import PDFExtractor

e = PDFExtractor('ruta/al/pdf.pdf')
texto = e.extract_text()
print(texto)

# Guardar a archivo
with open('texto_extraido.txt', 'w', encoding='utf-8') as f:
    f.write(texto)
```

### Ver Qué Parámetros se Detectan
Revisa el log después de procesar un PDF. Busca líneas como:
```
INFO - Parseado y VALIDADO Numérico: Glucosa: 94 mg/dl
WARNING - Validación fallida 'Creatinina': Encontrado='None'(None)
```

## 🏗️ Áreas Principales del Código

- **`extractor.py`**: Extracción de texto desde PDFs
- **`parser.py`**: Detección y parsing de parámetros
- **`formatter.py`**: Formateo de resultados
- **`gui.py`**: Interfaz gráfica
- **`config.json`**: Configuración de aliases y unidades

## 📦 Crear un Release

(Solo para mantenedores)

### 1. Actualizar Versión
Cambiar en:
- `LabTranscriber.spec` (nombre del ejecutable)
- `CHANGELOG.md` (nueva sección)
- `README.md` (sección de novedades)
- `README_BUILD.md` (sección de cambios)

### 2. Compilar Ejecutable
```bash
pyinstaller LabTranscriber.spec --clean
```

### 3. Probar
Probar el ejecutable con varios PDFs de diferentes hospitales.

### 4. Crear Tag y Release
```bash
git tag -a v1.3.6 -m "Release v1.3.6: Soporte para indicadores y aliases duplicados"
git push origin v1.3.6
```

Crear Release en GitHub adjuntando:
- Ejecutable `.exe`
- Archivo `config.json`
- Notas de la versión del CHANGELOG

## 🧪 Testing

Aunque actualmente no hay tests automatizados, cuando contribuyas:

1. **Prueba manualmente** con PDFs reales
2. **Verifica** que no se rompa compatibilidad con formatos anteriores
3. **Revisa logs** para asegurarte de que no hay errores

## ❓ Preguntas Frecuentes

### ¿Cómo añado soporte para un nuevo formato de hospital?
1. Extrae el texto exacto del PDF
2. Identifica cómo se llaman los parámetros
3. Añade esos nombres como aliases en `config.json`
4. Añade las unidades que usa ese hospital
5. Prueba y envía un PR

### ¿Qué hago si el PDF no se lee correctamente?
El programa solo funciona con PDFs nativos (texto seleccionable). PDFs escaneados no son compatibles.

### ¿Cómo debug problemas de detección?
1. Activa log level DEBUG
2. Extrae el texto del PDF manualmente (ver sección Debug)
3. Compara con los aliases en `config.json`
4. Revisa los logs para ver qué falla en la validación

## 📜 Código de Conducta

- Sé respetuoso y profesional
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto y los usuarios
- Recuerda que esto es un proyecto para ayudar a profesionales sanitarios

## 📬 Contacto

Si tienes dudas o sugerencias:
- **Issues:** https://github.com/aljVe/lab-transcriber/issues
- **Email:** alejandro2196vr@gmail.com

---

<p align="center">
  ¡Gracias por contribuir a mejorar Lab Transcriber! 🎉
</p>
