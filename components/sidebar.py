import flet as ft
from data_manager import DataManager
from typing import Callable

class Sidebar(ft.Column):
    def __init__(self, dm: DataManager, on_navigate: Callable, on_add_patient: Callable):
        super().__init__(expand=True)
        self.dm = dm
        self.on_navigate = on_navigate
        self.on_add_patient = on_add_patient
        
        self.sidebar_fixed = ft.Column()
        self.sidebar_scrollable = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
        self.controls = [
            self.sidebar_fixed,
            self.sidebar_scrollable
        ]
        self.width = 220
        self.update_sidebar()

    def update_sidebar(self):
        active_patients = self.dm.get_active_patients()
        sorted_patients = self.dm.sort_patients(active_patients)
        
        def on_sidebar_hover(e, container):
            container.bgcolor = ft.Colors.BLACK12 if e.data == "true" else None
            try:
                if container.page:
                    container.update()
            except Exception:
                pass

        def create_sidebar_item(icon_name, text, on_tap_handler):
            c = ft.Container(
                content=ft.Row([
                    ft.Icon(icon_name, size=18) if icon_name else ft.Container(),
                    ft.Text(text, size=13)
                ], spacing=10),
                padding=ft.padding.symmetric(vertical=3, horizontal=8),
                border_radius=8,
            )
            c.on_hover = lambda e: on_sidebar_hover(e, c)
            return ft.GestureDetector(
                content=c,
                on_tap=on_tap_handler,
                mouse_cursor=ft.MouseCursor.CLICK
            )
        
        fixed_items = [
            create_sidebar_item(ft.Icons.HOME, "Übersicht", lambda _: self.on_navigate("home")),
            ft.Divider(),
            create_sidebar_item(ft.Icons.ADD, "Patient hinzufügen", lambda _: self.on_add_patient()),
            ft.Divider(),
            ft.Text("Aktive Patienten", size=12, weight=ft.FontWeight.BOLD),
        ]
        
        patient_items = []
        for p in sorted_patients:
            patient_items.append(
                create_sidebar_item(
                    None, 
                    f"{p.name} ({p.bettplatz})", 
                    lambda _, pid=p.id: self.on_navigate("patient", pid)
                )
            )
            
        self.sidebar_fixed.controls = fixed_items
        self.sidebar_scrollable.controls = patient_items
        
        # Nur updaten, wenn das Control bereits auf der Seite aktiv ist
        try:
            if self.page:
                self.update()
        except Exception:
            pass
