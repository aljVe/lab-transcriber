# lab_transcriber/parser.py (v1.2.3 - Guardando línea para ordenar)
from __future__ import annotations
import re
import unicodedata
import logging
import json
import os
import sys
from difflib import SequenceMatcher
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

# --- Funciones Auxiliares ---
def _normalize(text: str) -> str:
    if not isinstance(text, str): return ""
    s = unicodedata.normalize("NFKC", text.strip().lower())
    return " ".join(s.split())

# --- Carga de Configuración ---
CONFIG_FILENAME = "config.json"
def find_config_path() -> Path | None:
    if getattr(sys, 'frozen', False): application_path = Path(sys.executable).parent
    else: application_path = Path(__file__).parent
    config_path = application_path / CONFIG_FILENAME
    if config_path.is_file(): return config_path
    parent_path = application_path.parent / CONFIG_FILENAME
    if parent_path.is_file(): return parent_path
    cwd_path = Path.cwd() / CONFIG_FILENAME
    if cwd_path.is_file(): logger.warning(f"Usando config.json desde directorio actual: {Path.cwd()}"); return cwd_path
    logger.error(f"No se encuentra '{CONFIG_FILENAME}' cerca de {application_path}, su padre, o el directorio actual.")
    return None

def load_config(config_path: Path) -> dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as f: config = json.load(f)
        logger.info(f"Configuración cargada desde: {config_path}")
        if not all(k in config for k in ["aliases", "category_map", "expected_units"]): raise ValueError("Config incompleta.")
        return config
    except Exception as e:
        logger.critical(f"Error cargando config desde '{config_path}': {e}", exc_info=True)
        return {"aliases": {}, "category_map": {}, "expected_units": {}}

config_path = find_config_path()
CONFIG = load_config(config_path) if config_path else {"aliases": {}, "category_map": {}, "expected_units": {}}
PARAM_ALIASES = CONFIG.get("aliases", {})
CATEGORY_MAP = CONFIG.get("category_map", {})
EXPECTED_UNITS_OR_TYPES = CONFIG.get("expected_units", {})
param_to_category_map: dict[str, str] = { std: cat for cat, stds in CATEGORY_MAP.items() for std in stds }
alias_to_std_name_map: dict[str, str] = {}
for std_name, alias_list in PARAM_ALIASES.items():
    if not isinstance(alias_list, list): logger.warning(f"Valor para alias '{std_name}' no es lista."); continue
    for alias in alias_list:
        normalized_alias = _normalize(alias)
        if normalized_alias in alias_to_std_name_map: logger.warning(f"Alias duplicado '{normalized_alias}' (apunta a '{std_name}').")
        alias_to_std_name_map[normalized_alias] = std_name
sorted_normalized_aliases = sorted(alias_to_std_name_map.keys(), key=len, reverse=True)

# --- Constantes y Regex ---
ABS_UNITS = {"x10³/mm³"}
UNIT_CLEAN: dict[str, str] = {
    "mg/dL": "mg/dl", "mg/dl": "mg/dl", "g/dL": "g/dl", "g/dl": "g/dl", "g/L": "g/L",
    "U/L": "U/L", "u/l": "U/L", "KU/L": "KU/L", "UI/ML": "UI/mL", "UI/ml": "UI/mL",
    "mmol/L": "mmol/L", "mmol/l": "mmol/L", "mmol/mol": "mmol/mol",
    "mL/min/1.73m2": "ml/min/1.73m²", "mL/min/1.73m^2": "ml/min/1.73m²",
    "mL/min/1,73m2": "ml/min/1.73m²", "ml/min/1.73m2": "ml/min/1.73m²",
    "mL/min/1.73m²":"ml/min/1.73m²", "mL/min/":"ml/min/1.73m²",
    "ng/mL": "ng/ml", "ng/ml": "ng/ml", "ng/dl": "ng/dl", "ng/L": "ng/L",
    "pg/mL": "pg/ml", "pg/ml": "pg/ml", "mU/L": "mU/L", "mU/l": "mU/L",
    "μg/L": "mcg/L", "µg/L": "mcg/L", "mcg/L": "mcg/L",
    "μg/dl": "mcg/dl", "µg/dl": "mcg/dl", "mcg/dl": "mcg/dl",
    "microg/dl": "mcg/dl", "microgr/dl":"mcg/dl",
    "fl": "fL", "pg": "pg", "mm":"mm", "segundos":"seg",
    "mil/mm3": "x10³/mm³", "mill/mm3": "x10³/mm³",
    "mil/mm": "x10³/mm³", "mill/mm": "x10³/mm³",
    "mil/": "x10³/mm³", "mill/": "x10³/mm³", "%": "%",
}
RE_VALUE_UNIT = re.compile(
    r"(?P<sign>[><]?)\s*"r"(?P<value>[\d]+(?:[.,]\d+)?)\s*"
    r"(?:(?P<percent>%)|(?P<unit>[a-zA-Zμmcgµg/]+(?:[ \t]*[a-zA-Zμmcgµg%/²³\^]+)*\b))?"
)
RE_SEROLOGY = re.compile(r"\b(POSITIVO|NEGATIVO|DUDOSO)\b", re.IGNORECASE)
RE_ORINA_CUALITATIVO = re.compile(r"\b(negativo|\+{1,4}|escasa|moderada|abundante|normal|positivo)\b", re.IGNORECASE)
# Añade cualquier otro término específico que usen, como "trazas", "indicios", etc.
# "positivo" se añade por si acaso, aunque "+" es más común.

