import yaml
import os
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field
from utils import get_resource_path, natural_sort_key

class Patient(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    station: str = ""
    bettplatz: str = ""
    diagnosen: str = ""
    operationen: str = ""
    kardiale_funktion: str = ""
    antiinfektiva: str = ""
    diagnostik: str = ""
    verlauf: str = ""
    probleme_aufgaben: str = ""
    hidden: bool = False

class DataManager:
    def __init__(self, filename: str = "patients.yaml"):
        if not os.path.isabs(filename):
            self.filename = get_resource_path(filename)
        else:
            self.filename = filename
        self.patients: List[Patient] = []
        self.load()

    def load(self):
        """Lädt Patienten aus der YAML-Datei."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or []
                self.patients = [Patient.model_validate(p) for p in data]
        else:
            self.patients = []
            self.save()

    def save(self):
        """Speichert Patienten in die YAML-Datei."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            data = [p.model_dump() for p in self.patients]
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    def add_patient(self, patient: Patient):
        """Fügt einen neuen Patienten hinzu und speichert."""
        self.patients.append(patient)
        self.save()

    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Sucht einen Patienten anhand seiner ID."""
        return next((p for p in self.patients if p.id == patient_id), None)

    def update_patient(self, patient: Patient) -> bool:
        """Aktualisiert die Daten eines Patienten."""
        for i, p in enumerate(self.patients):
            if p.id == patient.id:
                self.patients[i] = patient
                self.save()
                return True
        return False

    def get_active_patients(self) -> List[Patient]:
        """Gibt alle nicht-versteckten Patienten zurück."""
        return [p for p in self.patients if not p.hidden]

    def search_patients(self, query: str) -> List[Patient]:
        """Sucht Patienten nach Name oder Station (case-insensitive)."""
        query = query.lower()
        return [
            p for p in self.patients 
            if query in p.name.lower() or query in p.station.lower()
        ]

    def sort_patients(self, patients_list: List[Patient]) -> List[Patient]:
        """Sortiert Patienten nach Station und Bettplatz (natürliche Sortierung)."""
        return sorted(
            patients_list, 
            key=lambda p: (p.station.lower(), natural_sort_key(p.bettplatz))
        )
