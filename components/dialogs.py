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
    ]), value="verlauf")
    
    text_input = ft.TextField(label="Information", multiline=True, autofocus=True)
    
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
        title=ft.Text(f"Quick Add für {patient.name}"),
        content=ft.Column([
            ft.Text("Zielbereich:"),
            target_field,
            text_input
        ], tight=True),
        actions=[
            ft.TextButton("Abbrechen", on_click=lambda _: page.pop_dialog()),
            ft.TextButton("Hinzufügen", on_click=save_quick_add)
        ]
    )
    page.show_dialog(dialog)
