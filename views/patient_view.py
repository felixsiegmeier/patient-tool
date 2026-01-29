import flet as ft
from data_manager import DataManager
from typing import Callable

def get_patient_view(dm: DataManager, patient_id: str, on_navigate: Callable, update_sidebar: Callable):
    patient = dm.get_patient_by_id(patient_id)
    if not patient:
        return ft.Column([
            ft.Text("Patient nicht gefunden.", size=16),
            ft.ElevatedButton("Zurück zur Übersicht", on_click=lambda _: on_navigate("home"))
        ])

    def on_change(e, field_name):
        setattr(patient, field_name, e.control.value)
        dm.update_patient(patient)
        # Sidebar aktualisieren, wenn sich Namens- oder Platzrelevante Felder ändern
        if field_name in ["name", "bettplatz"]:
            update_sidebar()

    # Definition der Eingabefelder: (Attributname, Label, Mehrzeilig)
    field_definitions = [
        ("name", "Name", False),
        ("bettplatz", "Bettplatz", False),
    ]

    medical_checkboxes = [
        ("invasive_beatmung", "Inv. Beatmung"),
        ("niv", "NIV"),
        ("hfnc", "HFNC"),
        ("crrt", "CRRT"),
        ("ecmo", "ECMO"),
        ("impella", "Impella"),
    ]

    other_fields = [
        ("diagnosen", "Diagnosen", True),
        ("operationen", "Operationen", True),
        ("kardiale_funktion", "Kardiale Funktion", True),
        ("antiinfektiva", "Antiinfektiva", True),
        ("diagnostik", "Diagnostik", True),
        ("verlauf", "Verlauf", True),
        ("probleme_aufgaben", "Probleme/Aufgaben", True),
    ]

    field_controls = []
    # Erste Zeile: Name, Bettplatz
    header_fields = []
    for field_name, label, multiline in field_definitions:
        tf = ft.TextField(
            label=label,
            value=getattr(patient, field_name) or "",
            multiline=multiline,
            on_change=lambda e, fn=field_name: on_change(e, fn),
            expand=True,
            text_size=13,
            label_style=ft.TextStyle(size=12),
            dense=True
        )
        header_fields.append(tf)
    field_controls.append(ft.Row(header_fields, spacing=10))

    # Checkboxen in einer Reihe mit Umbruch (ResponsiveRow für Stabilität)
    medical_controls = []
    for field_name, label in medical_checkboxes:
        cb = ft.Checkbox(
            label=label,
            label_style=ft.TextStyle(size=11),
            value=getattr(patient, field_name),
            on_change=lambda e, fn=field_name: on_change(e, fn),
            col={"xs": 6, "sm": 4, "md": 2} # Bricht auf kleinen Bildschirmen um (2 pro Zeile auf XS, 3 auf SM, 6 auf MD)
        )
        medical_controls.append(cb)
    
    field_controls.append(ft.ResponsiveRow(medical_controls, spacing=5, run_spacing=0))

    # Restliche Felder
    for field_name, label, multiline in other_fields:
        tf = ft.TextField(
            label=label,
            value=getattr(patient, field_name) or "",
            multiline=multiline,
            on_change=lambda e, fn=field_name: on_change(e, fn),
            min_lines=2 if multiline else 1,
            text_size=13,
            label_style=ft.TextStyle(size=12),
            dense=True
        )
        field_controls.append(tf)

    back_btn = ft.IconButton(
        ft.Icons.ARROW_BACK, 
        icon_size=20,
        on_click=lambda _: on_navigate("home")
    )

    return ft.Column([
        ft.Row([
            back_btn,
            ft.Text(f"Patient: {patient.name}", size=18, weight=ft.FontWeight.BOLD)
        ], spacing=5),
        ft.Column(
            field_controls, 
            scroll=ft.ScrollMode.AUTO, 
            expand=True, 
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=10
        )
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, spacing=10)
