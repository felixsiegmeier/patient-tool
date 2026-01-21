import flet as ft
from data_manager import DataManager
from typing import Callable

def get_patient_view(dm: DataManager, patient_id: str, on_navigate: Callable, update_sidebar: Callable):
    patient = dm.get_patient_by_id(patient_id)
    if not patient:
        return ft.Column([
            ft.Text("Patient nicht gefunden.", size=20),
            ft.Button("Zurück zur Übersicht", on_click=lambda _: on_navigate("home"))
        ])

    def on_change(e, field_name):
        setattr(patient, field_name, e.control.value)
        dm.update_patient(patient)
        # Sidebar aktualisieren, wenn sich Namens- oder Platzrelevante Felder ändern
        if field_name in ["name", "station", "bettplatz"]:
            update_sidebar()

    # Definition der Eingabefelder: (Attributname, Label, Mehrzeilig)
    field_definitions = [
        ("name", "Name", True),
        ("station", "Station", False),
        ("bettplatz", "Bettplatz", False),
        ("diagnosen", "Diagnosen", True),
        ("operationen", "Operationen", True),
        ("kardiale_funktion", "Kardiale Funktion", True),
        ("antiinfektiva", "Antiinfektiva", True),
        ("diagnostik", "Diagnostik", True),
        ("verlauf", "Verlauf", True),
        ("probleme_aufgaben", "Probleme/Aufgaben", True),
    ]

    field_controls = []
    for field_name, label, multiline in field_definitions:
        tf = ft.TextField(
            label=label,
            value=getattr(patient, field_name) or "",
            multiline=multiline,
            on_change=lambda e, fn=field_name: on_change(e, fn),
        )
        field_controls.append(tf)

    back_btn = ft.IconButton(
        ft.Icons.ARROW_BACK, 
        on_click=lambda _: on_navigate("home")
    )

    return ft.Column([
        ft.Row([
            back_btn,
            ft.Text(f"Patient: {patient.name}", size=20, weight=ft.FontWeight.BOLD)
        ]),
        ft.Column(
            field_controls, 
            scroll=ft.ScrollMode.AUTO, 
            expand=True, 
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        )
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
