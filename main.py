import flet as ft
from data_manager import DataManager, Patient, get_resource_path
from utils import get_current_date_prefix, format_patient_export, create_patient_pdf
import uuid
import os
from datetime import datetime

def main(page: ft.Page):
    page.title = "Patienten Übersicht"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1200
    page.window.height = 800
    page.window.icon = get_resource_path("logo.png")
    
    # Data Manager initialisieren
    # In einer EXE Umgebung sollte der Pfad relativ zur EXE sein
    # Für die Entwicklung nutzen wir einfach 'patients.yaml'
    dm = DataManager("patients.yaml")

    # UI Komponenten für Sidebar
    sidebar_fixed = ft.Column()
    sidebar_scrollable = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    sidebar_container = ft.Column([
        sidebar_fixed,
        sidebar_scrollable
    ], width=250, expand=True)

    def navigate_to(view_name, patient_id=None):
        page.session.store.set("current_view", view_name)
        if patient_id:
            page.session.store.set("current_patient_id", patient_id)
        update_view()

    def update_sidebar():
        active_patients = dm.get_active_patients()
        sorted_patients = dm.sort_patients(active_patients)
        
        def on_sidebar_hover(e, container):
            container.bgcolor = ft.Colors.BLACK12 if e.data == "true" else None
            container.update()

        def create_sidebar_item(icon_name, text, on_click_handler):
            c = ft.Container(
                content=ft.Row([
                    ft.Icon(icon_name, size=20) if icon_name else ft.Container(),
                    ft.Text(text, size=14)
                ]),
                padding=ft.padding.symmetric(vertical=5, horizontal=10),
                border_radius=10,
            )
            c.on_hover = lambda e: on_sidebar_hover(e, c)
            return ft.GestureDetector(
                content=c,
                on_tap=on_click_handler,
                mouse_cursor=ft.MouseCursor.CLICK
            )
        
        fixed_items = [
            ft.Container(
                content=ft.Image(
                    src=get_resource_path("logo.png"),
                    width=100,
                    height=100,
                    fit=ft.BoxFit.CONTAIN,
                ),
                alignment=ft.alignment.center,
                padding=10,
            ),
            create_sidebar_item(ft.Icons.HOME, "Übersicht", lambda _: navigate_to("home")),
            ft.Divider(),
            create_sidebar_item(ft.Icons.ADD, "Patient hinzufügen", lambda _: add_new_patient()),
            ft.Divider(),
            ft.Text("Aktive Patienten", size=12, weight=ft.FontWeight.BOLD),
        ]
        
        patient_items = []
        for p in sorted_patients:
            patient_items.append(
                create_sidebar_item(None, f"{p.name} ({p.station}/{p.bettplatz})", lambda _, pid=p.id: navigate_to("patient", pid))
            )
            
        sidebar_fixed.controls = fixed_items
        sidebar_scrollable.controls = patient_items
        page.update()

    def add_new_patient():
        new_patient = Patient(name="Neuer Patient")
        dm.add_patient(new_patient)
        update_sidebar()
        navigate_to("patient", new_patient.id)

    # --- Views ---

    def get_home_view():
        search_field = ft.TextField(
            label="Patient suchen...", 
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: update_patient_list(e.control.value)
        )
        
        export_btn = ft.Button("Export", icon=ft.Icons.DOWNLOAD, on_click=lambda _: navigate_to("export"))

        patient_list_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def update_patient_list(query=""):
            if query:
                patients = dm.search_patients(query)
            else:
                patients = dm.get_active_patients()
            
            sorted_patients = dm.sort_patients(patients)
            
            rows = []
            for i, p in enumerate(sorted_patients):
                c = ft.Container(
                        content=ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE, 
                                icon_color=ft.Colors.GREEN,
                                tooltip="Quick Add",
                                on_click=lambda _, pid=p.id: open_quick_add(pid)
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
                        on_click=lambda _, pid=p.id: navigate_to("patient", pid),
                        ink=True
                    )
                rows.append(c)
            patient_list_container.controls = rows
            page.update()

        def toggle_hide(patient):
            patient.hidden = not patient.hidden
            dm.update_patient(patient)
            update_sidebar()
            update_patient_list(search_field.value)

        update_patient_list()
        
        return ft.Column([
            ft.Row([ft.Text("Patienten Übersicht", size=24, weight=ft.FontWeight.BOLD), 
                    export_btn], 
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            search_field,
            patient_list_container
        ], expand=True, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def get_patient_view(patient_id):
        patient = dm.get_patient_by_id(patient_id)
        if not patient:
            return ft.Text("Patient nicht gefunden.")

        def on_change(e, field_name):
            setattr(patient, field_name, e.control.value)
            dm.update_patient(patient)
            if field_name in ["name", "station", "bettplatz"]:
                update_sidebar()

        fields = [
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

        controls = []
        for i, (field_name, label, multiline) in enumerate(fields):
            tf = ft.TextField(
                label=label,
                value=getattr(patient, field_name),
                multiline=multiline,
                on_change=lambda e, fn=field_name: on_change(e, fn)
            )
            controls.append(tf)

        # Back Button
        back_btn = ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate_to("home"))

        return ft.Column([
            ft.Row([
                back_btn,
                ft.Text(f"Patient: {patient.name}", size=20, weight=ft.FontWeight.BOLD)
            ]),
            ft.Column(controls, scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        ], expand=True, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def get_export_view():
        all_patients = dm.patients
        active_patients = dm.get_active_patients()
        selected_patients = {p.id: (not p.hidden) for p in all_patients}
        
        fields_config = {
            "name": "Name",
            "station": "Station",
            "bettplatz": "Bettplatz",
            "diagnosen": "Diagnosen",
            "operationen": "Operationen",
            "kardiale_funktion": "Kardiale Funktion",
            "antiinfektiva": "Antiinfektiva",
            "diagnostik": "Diagnostik",
            "verlauf": "Verlauf",
            "probleme_aufgaben": "Probleme/Aufgaben"
        }
        selected_fields = {k: True for k in fields_config.keys() if k not in ["station", "bettplatz", "diagnostik", "verlauf", "probleme_aufgaben"]}

        export_text = ft.TextField(
            multiline=True,
            read_only=True,
            label="Export Vorschau",
            expand=True,
            text_size=12,
            text_style=ft.TextStyle(font_family="monospace"),
            min_lines=10,
        )

        def update_export_preview():
            included_patients = [p for p in dm.patients if selected_patients.get(p.id)]
            sorted_p = dm.sort_patients(included_patients)
            included_fields = [k for k, v in selected_fields.items() if v]
            
            full_text = []
            for p in sorted_p:
                full_text.append(format_patient_export(p, included_fields))
                full_text.append("-" * 40)
            
            export_text.value = "\n".join(full_text)
            page.update()

        def toggle_patient(pid, val):
            selected_patients[pid] = val
            update_export_preview()

        def toggle_field(fid, val):
            selected_fields[fid] = val
            update_export_preview()

        patient_checks = ft.Column([
            ft.Checkbox(label=p.name, value=selected_patients[p.id], on_change=lambda e, pid=p.id: toggle_patient(pid, e.control.value))
            for p in all_patients
        ])

        field_checks = ft.Row([
            ft.Checkbox(label=label, value=selected_fields.get(key, False), on_change=lambda e, fid=key: toggle_field(fid, e.control.value))
            for key, label in fields_config.items()
        ], wrap=True)

        update_export_preview()

        def copy_to_clipboard(_):
            page.clipboard.set(export_text.value)
            snack_bar = ft.SnackBar(ft.Text("In Zwischenablage kopiert!"))
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()

        def print_to_pdf(_):
            included_patients = [p for p in dm.patients if selected_patients.get(p.id)]
            sorted_p = dm.sort_patients(included_patients)
            included_fields = [k for k, v in selected_fields.items() if v]
            
            from data_manager import get_resource_path
            filename = f"Patienten_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = get_resource_path(filename)
            
            try:
                create_patient_pdf(sorted_p, included_fields, filepath)
                if os.name == 'nt':
                    os.startfile(filepath)
                else:
                    import subprocess
                    try:
                        cmd = ['open', filepath] if os.uname().sysname == 'Darwin' else ['xdg-open', filepath]
                        subprocess.run(cmd)
                    except:
                        pass # Fallback falls open/xdg-open nicht da
                
                snack_bar = ft.SnackBar(ft.Text(f"PDF erstellt: {filename}"))
                page.overlay.append(snack_bar)
                snack_bar.open = True
                page.update()
            except Exception as ex:
                snack_bar = ft.SnackBar(ft.Text(f"Fehler beim PDF-Export: {str(ex)}"))
                page.overlay.append(snack_bar)
                snack_bar.open = True
                page.update()

        selection_tile = ft.ExpansionTile(
            title=ft.Text("Patienten & Parameter auswählen", weight=ft.FontWeight.BOLD),
            expanded=False,
            controls=[
                ft.Column([
                    ft.Text("1. Patienten auswählen", weight=ft.FontWeight.BOLD),
                    patient_checks,
                    ft.Divider(),
                    ft.Text("2. Felder auswählen", weight=ft.FontWeight.BOLD),
                    field_checks,
                ], spacing=10)
            ],
            controls_padding=10
        )

        copy_btn = ft.IconButton(ft.Icons.COPY, on_click=copy_to_clipboard, tooltip="In Zwischenablage kopieren")
        print_btn = ft.IconButton(ft.Icons.PRINT, on_click=print_to_pdf, tooltip="Als A4-PDF drucken")

        back_btn_export = ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate_to("home"))

        return ft.Column([
            ft.Row([
                back_btn_export,
                ft.Text("Daten Exportieren", size=20, weight=ft.FontWeight.BOLD)
            ]),
            selection_tile,
            ft.Row([
                ft.Text("3. Ergebnis (Copy-Paste / Drucken)", weight=ft.FontWeight.BOLD),
                ft.Row([copy_btn, print_btn])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            export_text
        ], expand=True, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    # --- Quick Add Popover ---
    def open_quick_add(patient_id):
        patient = dm.get_patient_by_id(patient_id)
        
        target_field = ft.RadioGroup(content=ft.Column([
            ft.Radio(value="verlauf", label="Verlauf"),
            ft.Radio(value="diagnosen", label="Diagnosen"),
            ft.Radio(value="diagnostik", label="Diagnostik"),
            ft.Radio(value="probleme_aufgaben", label="Probleme/Aufgaben"),
        ]), value="verlauf")
        
        text_input = ft.TextField(label="Information", multiline=True)
        
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

    # --- Layout ---
    content_area = ft.Container(expand=True, padding=20)
    
    layout = ft.Row([
        ft.Container(sidebar_container, bgcolor=ft.Colors.SURFACE_CONTAINER, padding=10),
        ft.VerticalDivider(width=1),
        content_area
    ], expand=True)

    def update_view():
        view_name = page.session.store.get("current_view") or "home"
        if view_name == "home":
            content_area.content = get_home_view()
        elif view_name == "patient":
            content_area.content = get_patient_view(page.session.store.get("current_patient_id"))
        elif view_name == "export":
            content_area.content = get_export_view()
        page.update()

    page.add(layout)
    update_sidebar()
    update_view()

if __name__ == "__main__":
    ft.run(main)
