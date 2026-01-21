import os
import sys
import re
from datetime import datetime
from fpdf import FPDF

def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        # Wenn die App als EXE läuft
        if hasattr(sys, '_MEIPASS'):
            # Interne Ressource (z.B. Logo)
            internal_path = os.path.join(sys._MEIPASS, filename)
            if os.path.exists(internal_path):
                return internal_path
        # Externe Datei neben der EXE (z.B. patients.yaml)
        base_path = os.path.dirname(sys.executable)
    else:
        # Wenn die App als Skript läuft
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

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

def create_patient_pdf(patients, fields_to_include, filepath):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("helvetica", size=10)
    
    line_height = 5
    # Nutze etwas Puffer für den unteren Rand
    margin_bottom = 20
    page_height = 297 - margin_bottom 
    
    pdf.set_font("helvetica", style="B", size=14)
    pdf.cell(0, 10, f"Patientenliste - Stand {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
    pdf.ln(5)
    
    for patient in patients:
        # Text für diesen Patienten generieren
        patient_text = format_patient_export(patient, fields_to_include)
        lines = patient_text.splitlines()
        
        # Höhenberechnung
        # fpdf2 multiline text handling: we can use multi_cell with split_only=True to get lines
        # But here we already have lines. Let's check how long they are to handle wrapping.
        
        needed_height = 0
        formatted_lines = []
        for line in lines:
            # Wir müssen prüfen, ob eine Zeile im PDF umbrechen würde
            # Multi_cell split_only gibt uns die Anzahl der Zeilen zurück
            # Da wir 10pt Helvetica nutzen, ist die Breite begrenzt.
            w = pdf.w - 2 * pdf.l_margin
            # split_text_to_lines ist eine interne Methode oder wir nutzen multi_cell
            # Einfacher: wir gehen davon aus, dass die meisten Zeilen passen, 
            # aber zur Sicherheit schätzen wir es.
            
            # Bei Schriftgröße 10pt passen ca. 80-100 Zeichen in eine Zeile.
            # Da Patientenakten oft kurze Stichpunkte sind, passen sie meistens.
            wrapped = pdf.multi_cell(w, line_height, line, split_only=True)
            for w_line in wrapped:
                formatted_lines.append(w_line)
                needed_height += line_height
        
        needed_height += 5 # Abstand nach Patient
        
        # Prüfen ob der Block auf die Seite passt
        if needed_height > (page_height - 20): # Falls Patient > fast ganze Seite
             if pdf.get_y() > 30: # Nur neue Seite wenn wir nicht schon am Anfang sind
                pdf.add_page()
        elif pdf.get_y() + needed_height > page_height:
            pdf.add_page()
            
        # Patientenblock rendern
        for i, line in enumerate(formatted_lines):
            if i == 0:
                pdf.set_font("helvetica", style="B", size=10)
            else:
                pdf.set_font("helvetica", style="", size=10)
            
            pdf.cell(0, line_height, line, ln=True)
            
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.l_margin, pdf.get_y() + 2, pdf.w - pdf.r_margin, pdf.get_y() + 2)
        pdf.ln(5) 
        
    pdf.output(filepath)
