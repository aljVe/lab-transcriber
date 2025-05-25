# lab_transcriber/__main__.py (v1.2.3 - Eliminada funcionalidad diagnóstico)
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import logging
import os

# --- Configuración Directorio Datos y Logging ---
APP_NAME = "LabTranscriber"
try:
    if sys.platform == "win32": data_dir_base = Path(os.environ['APPDATA']) / APP_NAME
    elif sys.platform == "darwin": data_dir_base = Path.home() / "Library" / "Application Support" / APP_NAME
    else: data_dir_base = Path.home() / ".local" / "share" / APP_NAME
    DATA_DIR = data_dir_base
except Exception: DATA_DIR = Path.home() / f".{APP_NAME.lower()}_data"

try:
    os.makedirs(DATA_DIR, exist_ok=True)
    LOG_FILE = DATA_DIR / f"{APP_NAME.lower()}.log"
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1*1024*1024, backupCount=5, encoding='utf-8')
    stream_handler = logging.StreamHandler()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s [%(name)s:%(lineno)d] %(message)s', datefmt='%H:%M:%S', handlers=[file_handler, stream_handler])
except Exception as log_e:
     print(f"Error config logging: {log_e}", file=sys.stderr); logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

logger = logging.getLogger(__name__)
logger.info(f"Directorio datos/logs: {DATA_DIR}")

# --- Importaciones ---
try:
    from extractor import PDFExtractor as Extractor
    from parser import parse_report_text as Parser, get_unrecognized_lines, analyze_detection_success, CONFIG_FILENAME, config_path as PARSER_CONFIG_PATH
    from formatter import format_summary as Formatter
    from gui import launch_gui_tkinter as GuiLauncher
    logger.info("Importaciones directas completadas.")
except ImportError as e:
    logger.critical(f"Error import módulos: {e}", exc_info=True)
    print(f"Error fatal: {e}", file=sys.stderr)
    sys.exit(1)

# --- Funciones CLI y Main ---
def run_cli(pdf_path: Path):
    logger.info(f"CLI para: {pdf_path}")
    if not PARSER_CONFIG_PATH: print(f"Error: No se encontró {CONFIG_FILENAME}", file=sys.stderr); return 1
    try:
        extractor = Extractor(pdf_path); raw_text = extractor.extract_text()
        if not raw_text or not raw_text.strip(): print("\nError: No texto.", file=sys.stderr); return 1
        parsed_data = Parser(raw_text); summary = Formatter(parsed_data)
        print("\n--- Resumen Analítica (v1.2.3) ---"); print(summary); print("-" * 30)
        logger.info("CLI completada."); return 0
    except Exception as e: print(f"\nError CLI: {e}", file=sys.stderr); logger.error("Error CLI", exc_info=True); return 1

def main() -> int:
    cli_description = f"""Transcribe informes analíticos PDF. v1.2.3
Usa config externa ({CONFIG_FILENAME}), validación de unidades y fuzzy matching.
GUI permite lotes. NO LEE PDFs ESCANEADOS.
    """
    parser = argparse.ArgumentParser(description=cli_description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf_path", nargs="?", type=Path, help="Ruta PDF (solo modo CLI).")
    parser.add_argument("--gui", action="store_true", help="Forzar modo GUI.")
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Nivel logs.')
    args = parser.parse_args()

    log_level_numeric = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level_numeric)
    logger.info(f"Nivel logging: {args.log_level.upper()}")
    logger.info(f"Lab Transcriber v1.2.3 (Config: {CONFIG_FILENAME}) iniciado")

    # Verificar que se encontró config.json antes de continuar
    if not PARSER_CONFIG_PATH:
         message = f"¡ERROR CRÍTICO! No se encontró el archivo de configuración '{CONFIG_FILENAME}'.\nAsegúrate de que esté en la misma carpeta que el ejecutable o dentro de 'lab_transcriber' si ejecutas desde código."
         print(message, file=sys.stderr)
         # Intentar mostrarlo también en un popup si es posible (útil para .exe)
         try:
             import tkinter as tk; from tkinter import messagebox
             root = tk.Tk(); root.withdraw(); messagebox.showerror("Error de Configuración", message); root.destroy()
         except: pass
         return 1

    if args.gui or args.pdf_path is None:
        logger.info("Iniciando modo GUI...")
        try:
            try: import pyperclip; import tkinter; from tkinter import ttk
            except ImportError as gui_dep_err: logger.critical(f"Falta dep GUI: {gui_dep_err}.", exc_info=True); print(f"Error: {gui_dep_err}", file=sys.stderr); return 1
            GuiLauncher()
        except Exception as e: logger.critical("Error GUI", exc_info=True); print(f"Error GUI: {e}", file=sys.stderr); return 1
    else:
        pdf_file = Path(args.pdf_path)
        if not pdf_file.is_file(): print(f"Error: PDF no encontrado: {pdf_file}", file=sys.stderr); logger.error(f"PDF no válido CLI: {pdf_file}"); return 1
        return run_cli(pdf_file)
    return 0

if __name__ == "__main__":
    sys.exit(main())