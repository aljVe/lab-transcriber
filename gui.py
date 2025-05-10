# lab_transcriber/gui.py (v1.2.3 - Eliminada funcionalidad diagnóstico y texto actualizado)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import logging
import pyperclip
import os
import json
from datetime import datetime
from pathlib import Path

try:
    from .extractor import PDFExtractor
    # FIX: Importar fuzzy_match_parameter 
    from .parser import parse_report_text, get_unrecognized_lines, analyze_detection_success, fuzzy_match_parameter, CONFIG_FILENAME
    from .formatter import format_summary
except ImportError:
    from extractor import PDFExtractor
    # FIX: Importar fuzzy_match_parameter
    from parser import parse_report_text, get_unrecognized_lines, analyze_detection_success, fuzzy_match_parameter, CONFIG_FILENAME
    from formatter import format_summary

logger = logging.getLogger(__name__)
DATA_DIR = Path(os.path.expanduser("~")) / "lab_transcriber_data"
os.makedirs(DATA_DIR, exist_ok=True)

INSTRUCTIONS = """**Lab Transcriber v1.2.2 - Guía Rápida**

1. El programa extrae datos de analíticas desde PDFs NATIVOS (no escaneados).
2. Asegúrese de que el archivo config.json esté en la misma carpeta que el ejecutable.
3. Pulse "Seleccionar PDFs" para elegir uno o varios informes de analíticas.
4. Los resultados se mostrarán en formato estandarizado.
5. Use "Copiar Resultados" para transferirlos a su historial clínico.

IMPORTANTE: Solo procesa PDFs con texto seleccionable, NO funciona con PDFs escaneados."""

class LabTranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Lab Transcriber v1.2.2 (Config: {CONFIG_FILENAME})") # Título actualizado
        self.root.geometry("850x680") # Aumentar un poco la altura para la firma
        self.status_text = tk.StringVar()
        self.status_text.set(f"Carga {CONFIG_FILENAME} y selecciona PDFs.")
        self.last_raw_text = None; self.last_parsed_data = None; self.last_filepath = None
        style = ttk.Style(); style.theme_use('clam')
        self.notebook = ttk.Notebook(root)
        # --- Pestaña Principal ---
        self.main_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.main_frame, text='Procesar Analíticas')
        self.top_frame = ttk.Frame(self.main_frame); self.top_frame.pack(pady=5, padx=5, fill=tk.X)
        self.select_button = ttk.Button(self.top_frame, text="Seleccionar PDFs", command=self.select_pdfs_and_process)
        self.select_button.pack(side=tk.LEFT, padx=5)
        self.file_count_label = ttk.Label(self.top_frame, text="Archivos: 0", relief=tk.SUNKEN, width=15)
        self.file_count_label.pack(side=tk.LEFT, padx=5)
        self.reload_config_button = ttk.Button(self.top_frame, text="Recargar Config", command=self.reload_config_action)
        self.reload_config_button.pack(side=tk.LEFT, padx=5)
        self.results_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=25, state=tk.DISABLED, font=("Consolas", 9))
        self.results_area.configure(bg='light grey'); self.results_area.pack(pady=10, padx=5, expand=True, fill=tk.BOTH)
        self.bottom_frame = ttk.Frame(self.main_frame); self.bottom_frame.pack(pady=5, padx=5, fill=tk.X)
        self.copy_button = ttk.Button(self.bottom_frame, text="Copiar Resultados", command=self.copy_to_clipboard, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(self.bottom_frame, textvariable=self.status_text, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # --- Pestaña Instrucciones ---
        self.instructions_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.instructions_frame, text='Instrucciones')
        self.instructions_text_area = scrolledtext.ScrolledText(self.instructions_frame, wrap=tk.WORD, height=25, state=tk.NORMAL, font=("Calibri", 10))
        self.instructions_text_area.insert(tk.END, INSTRUCTIONS); self.instructions_text_area.configure(state=tk.DISABLED, bg='light grey')
        self.instructions_text_area.pack(padx=5, pady=5, expand=True, fill=tk.BOTH)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # --- Firma ---
        signature_text = "Creado por Alejandro Venegas Robles. Para dudas o sugerencias contactar con alejandro2196vr@gmail.com"
        self.signature_label = ttk.Label(self.root, text=signature_text, anchor=tk.E, font=("Calibri", 8))
        self.signature_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))


    def reload_config_action(self):
        try:
            import importlib
            # Asumiendo que los módulos están en un paquete llamado 'lab_transcriber'
            # Si están en el mismo directorio, usa 'import parser as parser_module'
            # e 'importlib.reload(parser_module)'
            try:
                import lab_transcriber.parser as parser_module
            except ImportError: # Fallback si se ejecuta como script individual
                import parser as parser_module

            importlib.reload(parser_module)
            if parser_module.CONFIG and parser_module.CONFIG.get("aliases"):
                self.status_text.set(f"Config '{parser_module.CONFIG_FILENAME}' recargada.")
                messagebox.showinfo("Config Recargada", f"Recargado desde\n{parser_module.config_path}", parent=self.root)
                logger.info("Configuración recargada manualmente.")
            else: raise ValueError("Archivo config vacío o no cargado.")
        except Exception as e:
            logger.error(f"Error recargando config: {e}", exc_info=True)
            messagebox.showerror("Error Config", f"No se pudo recargar '{CONFIG_FILENAME}':\n{e}", parent=self.root)
            self.status_text.set("Error al recargar config.")

    def select_pdfs_and_process(self):
        filepaths = filedialog.askopenfilenames(title='Selecciona PDFs', filetypes=(('PDF', '*.pdf'), ('Todo', '*.*')))
        if not filepaths: self.status_text.set("Cancelado."); self.file_count_label.config(text="Archivos: 0"); return
        total_files = len(filepaths); self.file_count_label.config(text=f"Archivos: {total_files}")
        self.status_text.set(f"Iniciando para {total_files} archivos..."); self.results_area.configure(state=tk.NORMAL, bg='yellow')
        self.results_area.delete('1.0', tk.END); self.copy_button.configure(state=tk.DISABLED)
        self.root.update_idletasks()
        success_count = 0; error_count = 0; results_available = False

        for i, filepath in enumerate(filepaths):
            filename = os.path.basename(filepath)
            self.status_text.set(f"Procesando {i+1}/{total_files}: {filename}...")
            separator = f"\n{'*' * 10} INICIO: {filename} {'*' * 10}\n\n"
            self.results_area.insert(tk.END, separator); self.root.update_idletasks()
            try:
                logger.info(f"[{i+1}/{total_files}] Procesando: {filepath}")
                extractor = PDFExtractor(filepath); raw_text = extractor.extract_text()
                if not raw_text or not raw_text.strip(): raise ValueError("No se extrajo texto.")
                logger.info(f"[{i+1}/{total_files}] Parseando..."); parsed_data = parse_report_text(raw_text)
                self.last_raw_text = raw_text; self.last_parsed_data = parsed_data; self.last_filepath = filepath
                logger.info(f"[{i+1}/{total_files}] Formateando..."); summary = format_summary(parsed_data)
                self.results_area.insert(tk.END, summary); success_count += 1; results_available = True
            except Exception as e:
                error_msg = f"Error {filename}: {type(e).__name__}: {e}"
                logger.error(error_msg, exc_info=isinstance(e, (ValueError, RuntimeError))) # Log simple para file not found
                self.results_area.insert(tk.END, f"*** ERROR: {error_msg} ***"); error_count += 1
            finally:
                self.results_area.insert(tk.END, f"\n\n{'*' * 10} FIN: {filename} {'*' * 10}\n"); self.results_area.see(tk.END)

        final_status = f"Completado. {success_count}/{total_files} OK."; final_bg_color = 'white'
        if error_count > 0: final_status += f" {error_count} con errores."; final_bg_color = 'pink'
        self.status_text.set(final_status); self.results_area.configure(state=tk.DISABLED, bg=final_bg_color)
        if results_available: self.copy_button.configure(state=tk.NORMAL)
        if error_count > 0: messagebox.showwarning("Errores", f"{final_status}\nRevisa resultados.", parent=self.root)
        else: messagebox.showinfo("Éxito", f"{final_status}", parent=self.root)

    def copy_to_clipboard(self):
        results_content = self.results_area.get('1.0', tk.END).strip()
        if results_content:
            try: pyperclip.copy(results_content); self.status_text.set("Resultados copiados.")
            except Exception as clip_err: logger.error(f"Error copia: {clip_err}", exc_info=True); self.status_text.set("Error copia."); messagebox.showwarning("Error Copia", "No se pudo copiar.\nSelecciona manualmente.", parent=self.root)
        else: self.status_text.set("Nada que copiar.")

def launch_gui_tkinter():
    root = tk.Tk()
    app = LabTranscriberApp(root)
    root.mainloop()