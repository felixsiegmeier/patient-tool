import flet as ft
from data_manager import DataManager, Patient
from typing import Callable

def get_home_view(dm: DataManager, on_navigate: Callable, on_quick_add: Callable, update_sidebar: Callable):
    search_field = ft.TextField(
        label="Patient suchen...", 
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: update_patient_list(e.control.value)
    )
    
    export_btn = ft.Button(
        "Export", 
        icon=ft.Icons.DOWNLOAD, 
        on_click=lambda _: on_navigate("export")
    )

    patient_list_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def update_patient_list(query=""):
        if query:
            patients = dm.search_patients(query)
        else:
            patients = dm.get_active_patients()
        
        sorted_patients = dm.sort_patients(patients)
        
        rows = []
        for p in sorted_patients:
            c = ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE, 
                        icon_color=ft.Colors.GREEN,
                        tooltip="Quick Add",
                        on_click=lambda _, pid=p.id: on_quick_add(pid)
                    ),
                    ft.Text(f"{p.name} ({p.station} / {p.bettplatz})", weight=ft.FontWeight.BOLD, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.VISIBILITY_OFF if not p.hidden else ft.Icons.VISIBILITY, 
                        tooltip="Hide/Unhide",
                        on_click=lambda _, pat=p: toggle_hide(pat)
                    ),
                ]),
                padding=5,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
                on_click=lambda _, pid=p.id: on_navigate("patient", pid),
                ink=True
            )
            rows.append(c)
        patient_list_container.controls = rows
        if patient_list_container.page:
            patient_list_container.update()

    def toggle_hide(patient: Patient):
        patient.hidden = not patient.hidden
        dm.update_patient(patient)
        update_sidebar()
        update_patient_list(search_field.value)

    update_patient_list()
    
    return ft.Column([
        ft.Row([
            ft.Text("Patienten Übersicht", size=24, weight=ft.FontWeight.BOLD), 
            export_btn
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        search_field,
        patient_list_container
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
