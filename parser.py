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
    if isinstance(expected, (list, tuple)): valid = found_unit in expected
    elif expected == 'abs' and unit_type == 'abs': valid = True
    elif expected == '%' and unit_type == '%': valid = True
    elif expected == 'status' and unit_type == 'status': valid = True
    elif expected == 'other' and unit_type == 'other': valid = True
    elif expected == found_unit: valid = True # Incluye None == None
    elif expected is None and unit_type is None: valid = True

    if not valid: logger.warning(f"Validación fallida '{param_std}': Encontrado='{found_unit}'({unit_type}), Esperado='{expected}'")
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
        if i in processed_lines: continue
        normalized_line = _normalize(line.strip())
        if not normalized_line: continue

        best_match_for_line = None; found_by_exact = False

        for norm_alias in sorted_normalized_aliases:
            try:
                start_index = normalized_line.find(norm_alias)
                if start_index != -1:
                    end_index = start_index + len(norm_alias)
                    is_whole = (start_index == 0 or normalized_line[start_index-1].isspace()) and \
                               (end_index == len(normalized_line) or normalized_line[end_index].isspace() or \
                                normalized_line[end_index].isdigit() or normalized_line[end_index] in '<>')
                    if is_whole:
                        param_std = alias_to_std_name_map[norm_alias]
                        category = param_to_category_map.get(param_std)
                        if not category: continue
                        line_remainder = line[start_index + len(norm_alias):].strip()
                        temp_value_match = None; temp_search_line_idx = -1

                        if category == "Serologías":
                            serology_match = RE_SEROLOGY.search(line_remainder)
                            if serology_match and serology_match.start() < 15: temp_value_match = serology_match; temp_search_line_idx = i
                            elif i + 1 < len(lines) and (i+1) not in processed_lines:
                                 serology_match_next = RE_SEROLOGY.search(lines[i+1])
                                 if serology_match_next and len(lines[i+1].strip()) < 20: temp_value_match = serology_match_next; temp_search_line_idx = i + 1
                        else:
                            numeric_match = RE_VALUE_UNIT.search(line_remainder)
                            if numeric_match and numeric_match.start() < 10: temp_value_match = numeric_match; temp_search_line_idx = i
                            elif i + 1 < len(lines) and (i+1) not in processed_lines:
                                numeric_match_next = RE_VALUE_UNIT.match(lines[i+1].strip())
                                if numeric_match_next: temp_value_match = numeric_match_next; temp_search_line_idx = i + 1

                        if temp_value_match:
                            best_match_for_line = (param_std, temp_value_match, temp_search_line_idx, line_remainder)
                            logger.debug(f"Candidato Exacto línea {i+1}: '{norm_alias}'->'{param_std}' valor línea {temp_search_line_idx+1}")
                            break
            except Exception as e: logger.error(f"Error procesando alias '{norm_alias}' línea {i+1}: {e}", exc_info=True); continue

        if not best_match_for_line:
            if i not in processed_lines and RE_VALUE_UNIT.search(line): unrecognized_lines_with_values.append((i, line))
            continue

        param_std, value_match, search_line_idx, line_remainder_orig = best_match_for_line
        if search_line_idx in processed_lines: continue

        category = param_to_category_map[param_std]
        existing_data = results_intermediate[category].get(param_std)
        current_value_str = None; current_unit_type = None; unit_final_formatted = None; valid_unit_found = False

        if category == "Serologías":
            status = value_match.group(1).lower()
            current_value_str = f"{param_std}: {status}"
            current_unit_type = "status"
            if validate_unit(param_std, None, current_unit_type):
                valid_unit_found = True
                logger.info(f"Parseado Serología: {current_value_str} (Línea {search_line_idx+1})")
        else:
            sign, value, unit, unit_type = extract_value_and_unit(value_match.string)
            if value is not None:
                if validate_unit(param_std, unit, unit_type):
                    valid_unit_found = True
                    unit_final_formatted = unit
                    current_unit_type = unit_type
                    if param_std == "F. glomerular calculado":
                         full_unit_pattern = r"ml/min/1[.,]73m[2²\^]"
                         if re.search(full_unit_pattern, line_remainder_orig, re.IGNORECASE) or \
                           (search_line_idx == i + 1 and re.search(full_unit_pattern, lines[search_line_idx], re.IGNORECASE)):
                             unit_final_formatted = "ml/min/1.73m²"; current_unit_type = 'other'
                         elif sign == '>' and unit_final_formatted is None:
                              unit_final_formatted = "ml/min/1.73m²"; current_unit_type = 'other'
                    current_value_str = f"{param_std}: {sign}{value}{' ' + unit_final_formatted if unit_final_formatted else ''}"
                    logger.info(f"Parseado y VALIDADO Numérico: {current_value_str} (Tipo: {current_unit_type}) (Línea {search_line_idx+1})")

        if valid_unit_found and current_value_str:
            should_replace = False; existing_unit_type = existing_data[1] if existing_data else None
            if not existing_data: should_replace = True
            else:
                priority_map = {'abs': 5, 'other': 4, '%': 3, 'status': 2, None: 1}
                current_priority = priority_map.get(current_unit_type, 0)
                existing_priority = priority_map.get(existing_unit_type, 0)
                if current_priority >= existing_priority: should_replace = True

            if should_replace:
                 logger.debug(f"Exact Match: Guardando '{param_std}' (Tipo: {current_unit_type}) valor línea {search_line_idx+1}")
                 # *** GUARDAR LINE INDEX ***
                 results_intermediate[category][param_std] = (current_value_str.strip(), current_unit_type, "exact", search_line_idx)
                 processed_lines.add(search_line_idx)
                 if i != search_line_idx and i not in processed_lines: processed_lines.add(i)
                 found_by_exact = True
            # else: logger.debug(...)

        if not found_by_exact and i not in processed_lines and RE_VALUE_UNIT.search(line):
             if not any(l[0] == i for l in unrecognized_lines_with_values):
                 unrecognized_lines_with_values.append((i, line))

    logger.info("Iniciando Pasada 2: Fuzzy Matching + Validación...")
    fuzzy_found_count = 0
    for i, line in unrecognized_lines_with_values:
        if i in processed_lines: continue
        potential_param_std = fuzzy_match_parameter(line, threshold=0.70)
        if potential_param_std:
            category = param_to_category_map.get(potential_param_std)
            if not category: continue
            sign, value, unit, unit_type = extract_value_and_unit(line)
            if value is not None:
                if validate_unit(potential_param_std, unit, unit_type):
                    existing_data = results_intermediate[category].get(potential_param_std)
                    if not existing_data or existing_data[2] != "exact": # Solo si no hay exacto
                        unit_final = unit
                        formatted_value = f"{potential_param_std}: {sign}{value}{' ' + unit_final if unit_final else ''}"
                        detection_method = "fuzzy"
                        logger.info(f"Fuzzy Match: Guardando '{potential_param_std}' (Tipo: {unit_type}) valor línea {i+1}")
                        # *** GUARDAR LINE INDEX (i) ***
                        results_intermediate[category][potential_param_std] = (formatted_value.strip(), unit_type, detection_method, i)
                        processed_lines.add(i); fuzzy_found_count += 1
                # else: logger ya advirtió

    # --- Formatear salida final (preparando para formatter) ---
    # Devolver dict { Categoria: { StdName: (FormattedValue_with_Marker, LineIndex) } }
    final_results_for_formatter = defaultdict(dict)
    unique_params_count = 0
    for category, items in results_intermediate.items():
        for std_name, (formatted_value, unit_type, detection_method, line_idx) in items.items():
             if formatted_value:
                 display_value = formatted_value + " [~]" if detection_method == "fuzzy" else formatted_value
                 # Asegurar % final
                 expected_type_for_std = EXPECTED_UNITS_OR_TYPES.get(std_name)
                 if expected_type_for_std == '%' and unit_type == '%' and not display_value.replace(' [~]', '').endswith('%'):
                      parts = display_value.split(":", 1); val_part = parts[1].replace('[~]', '').strip().split(" ")[0]
                      display_value = f"{std_name}: {val_part} %{' [~]' if detection_method == 'fuzzy' else ''}"

                 final_results_for_formatter[category][std_name] = (display_value, line_idx) # Guardar tupla
                 unique_params_count += 1

    logger.info(f"Parseo finalizado. {unique_params_count} parámetros únicos para formatear.")
    return dict(final_results_for_formatter) # Devolver dict listo para formatear

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