# --- Funciones de Parsing (Continuación) ---
def fuzzy_match_parameter(text: str, threshold=0.75) -> str | None:
    cleaned_text = _normalize(re.sub(r'[:\d.,<>()\[\]~]', ' ', text))
    if not cleaned_text: return None
    best_match_std = None; best_score = threshold
    for norm_alias, std_name in alias_to_std_name_map.items():
         if len(norm_alias) > 2:
             score = SequenceMatcher(None, cleaned_text, norm_alias).ratio()
             if score >= best_score: best_score = score; best_match_std = std_name
    if best_match_std: logger.debug(f"Fuzzy: '{text[:30]}...' -> '{best_match_std}' (Score: {best_score:.2f})")
    return best_match_std

def extract_value_and_unit(line_part: str) -> tuple[str | None, str | None, str | None, str | None]:
    match = RE_VALUE_UNIT.search(line_part)
    if match:
        sign = match.group("sign") or ""; value = match.group("value").replace(',', '.')
        unit_percent = match.group("percent"); unit_other_raw = match.group("unit")
        found_unit_cleaned = None; current_unit_type = None
        if unit_percent: found_unit_cleaned = "%"; current_unit_type = "%"
        elif unit_other_raw:
            cleaned = UNIT_CLEAN.get(unit_other_raw.strip(), unit_other_raw.strip())
            found_unit_cleaned = cleaned
            if cleaned == "%": current_unit_type = "%"
            elif cleaned in ABS_UNITS: current_unit_type = 'abs'
            else: current_unit_type = 'other'
        else: current_unit_type = None
        return sign, value, found_unit_cleaned, current_unit_type
    return None, None, None, None

def validate_unit(param_std: str, found_unit: str | None, unit_type: str | None) -> bool:
    expected = EXPECTED_UNITS_OR_TYPES.get(param_std)
    valid = False
    if expected == "status_orina_cualitativo":
        # Para parámetros de orina cualitativos, validamos que el tipo sea el correcto
        # y que el valor encontrado sea uno de los esperados
        valid = (unit_type == "status_orina_cualitativo" and 
                found_unit is not None and 
                RE_ORINA_CUALITATIVO.match(found_unit) is not None)
    elif isinstance(expected, (list, tuple)):
        valid = found_unit in expected
    elif expected == 'abs' and unit_type == 'abs':
        valid = True
    elif expected == '%' and unit_type == '%':
        valid = True
    elif expected == 'status' and unit_type == 'status':
        valid = True
    elif expected == 'other' and unit_type == 'other':
        valid = True
    elif expected == found_unit:
        valid = True  # Incluye None == None
    elif expected is None and unit_type is None:
        valid = True

    if not valid:
        logger.warning(f"Validación fallida '{param_std}': Encontrado='{found_unit}'({unit_type}), Esperado='{expected}'")
    return valid

