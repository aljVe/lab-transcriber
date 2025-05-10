# lab_transcriber/extractor.py (v0.5 - Sin cambios)
from __future__ import annotations
from pathlib import Path
import logging

try:
    import pdfplumber
except ImportError:
    logging.critical("La biblioteca 'pdfplumber' es necesaria y no se encontró.")
    pdfplumber = None

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extrae texto nativo (seleccionable) de archivos PDF usando pdfplumber."""
    def __init__(self, path: str | Path):
        if pdfplumber is None:
            raise ImportError("La biblioteca 'pdfplumber' es necesaria y no está instalada/disponible.")
        self.path = Path(path)
        if not self.path.exists():
            logger.error(f"Archivo no encontrado: {self.path}")
            raise FileNotFoundError(f"El archivo especificado no existe: {self.path}")
        logger.info(f"Extractor (solo texto nativo) inicializado para: {self.path}")

    def extract_text(self) -> str:
        """Extrae el texto nativo completo del PDF."""
        extracted_pages: list[str] = []
        try:
            with pdfplumber.open(self.path) as pdf:
                if not pdf.pages:
                    logger.warning(f"El PDF '{self.path.name}' no contiene páginas o está vacío.")
                    return ""
                logger.info(f"Procesando {len(pdf.pages)} páginas de '{self.path.name}' con pdfplumber...")
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text(x_tolerance=2, y_tolerance=2, layout=False)
                    if page_text:
                        extracted_pages.append(page_text)
                    else:
                        logger.debug(f"Página {i+1} no devolvió texto.")
                full_text = "\n".join(extracted_pages)
                if not full_text.strip():
                     logger.warning(f"No se extrajo texto significativo de '{self.path.name}'. ¿Es un PDF de solo imágenes?")
                     return ""
                logger.info(f"Texto extraído nativamente ({len(full_text)} caracteres).")
                return full_text
        except Exception as e:
            logger.error(f"Error durante la extracción de texto nativo con pdfplumber: {e}", exc_info=True)
            raise RuntimeError(f"No se pudo leer el contenido del PDF. ¿Está dañado o protegido? (Error: {e})")