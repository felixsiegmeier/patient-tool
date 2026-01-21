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
    p = Patient(name="Test Patient", station="Station 1", bettplatz="A1")
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
    dm.add_patient(Patient(name="Alpha", station="S1"))
    dm.add_patient(Patient(name="Beta", station="S2"))
    
    results = dm.search_patients("Alpha")
    assert len(results) == 1
    assert results[0].name == "Alpha"

def test_sort_patients(temp_yaml):
    dm = DataManager(temp_yaml)
    p1 = Patient(name="P1", station="B", bettplatz="2")
    p2 = Patient(name="P2", station="A", bettplatz="1")
    p3 = Patient(name="P3", station="A", bettplatz="10") # Testet String-Sortierung (10 kommt nach 1)
    
    sorted_p = dm.sort_patients([p1, p2, p3])
    assert sorted_p[0].name == "P2" # Station A, Bett 1
    assert sorted_p[1].name == "P3" # Station A, Bett 10
    assert sorted_p[2].name == "P1" # Station B, Bett 2

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