def parse_report_text(raw_text: str) -> dict:
    """Analiza texto, validando unidades y guardando línea para orden."""
    # Guardar { Categoria: { StdName: (FormattedValue, UnitType, DetectionMethod, LineIndex) } }
    results_intermediate: dict = defaultdict(lambda: defaultdict(tuple))
    processed_lines: set[int] = set()
    lines = raw_text.splitlines()
    unrecognized_lines_with_values: list[tuple[int, str]] = []

    logger.info("Iniciando Pasada 1: Detección Exacta + Validación...")
    for i, line in enumerate(lines):
        if i in processed_lines:
            continue
        normalized_line = _normalize(line.strip())
        if not normalized_line:
            continue

        best_match_for_line = None
        found_by_exact = False

        for norm_alias in sorted_normalized_aliases:
            try:
                start_index = normalized_line.find(norm_alias)
                if start_index != -1:
                    # 1. Recopilar todos los param_std que pueden usar este `norm_alias`
                    candidate_params = []
                    for p_std, alias_list_cfg in PARAM_ALIASES.items():
                        for alias_cfg in alias_list_cfg:
                            if _normalize(alias_cfg) == norm_alias:
                                candidate_params.append(p_std)
                                break  # Ya encontramos que este p_std usa el norm_alias

                    found_match_for_this_alias_on_line = False
                    for param_candidate_std in candidate_params:
                        category = param_to_category_map.get(param_candidate_std)
                        if not category:
                            continue
                        
                        # Evitar sobreescribir un parámetro ya parseado y validado para esta categoría
                        if param_candidate_std in results_intermediate[category]:
                            continue

                        expected_unit_config = EXPECTED_UNITS_OR_TYPES.get(param_candidate_std)
                        
                        # Intentar extraer valor (considerando la línea actual y la siguiente)
                        value_info_tuple = None  # (formatted_value, actual_value_line_idx)
                        text_to_search_value = line[start_index + len(norm_alias):]  # Parte de la línea actual
                        potential_next_line_idx = i + 1
                        next_line_text = lines[potential_next_line_idx] if potential_next_line_idx < len(lines) else ""

                        # Intento 1: Cualitativo de Orina (si el param_candidate_std lo espera)
                        if expected_unit_config == "status_orina_cualitativo":
                            match_qual = RE_ORINA_CUALITATIVO.search(text_to_search_value)
                            value_line_for_match = i
                            if not match_qual and next_line_text:  # Intentar en la siguiente línea
                                # Solo si la línea siguiente es corta y no parece otro parámetro
                                if len(_normalize(next_line_text).split()) < 4: 
                                    match_qual = RE_ORINA_CUALITATIVO.search(next_line_text)
                                    value_line_for_match = potential_next_line_idx if match_qual else i
                            
                            if match_qual and match_qual.start() < 20:  # Umbral de proximidad
                                qual_value = match_qual.group(1).lower()
                                if validate_unit(param_candidate_std, qual_value, "status_orina_cualitativo"):
                                    value_info_tuple = (f"{param_candidate_std}: {qual_value}", value_line_for_match)

                        # Intento 2: Numérico (si el param_candidate_std lo espera y no se encontró cualitativo)
                        elif value_info_tuple is None and isinstance(expected_unit_config, (str, list)) and expected_unit_config != "status_orina_cualitativo":
                            sign, val_str, unit_clean, u_type = extract_value_and_unit(text_to_search_value)
                            value_line_for_num_match = i
                            is_on_current_line = True

                            if val_str is None and next_line_text:  # Intentar en la siguiente línea
                                if len(_normalize(next_line_text).split()) < 4 or RE_VALUE_UNIT.fullmatch(next_line_text.strip()):
                                    sign, val_str, unit_clean, u_type = extract_value_and_unit(next_line_text)
                                    value_line_for_num_match = potential_next_line_idx if val_str is not None else i
                                    is_on_current_line = False if val_str is not None else True
                            
                            if val_str is not None:
                                # Verificar proximidad si está en la línea actual
                                proximity_check_ok = True
                                if is_on_current_line:
                                    match_num_prox = RE_VALUE_UNIT.search(text_to_search_value)
                                    if not (match_num_prox and match_num_prox.start() < 30):  # Umbral
                                        proximity_check_ok = False

                                if proximity_check_ok and validate_unit(param_candidate_std, unit_clean, u_type):
                                    formatted_val = f"{param_candidate_std}: {sign}{val_str}"
                                    if unit_clean:
                                        formatted_val += f" {unit_clean}"
                                    value_info_tuple = (formatted_val, value_line_for_num_match)
                        
                        if value_info_tuple:
                            formatted_value, actual_value_line_idx = value_info_tuple
                            logger.info(f"Parseado (Desambiguado): {formatted_value} para '{param_candidate_std}' (Línea Alias: {i+1}, Línea Valor: {actual_value_line_idx+1})")
                            results_intermediate[category][param_candidate_std] = (formatted_value, "exact", actual_value_line_idx)
                            processed_lines.add(i)
                            if actual_value_line_idx != i:
                                processed_lines.add(actual_value_line_idx)
                            
                            found_match_for_this_alias_on_line = True
                            break  # Salir del bucle de `param_candidate_std`

                    if found_match_for_this_alias_on_line:
                        break  # Salir del bucle de `sorted_normalized_aliases`

            except Exception as e:
                logger.error(f"Error procesando alias '{norm_alias}' línea {i+1}: {e}", exc_info=True)
                continue

        if not best_match_for_line:
            if i not in processed_lines and RE_VALUE_UNIT.search(line):
                unrecognized_lines_with_values.append((i, line))
            continue

    # --- Formatear salida final (preparando para formatter) ---
    final_results_for_formatter = defaultdict(dict)
    unique_params_count = 0
    for category, items in results_intermediate.items():
        for std_name, (formatted_value, detection_method, line_idx) in items.items():
            if formatted_value:
                display_value = formatted_value + " [~]" if detection_method == "fuzzy" else formatted_value
                # Asegurar % final
                expected_type_for_std = EXPECTED_UNITS_OR_TYPES.get(std_name)
                if expected_type_for_std == '%' and not display_value.replace(' [~]', '').endswith('%'):
                    parts = display_value.split(":", 1)
                    val_part = parts[1].replace('[~]', '').strip().split(" ")[0]
                    display_value = f"{std_name}: {val_part} %{' [~]' if detection_method == 'fuzzy' else ''}"

                final_results_for_formatter[category][std_name] = (display_value, line_idx)
                unique_params_count += 1

    logger.info(f"Parseo finalizado. {unique_params_count} parámetros únicos para formatear.")
    return dict(final_results_for_formatter)

