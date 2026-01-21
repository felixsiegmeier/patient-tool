from datetime import datetime

def get_current_date_prefix():
    return f"[{datetime.now().strftime('%d.%m.')}]"

def format_patient_export(patient, fields_to_include):
    lines = []
    lines.append(f"Name: {patient.name}")
    if "station" in fields_to_include:
        lines.append(f"  Station: {patient.station}")
    if "bettplatz" in fields_to_include:
        lines.append(f"  Bettplatz: {patient.bettplatz}")
    
    field_mapping = {
        "diagnosen": "Diagnosen",
        "operationen": "Operationen",
        "kardiale_funktion": "Kardiale Funktion",
        "antiinfektiva": "Antiinfektiva",
        "diagnostik": "Diagnostik",
        "verlauf": "Verlauf",
        "probleme_aufgaben": "Probleme/Aufgaben"
    }
    
    for key, label in field_mapping.items():
        if key in fields_to_include:
            value = getattr(patient, key)
            if value:
                lines.append(f"  {label}:")
                for line in value.splitlines():
                    lines.append(f"    {line}")
    
    return "\n".join(lines)
