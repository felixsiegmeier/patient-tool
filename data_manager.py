import yaml
import os
import uuid
import sys
import re
from typing import List, Dict, Optional

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        # Wenn die App als EXE läuft
        base_path = os.path.dirname(sys.executable)
    else:
        # Wenn die App als Skript läuft
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

class Patient:
    def __init__(self, 
                 id: str = None, 
                 name: str = "", 
                 station: str = "", 
                 bettplatz: str = "", 
                 diagnosen: str = "", 
                 operationen: str = "", 
                 kardiale_funktion: str = "", 
                 antiinfektiva: str = "", 
                 diagnostik: str = "", 
                 verlauf: str = "", 
                 probleme_aufgaben: str = "", 
                 hidden: bool = False):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.station = station
        self.bettplatz = bettplatz
        self.diagnosen = diagnosen
        self.operationen = operationen
        self.kardiale_funktion = kardiale_funktion
        self.antiinfektiva = antiinfektiva
        self.diagnostik = diagnostik
        self.verlauf = verlauf
        self.probleme_aufgaben = probleme_aufgaben
        self.hidden = hidden

    def to_dict(self):
        return vars(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class DataManager:
    def __init__(self, filename="patients.yaml"):
        if not os.path.isabs(filename):
            self.filename = get_resource_path(filename)
        else:
            self.filename = filename
        self.patients: List[Patient] = []
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or []
                self.patients = [Patient.from_dict(p) for p in data]
        else:
            self.patients = []
            self.save()

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            yaml.dump([p.to_dict() for p in self.patients], f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    def add_patient(self, patient: Patient):
        self.patients.append(patient)
        self.save()

    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        for p in self.patients:
            if p.id == patient_id:
                return p
        return None

    def update_patient(self, patient: Patient):
        for i, p in enumerate(self.patients):
            if p.id == patient.id:
                self.patients[i] = patient
                self.save()
                return True
        return False

    def get_active_patients(self):
        return [p for p in self.patients if not p.hidden]

    def search_patients(self, query: str):
        query = query.lower()
        return [p for p in self.patients if query in p.name.lower() or query in p.station.lower()]

    def sort_patients(self, patients_list: List[Patient]):
        # Alphabetisch nach Station, dann numerisch/alphabetisch nach Bettplatz
        return sorted(patients_list, key=lambda p: (p.station.lower(), natural_sort_key(p.bettplatz)))
