import flet as ft
import os
from datetime import datetime
from data_manager import DataManager
from utils import format_patient_export, create_patient_pdf, get_resource_path
from typing import Callable

def get_export_view(page: ft.Page, dm: DataManager, on_navigate: Callable):
    active_patients = dm.get_active_patients()
    selected_patients = {p.id: True for p in active_patients}
    
    fields_config = {
        "name": "Name",
        "bettplatz": "Bettplatz",
        "unterstuetzung": "Med. Unterstützung",
        "diagnosen": "Diagnosen",
        "nebendiagnosen": "Nebendiagnosen",
        "operationen": "Operationen",
        "weitere_operationen": "Weitere Operationen",
        "kardiale_funktion": "Kardiale Funktion",
        "antiinfektiva": "Antiinfektiva",
        "diagnostik": "Diagnostik",
        "verlauf": "Verlauf",
        "probleme_aufgaben": "Probleme/Aufgaben",
        "uebergabe": "Übergabe"
    }
    
    # Standardauswahl für Felder
    default_fields = ["name", "unterstuetzung", "diagnosen", "nebendiagnosen", "operationen", "kardiale_funktion", "antiinfektiva", "uebergabe"]
    selected_fields = {k: (k in default_fields) for k in fields_config.keys()}

    export_preview = ft.TextField(
        multiline=True,
        read_only=True,
        label="Export Vorschau",
        expand=True,
        text_size=11,
        text_style=ft.TextStyle(font_family="monospace"),
        min_lines=10,
        dense=True
    )

    def update_export_preview():
        included_patients = [p for p in dm.patients if selected_patients.get(p.id)]
        sorted_p = dm.sort_patients(included_patients)
        included_fields = [k for k, v in selected_fields.items() if v]
        
        full_text = []
        for p in sorted_p:
            full_text.append(format_patient_export(p, included_fields))
            full_text.append("-" * 40)
        
        export_preview.value = "\n".join(full_text)
        try:
            if export_preview.page:
                export_preview.update()
        except Exception:
            pass

    def on_patient_toggle(pid, val):
        selected_patients[pid] = val
        update_export_preview()

    def on_field_toggle(fid, val):
        selected_fields[fid] = val
        update_export_preview()

    def copy_to_clipboard(_):
        page.clipboard.set(export_preview.value)
        show_snack_bar(page, "In Zwischenablage kopiert!")

    def print_to_pdf(_):
        included_patients = [p for p in dm.patients if selected_patients.get(p.id)]
        sorted_p = dm.sort_patients(included_patients)
        included_fields = [k for k, v in selected_fields.items() if v]
        
        filename = f"Patienten_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = get_resource_path(filename)
        
        try:
            create_patient_pdf(sorted_p, included_fields, filepath)
            open_file(filepath)
            show_snack_bar(page, f"PDF erstellt: {filename}")
        except Exception as ex:
            show_snack_bar(page, f"Fehler beim PDF-Export: {str(ex)}", is_error=True)

    def show_snack_bar(page, message, is_error=False):
        page.overlay.append(ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_700 if is_error else None,
            open=True
        ))
        page.update()

    def open_file(path):
        if os.name == 'nt':
            os.startfile(path)
        else:
            import subprocess
            cmd = ['open', path] if os.uname().sysname == 'Darwin' else ['xdg-open', path]
            try:
                subprocess.run(cmd)
            except:
                pass

    # UI Controls
    patient_checks = ft.Column([
        ft.Checkbox(
            label=p.name, 
            value=selected_patients[p.id], 
            label_style=ft.TextStyle(size=12),
            on_change=lambda e, pid=p.id: on_patient_toggle(pid, e.control.value)
        ) for p in active_patients
    ], spacing=0)

    field_checks = ft.Row([
        ft.Checkbox(
            label=label, 
            value=selected_fields.get(key, False), 
            label_style=ft.TextStyle(size=12),
            on_change=lambda e, fid=key: on_field_toggle(fid, e.control.value)
        ) for key, label in fields_config.items()
    ], wrap=True, spacing=5)

    selection_tile = ft.ExpansionTile(
        title=ft.Text("Patienten & Parameter auswählen", size=13, weight=ft.FontWeight.BOLD),
        expanded=False,
        controls_padding=5,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("1. Felder auswählen", size=12, weight=ft.FontWeight.BOLD),
                    field_checks,
                    ft.Divider(height=10),
                    ft.Text("2. Patienten auswählen", size=12, weight=ft.FontWeight.BOLD),
                    patient_checks,
                ], spacing=5, scroll=ft.ScrollMode.ADAPTIVE),
                height=300,
            )
        ]
    )

    update_export_preview()

    return ft.Column([
        ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK, icon_size=20, on_click=lambda _: on_navigate("home")),
            ft.Text("Daten Exportieren", size=18, weight=ft.FontWeight.BOLD)
        ], spacing=5),
        selection_tile,
        ft.Row([
            ft.Text("3. Ergebnis (Copy-Paste / Drucken)", size=12, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.IconButton(ft.Icons.COPY, icon_size=20, on_click=copy_to_clipboard, tooltip="In Zwischenablage kopieren"),
                ft.IconButton(ft.Icons.PRINT, icon_size=20, on_click=print_to_pdf, tooltip="Als A4-PDF drucken")
            ], spacing=0)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        export_preview
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, spacing=10)
