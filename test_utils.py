from utils import format_patient_export, get_current_date_prefix
from data_manager import Patient
from datetime import datetime

def test_get_current_date_prefix():
    prefix = get_current_date_prefix()
    expected = f"[{datetime.now().strftime('%d.%m.')}]"
    assert prefix == expected

def test_format_patient_export():
    p = Patient(name="Max Mustermann", station="ITS", bettplatz="1", diagnosen="Test")
    fields = ["name", "station", "diagnosen"]
    export = format_patient_export(p, fields)
    
    assert "Name: Max Mustermann" in export
    assert "Station: ITS" in export
    assert "Diagnosen:" in export
    assert "Test" in export
    assert "Bettplatz" not in export
