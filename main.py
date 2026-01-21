import flet as ft
import os
from data_manager import DataManager, Patient
from components.sidebar import Sidebar
from components.dialogs import open_quick_add_dialog
from views.home_view import get_home_view
from views.patient_view import get_patient_view
from views.export_view import get_export_view

def main(page: ft.Page):
    # App Konfiguration
    page.title = "Patienten Übersicht"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1200
    page.window.height = 800
    page.window.icon = "logo.png"
    
    # Data Manager initialisieren
    dm = DataManager("patients.yaml")

    def navigate_to(view_name, patient_id=None):
        page.session.store.set("current_view", view_name)
        if patient_id:
            page.session.store.set("current_patient_id", patient_id)
        update_view()

    def add_new_patient():
        new_patient = Patient(name="Neuer Patient")
        dm.add_patient(new_patient)
        sidebar.update_sidebar()
        navigate_to("patient", new_patient.id)

    def on_quick_add(patient_id):
        open_quick_add_dialog(page, dm, patient_id)

    # UI Komponenten
    sidebar = Sidebar(dm, on_navigate=navigate_to, on_add_patient=add_new_patient)
    content_area = ft.Container(expand=True, padding=20)
    
    layout = ft.Row([
        ft.Container(sidebar, bgcolor=ft.Colors.SURFACE_CONTAINER, padding=10),
        ft.VerticalDivider(width=1),
        content_area
    ], expand=True)

    def update_view():
        view_name = page.session.store.get("current_view") or "home"
        
        if view_name == "home":
            content_area.content = get_home_view(
                dm, 
                on_navigate=navigate_to, 
                on_quick_add=on_quick_add,
                update_sidebar=sidebar.update_sidebar
            )
        elif view_name == "patient":
            pid = page.session.store.get("current_patient_id")
            content_area.content = get_patient_view(
                dm, 
                pid, 
                on_navigate=navigate_to,
                update_sidebar=sidebar.update_sidebar
            )
        elif view_name == "export":
            content_area.content = get_export_view(page, dm, on_navigate=navigate_to)
            
        page.update()

    page.add(layout)
    update_view()

if __name__ == "__main__":
    # Assets Verzeichnis für Logo etc.
    assets_path = os.path.dirname(os.path.abspath(__file__))
    ft.run(main, assets_dir=assets_path)
