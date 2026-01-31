import flet as ft
from data_manager import DataManager, Patient
from typing import Callable

def get_home_view(dm: DataManager, on_navigate: Callable, on_quick_add: Callable, update_sidebar: Callable):
    search_field = ft.TextField(
        label="Patient suchen...", 
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: update_patient_list(e.control.value),
        text_size=13,
        label_style=ft.TextStyle(size=12),
        dense=True
    )
    
    export_btn = ft.ElevatedButton(
        "Export", 
        icon=ft.Icons.DOWNLOAD, 
        on_click=lambda _: on_navigate("export"),
        style=ft.ButtonStyle(padding=10)
    )

    patient_list_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=5)

    def update_patient_list(query=""):
        if query:
            patients = dm.search_patients(query)
        else:
            patients = dm.get_active_patients()
        
        sorted_patients = dm.sort_patients(patients)
        
        rows = []
        for p in sorted_patients:
            # Medizinische Tags erstellen
            medical_tags = []
            tag_configs = [
                # Beatmung (Blau)
                ("invasive_beatmung", "Beatmung", ft.Colors.BLUE_800),
                ("niv", "NIV", ft.Colors.BLUE_800),
                ("hfnc", "HFNC", ft.Colors.BLUE_800),
                # Nierenersatz (Orange)
                ("crrt", "CRRT", ft.Colors.ORANGE_800),
                ("ihd", "iHD", ft.Colors.ORANGE_800),
                # Kreislaufunterstützung mechanisch (Rot)
                ("ecmo", "ECMO", ft.Colors.RED_800),
                ("impella", "Impella", ft.Colors.RED_800),
                # Medikamente (Grün)
                ("vasopressoren", "Vaso", ft.Colors.GREEN_800),
                ("inotropika", "Ino", ft.Colors.GREEN_800),
                ("sedierung", "Sed", ft.Colors.GREEN_800),
            ]
            
            for field, label, color in tag_configs:
                if getattr(p, field):
                    medical_tags.append(
                        ft.Container(
                            content=ft.Text(label, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=color,
                            padding=ft.padding.symmetric(horizontal=5, vertical=2),
                            border_radius=5
                        )
                    )

            c = ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE, 
                        icon_color=ft.Colors.GREEN,
                        tooltip="Quick Add",
                        on_click=lambda _, pid=p.id: on_quick_add(pid)
                    ),
                    ft.Column([
                        ft.Text(f"{p.name} ({p.bettplatz})", size=13, weight=ft.FontWeight.BOLD),
                        ft.Row(medical_tags, spacing=5, wrap=True) if medical_tags else ft.Container()
                    ], expand=True),
                    ft.IconButton(
                        icon=ft.Icons.VISIBILITY_OFF if not p.hidden else ft.Icons.VISIBILITY, 
                        icon_size=18,
                        tooltip="Hide/Unhide",
                        on_click=lambda _, pat=p: toggle_hide(pat)
                    ),
                ]),
                padding=2,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=8,
                on_click=lambda _, pid=p.id: on_navigate("patient", pid),
                ink=True
            )
            rows.append(c)
        patient_list_container.controls = rows
        try:
            if patient_list_container.page:
                patient_list_container.update()
        except Exception:
            pass

    def toggle_hide(patient: Patient):
        patient.hidden = not patient.hidden
        dm.update_patient(patient)
        update_sidebar()
        update_patient_list(search_field.value)

    update_patient_list()
    
    return ft.Column([
        ft.Row([
            ft.Text("Patienten Übersicht", size=20, weight=ft.FontWeight.BOLD), 
            export_btn
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        search_field,
        patient_list_container
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, spacing=10)
