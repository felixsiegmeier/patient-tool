import flet as ft
from data_manager import DataManager, Patient
from utils import get_current_date_prefix

def open_quick_add_dialog(page: ft.Page, dm: DataManager, patient_id: str):
    patient = dm.get_patient_by_id(patient_id)
    if not patient:
        return

    target_field = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="verlauf", label="Verlauf"),
        ft.Radio(value="diagnosen", label="Diagnosen"),
        ft.Radio(value="diagnostik", label="Diagnostik"),
        ft.Radio(value="probleme_aufgaben", label="Probleme/Aufgaben"),
    ], spacing=0), value="verlauf")
    
    text_input = ft.TextField(
        label="Information", 
        multiline=True, 
        autofocus=True,
        text_size=13,
        label_style=ft.TextStyle(size=12),
        dense=True
    )
    
    def save_quick_add(_):
        if not text_input.value:
            page.pop_dialog()
            return
            
        prefix = get_current_date_prefix()
        field_name = target_field.value
        current_val = getattr(patient, field_name) or ""
        new_val = f"{current_val}\n{prefix} {text_input.value}".strip()
        setattr(patient, field_name, new_val)
        dm.update_patient(patient)
        page.pop_dialog()

    dialog = ft.AlertDialog(
        title=ft.Text(f"Quick Add für {patient.name}", size=16, weight=ft.FontWeight.BOLD),
        content=ft.Column([
            ft.Text("Zielbereich:", size=12),
            target_field,
            text_input
        ], tight=True, spacing=10),
        actions=[
            ft.TextButton("Abbrechen", on_click=lambda _: page.pop_dialog()),
            ft.TextButton("Hinzufügen", on_click=save_quick_add)
        ]
    )
    page.show_dialog(dialog)

def open_uebergabe_dialog(page: ft.Page, dm: DataManager, patient_id: str):
    patient = dm.get_patient_by_id(patient_id)
    if not patient:
        return

    text_input = ft.TextField(
        label="Übergabe", 
        value=patient.uebergabe or "",
        multiline=True, 
        autofocus=True,
        text_size=13,
        label_style=ft.TextStyle(size=12),
        dense=True,
        min_lines=5,
        max_lines=15
    )
    
    def save_uebergabe(_):
        patient.uebergabe = text_input.value
        dm.update_patient(patient)
        page.pop_dialog()

    dialog = ft.AlertDialog(
        title=ft.Text(f"Übergabe bearbeiten: {patient.name}", size=16, weight=ft.FontWeight.BOLD),
        content=ft.Column([
            text_input
        ], tight=True, width=500),
        actions=[
            ft.TextButton("Abbrechen", on_click=lambda _: page.pop_dialog()),
            ft.TextButton("Speichern", on_click=save_uebergabe)
        ]
    )
    page.show_dialog(dialog)
