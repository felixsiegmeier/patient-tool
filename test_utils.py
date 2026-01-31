from utils import format_patient_export, get_current_date_prefix, sanitize_for_pdf
from data_manager import Patient
from datetime import datetime

def test_get_current_date_prefix():
    prefix = get_current_date_prefix()
    expected = f"[{datetime.now().strftime('%d.%m.')}]"
    assert prefix == expected

def test_format_patient_export():
    p = Patient(
        name="Max Mustermann", 
        bettplatz="1", 
        diagnosen="Test",
        vasopressoren=True,
        sedierung=True
    )
    fields = ["name", "bettplatz", "diagnosen", "unterstuetzung"]
    export = format_patient_export(p, fields)
    
    assert "Name: Max Mustermann" in export
    assert "Bettplatz: 1" in export
    assert "Diagnosen:" in export
    assert "Test" in export
    assert "Unterstützung: Vasopressoren, Sedierung" in export

def test_sanitize_for_pdf():
    text = "Langer Bindestrich: \u2013, Pfeil: \u2192, Unbekannt: \u263a"
    sanitized = sanitize_for_pdf(text)
    
    assert "\u2013" not in sanitized
    assert "-" in sanitized
    assert "\u2192" not in sanitized
    assert "->" in sanitized
    assert "?" in sanitized # \u263a (Smiley) ist nicht in Latin-1 und sollte durch ? ersetzt werden
