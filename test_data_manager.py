import pytest
import os
import yaml
from data_manager import DataManager, Patient

@pytest.fixture
def temp_yaml(tmp_path):
    return os.path.join(tmp_path, "test_patients.yaml")

def test_data_manager_initialization(temp_yaml):
    dm = DataManager(temp_yaml)
    assert dm.patients == []
    assert os.path.exists(temp_yaml)

def test_add_patient(temp_yaml):
    dm = DataManager(temp_yaml)
    p = Patient(name="Test Patient", bettplatz="A1")
    dm.add_patient(p)
    
    # Neu laden
    dm2 = DataManager(temp_yaml)
    assert len(dm2.patients) == 1
    assert dm2.patients[0].name == "Test Patient"
    assert dm2.patients[0].id == p.id

def test_update_patient(temp_yaml):
    dm = DataManager(temp_yaml)
    p = Patient(name="Old Name")
    dm.add_patient(p)
    
    p.name = "New Name"
    dm.update_patient(p)
    
    dm2 = DataManager(temp_yaml)
    assert dm2.patients[0].name == "New Name"

def test_search_patients(temp_yaml):
    dm = DataManager(temp_yaml)
    dm.add_patient(Patient(name="Alpha"))
    dm.add_patient(Patient(name="Beta"))
    
    results = dm.search_patients("Alpha")
    assert len(results) == 1
    assert results[0].name == "Alpha"

def test_sort_patients(temp_yaml):
    dm = DataManager(temp_yaml)
    p1 = Patient(name="P1", bettplatz="2")
    p2 = Patient(name="P2", bettplatz="1")
    p3 = Patient(name="P3", bettplatz="10") # Testet String-Sortierung (10 kommt nach 1)
    
    sorted_p = dm.sort_patients([p1, p2, p3])
    assert sorted_p[0].name == "P2" # Bett 1
    assert sorted_p[1].name == "P1" # Bett 2
    assert sorted_p[2].name == "P3" # Bett 10

def test_hide_patient(temp_yaml):
    dm = DataManager(temp_yaml)
    p = Patient(name="Hidden", hidden=False)
    dm.add_patient(p)
    
    active = dm.get_active_patients()
    assert len(active) == 1
    
    p.hidden = True
    dm.update_patient(p)
    
    active = dm.get_active_patients()
    assert len(active) == 0

def test_medical_fields(temp_yaml):
    dm = DataManager(temp_yaml)
    p = Patient(
        name="ICU Patient", 
        invasive_beatmung=True, 
        ecmo=True,
        vasopressoren=True,
        inotropika=True,
        ihd=True,
        sedierung=True
    )
    dm.add_patient(p)
    
    dm2 = DataManager(temp_yaml)
    loaded_p = dm2.patients[0]
    assert loaded_p.invasive_beatmung is True
    assert loaded_p.ecmo is True
    assert loaded_p.vasopressoren is True
    assert loaded_p.inotropika is True
    assert loaded_p.ihd is True
    assert loaded_p.sedierung is True
    assert loaded_p.niv is False
    assert loaded_p.hfnc is False
    assert loaded_p.crrt is False
    assert loaded_p.impella is False

def test_backward_compatibility(temp_yaml):
    # Alte YAML-Struktur: mit 'station', ohne medizinische Checkboxen
    old_data = [
        {
            "id": "old-id-1",
            "name": "Altpatient",
            "station": "ITS 1",
            "bettplatz": "12",
            "diagnosen": "Pneumonie",
            "hidden": False
        }
    ]
    with open(temp_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(old_data, f)
    
    # Laden mit dem aktuellen DataManager
    dm = DataManager(temp_yaml)
    assert len(dm.patients) == 1
    p = dm.patients[0]
    
    assert p.name == "Altpatient"
    # Die station ITS 1 sollte in den Bettplatz migriert worden sein
    assert p.bettplatz == "ITS 1 12"
    
    # Neue Felder sollten mit False initialisiert sein
    assert p.invasive_beatmung is False
    assert p.ecmo is False
    assert p.niv is False
    
    # Sicherstellen, dass die station-Daten nicht einfach sang- und klanglos verschwinden, 
    # falls sie noch nützlich sein könnten. 
    # Aber laut Anforderung "vollständig entfernen".
    # Wir prüfen hier nur, dass das Laden nicht abstürzt.