# --- Funciones de Diagnóstico ---
# (get_unrecognized_lines y analyze_detection_success se mantienen igual que v1.2.2)
def get_unrecognized_lines(raw_text: str) -> list[str]:
    unrecognized = []; value_pattern = re.compile(r'\d'); min_length = 5
    all_alias_patterns = set()
    local_aliases = CONFIG.get("aliases", {})
    for alias_list in local_aliases.values():
        for alias in alias_list: all_alias_patterns.add(r'\b' + re.escape(_normalize(alias)) + r'\b')
    for line in raw_text.splitlines():
        line_strip = line.strip()
        if not line_strip or len(line_strip) < min_length: continue
        if value_pattern.search(line_strip):
            normalized_line = _normalize(line_strip); is_recognized = False
            for pattern in all_alias_patterns:
                if re.search(pattern, normalized_line, re.IGNORECASE): is_recognized = True; break
            if not is_recognized: unrecognized.append(line_strip)
    return unrecognized

def analyze_detection_success(raw_text: str, parsed_data: dict) -> dict:
    lines_with_numbers = 0; value_pattern = re.compile(r'\d+[.,]?\d*'); potential_param_lines = []
    processed_final_values = set();
    # parsed_data ahora es { Categoria: { StdName: (FormattedValue, LineIndex) } }
    # Extraer solo FormattedValue para la comprobación
    for category_data in parsed_data.values():
        for formatted_value_tuple in category_data.values():
            processed_final_values.add(formatted_value_tuple[0].replace(" [~]", ""))

    for line in raw_text.splitlines():
        line_strip = line.strip();
        if not line_strip: continue
        if value_pattern.search(line_strip):
            lines_with_numbers += 1; recognized_in_line = False
            for final_val in processed_final_values:
                 match_final = re.search(r':\s*[><]?(\d+(?:[.,]\d+)?)', final_val)
                 if match_final:
                      num_str_final = match_final.group(1).replace(',', '.')
                      # Usar \b para palabra completa en la búsqueda del número
                      if re.search(r'\b' + re.escape(num_str_final) + r'\b', line_strip.replace(',', '.')):
                           recognized_in_line = True; break
            if not recognized_in_line and not re.match(r'\s*[\d\s-]+$', line_strip):
                potential_param = fuzzy_match_parameter(line_strip, threshold=0.65)
                potential_param_lines.append({"line": line_strip, "potential_param": potential_param})

    detected_count = sum(len(v) for v in parsed_data.values())
    detection_rate = detected_count / lines_with_numbers if lines_with_numbers > 0 else 0
    # Devolver un dict plano con los valores formateados para diagnóstico
    detected_params_flat = {}
    for cat, params in parsed_data.items():
        for name, (val_str, _) in params.items():
            detected_params_flat[f"{cat}_{name}"] = val_str

    return {"total_lines_with_values": lines_with_numbers,
            "detected_params_count": detected_count, # Cambiar nombre de clave
            "detected_params_summary": detected_params_flat, # Pasar dict plano
            "detection_rate": detection_rate,
            "potential_missed_params": potential_param_lines}