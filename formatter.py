# lab_transcriber/formatter.py (v1.2.3 - Ordenando por línea)
from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

OUTPUT_ORDER = [
    "Bioquímica", "Hemograma", "Perfil férrico", "Hemostasia",
    "Inmunología", "Serologías", "Otros"
]

def format_summary(parsed_data: dict) -> str:
    """Formatea los datos parseados, ordenando por línea de aparición."""
    # Estructura esperada de parsed_data:
    # { Categoria: { StdName: (FormattedValue_with_Marker, LineIndex) } }
    if not parsed_data:
        return "No se encontraron parámetros reconocibles."

    summary_parts: list[str] = ["AS:"]
    processed_categories = set()

    for category in OUTPUT_ORDER:
        # Obtener los items de la categoría si existe
        items_in_category = parsed_data.get(category)
        if items_in_category: # Verificar que no sea None o vacío
            try:
                # Ordenar los items (StdName, (FormattedValue, LineIndex)) por LineIndex
                # item[0] es StdName, item[1] es la tupla (FormattedValue, LineIndex)
                # item[1][1] es LineIndex
                sorted_items_by_line = sorted(items_in_category.items(), key=lambda item: item[1][1])

                # Extraer solo los FormattedValue ya ordenados
                sorted_formatted_values = [item[1][0] for item in sorted_items_by_line]

                if sorted_formatted_values: # Solo añadir si hay items tras ordenar
                    items_string = "; ".join(sorted_formatted_values)
                    summary_parts.append(f"    • {category}: {items_string}.")
                    processed_categories.add(category)
                    logger.info(f"Formateada categoría: {category} con {len(sorted_formatted_values)} items (orden PDF).")
            except Exception as e:
                logger.error(f"Error al formatear/ordenar categoría '{category}': {e}", exc_info=True)
                summary_parts.append(f"    • {category}: [Error al formatear]")

    # Añadir categorías no listadas (ordenadas por línea también)
    for category, items_dict in parsed_data.items():
        if category not in processed_categories and items_dict:
            logger.warning(f"Categoría '{category}' no en OUTPUT_ORDER. Añadiendo al final.")
            try:
                items_with_lines = items_dict.items()
                sorted_items_by_line = sorted(items_with_lines, key=lambda item: item[1][1])
                sorted_formatted_values = [item[1][0] for item in sorted_items_by_line]
                if sorted_formatted_values:
                    items_string = "; ".join(sorted_formatted_values)
                    summary_parts.append(f"    • {category}: {items_string}.")
            except Exception as e:
                 logger.error(f"Error al formatear/ordenar categoría adicional '{category}': {e}", exc_info=True)
                 summary_parts.append(f"    • {category}: [Error al formatear]")

    if len(summary_parts) == 1:
        logger.warning("No se encontraron resultados para formatear.")
        return "AS:\n    No se encontraron resultados procesables."

    return "\n".join(summary_parts)