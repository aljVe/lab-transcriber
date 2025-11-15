# Changelog

Todas las modificaciones notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.6] - 2025-01-15

### Añadido
- **Soporte para indicadores visuales**: Las flechas (↑↓▲▼⬆⬇) que indican valores altos/bajos ahora se ignoran correctamente durante el análisis
- **Nuevas unidades de medida**:
  - `10E3/µL` y `10E6/µL` para parámetros hematológicos
  - `UI/L` como variante de `U/L`
  - `µg/dL` para hierro y otros micronutrientes
  - `s` (segundos) para tiempos de coagulación
- **Nuevos aliases para compatibilidad hospitalaria**:
  - `ASPARTATO` para AST (nombres en múltiples líneas)
  - `ALANINA` para ALT (nombres en múltiples líneas)
  - `GAMMA GLUTAMILTRANSFERASA` para Gamma GT
  - `FILTRADO GLOMERULAR ESTIMADO CKD-EPI` para filtrado glomerular
  - `FOSFATO INORGANICO` para fósforo
  - `PROTEINA C REACTIVA (us)` para PCR ultrasensible
  - Variantes completas para VCM, HCM, CHCM, ADE
- **Gestión inteligente de aliases duplicados**:
  - Soporte para aliases que apuntan a múltiples parámetros (ej: "Glucosa" → Glucosa sangre vs Glucosa orina)
  - Selección automática del parámetro correcto mediante validación de unidades
  - Previene confusiones entre parámetros de sangre y orina

### Mejorado
- **Robustez del parser**: Mejor manejo de caracteres Unicode (flechas, símbolos especiales)
- **Validación de unidades**: Sistema más estricto para distinguir parámetros ambiguos
- **Compatibilidad multi-hospital**: Soporte para formatos de más laboratorios y hospitales

### Corregido
- Error en detección de parámetros cuando las flechas aparecen entre valor y unidad
- Problema con aliases duplicados causando detección incorrecta de parámetros
- Fallos de encoding al guardar texto con caracteres Unicode especiales

## [1.3.5] - 2025-05-10

### Añadido
- Texto actualizado en la pestaña de instrucciones
- Firma actualizada en la interfaz

### Eliminado
- Funcionalidad de diagnóstico eliminada de la interfaz

## [1.2.3] - 2025-04-29

### Añadido
- Ordenación de resultados según aparición en el PDF original

### Corregido
- Problemas con la detección de unidades en ciertos formatos

## [1.2.2] - 2025-04-27

### Añadido
- Funcionalidad de diagnóstico para depurar detección
- Firma del desarrollador

### Corregido
- Varios errores menores en la interfaz

## [1.1] - 2025-04-27

### Añadido
- Soporte para procesamiento por lotes

### Mejorado
- Rendimiento en análisis de PDFs extensos

## [1.0] - 2025-04-27

### Añadido
- Lanzamiento inicial
- Interfaz gráfica básica
- Extracción de parámetros de laboratorio
- Configuración externa mediante config.json