# Lab Transcriber

<p align="center">
  <img src="docs/images/logo.png" alt="Lab Transcriber Logo" width="200"/>
</p>

<p align="center">
  <strong>Extracción automática e inteligente de analíticas de laboratorio desde PDFs</strong>
</p>

<p align="center">
  <a href="#características">Características</a> •
  <a href="#instalación">Instalación</a> •
  <a href="#uso">Uso</a> •
  <a href="#configuración">Configuración</a> •
  <a href="CHANGELOG.md">Changelog</a>
</p>

---

## 🎯 Descripción

Lab Transcriber es una aplicación diseñada para **automatizar la transcripción de analíticas de laboratorio** desde informes en PDF a formato estandarizado para historias clínicas electrónicas.

Ahorra tiempo valioso a los profesionales sanitarios eliminando la necesidad de copiar manualmente decenas de valores de cada analítica.

## ✨ Características

### 🔍 Detección Inteligente
- **Fuzzy matching** para reconocer parámetros con variaciones ortográficas
- **Validación automática de unidades** para distinguir parámetros ambiguos (ej: Glucosa en sangre vs orina)
- **Soporte para múltiples formatos** de hospitales y laboratorios
- **Ignorar indicadores visuales** (flechas ↑↓ de valores altos/bajos)

### 📊 Categorización Automática
- Bioquímica general
- Hemograma completo
- Perfil férrico
- Hemostasia y coagulación
- Gasometría arterial
- Análisis de orina
- Y más...

### ⚡ Productividad
- **Procesamiento por lotes** de múltiples PDFs simultáneamente
- **Copia al portapapeles** con un solo clic
- **Ordenación** según aparición en el PDF original
- Interfaz gráfica intuitiva

### 🔧 Personalizable
- Configuración externa mediante `config.json`
- Añadir nuevos parámetros y aliases fácilmente
- Adaptar unidades y formatos según necesidades locales

## 📋 Requisitos

- **Sistema Operativo:** Windows 10/11, macOS, o Linux
- **PDFs:** Con texto seleccionable (no escaneados como imagen)
- **Memoria:** 100 MB libres

## 🚀 Instalación

### Opción 1: Ejecutable para Windows (Recomendado)

1. **Descargue** la [última versión](https://github.com/aljVe/lab-transcriber/releases) (LabTranscriber_v136.exe)
2. **Descomprima** el archivo ZIP
3. **Verifique** que `config.json` esté en la misma carpeta que el ejecutable
4. **Ejecute** `LabTranscriber_v136.exe`

> **Nota:** Algunos antivirus pueden marcar el ejecutable como sospechoso (falso positivo común con PyInstaller). Es seguro añadirlo a la lista de excepciones.

### Opción 2: Desde Código Fuente

Consulte las [instrucciones de instalación detalladas](INSTALL.md) para ejecutar desde Python o compilar su propio ejecutable.

## 💻 Uso

### Uso Básico

1. **Inicie** la aplicación haciendo doble clic en el ejecutable
2. **Seleccione** uno o varios PDFs con el botón "Seleccionar PDFs"
3. **Revise** los resultados extraídos en la ventana de resultados
4. **Copie** al portapapeles con "Copiar Resultados"
5. **Pegue** en su historia clínica electrónica

### Consejos

- Los parámetros detectados por fuzzy matching se marcan con `[~]`
- Si un parámetro no se detecta, verifique que el PDF tenga texto seleccionable
- Puede procesar múltiples PDFs a la vez para mayor eficiencia

## ⚙️ Configuración

El archivo `config.json` controla qué parámetros se reconocen y cómo se procesan:

```json
{
  "aliases": {
    "Glucosa": ["Glucosa basal", "Glucosa", "GLUCOSA"],
    "Hemoglobina": ["HEMOGLOBINA", "Hemoglobina", "Hb", "Hgb"]
  },
  "expected_units": {
    "Glucosa": "mg/dl",
    "Hemoglobina": "g/dl"
  }
}
```

### Personalización

- **Añadir nuevos parámetros:** Agregue entradas en `aliases` y `expected_units`
- **Adaptar a su hospital:** Añada los nombres específicos que usa su laboratorio
- **Unidades alternativas:** Especifique lista de unidades aceptadas: `["mg/dl", "g/L"]`

## 📝 Novedades v1.3.6

✅ **Soporte para indicadores alto/bajo** (flechas ↑↓)
✅ **Resolución inteligente de aliases duplicados** mediante validación de unidades
✅ **Compatibilidad ampliada** con formatos de más hospitales
✅ **Nuevas unidades:** 10E3/µL, 10E6/µL, UI/L, µg/dL

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo de cambios.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Cree una rama para su feature (`git checkout -b feature/AmazingFeature`)
3. Commit sus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abra un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Alejandro Venegas Robles**

- Email: alejandro2196vr@gmail.com
- GitHub: [@aljVe](https://github.com/aljVe)

---

<p align="center">
  Hecho con ❤️ para profesionales sanitarios
</p>
