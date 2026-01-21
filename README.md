# Patienten Tool

Ein leichtgewichtiges Flet-basiertes Werkzeug zur Verwaltung von Patientenübersichten auf Intensivstationen.

## Features
- **Patientenverwaltung:** Einfaches Hinzufügen, Bearbeiten und Ausblenden von Patienten.
- **Datenmodell:** Speicherung in einer lokalen `patients.yaml` (DRY & Pythonisch via Pydantic).
- **Quick-Add:** Schnelles Hinzufügen von Informationen mit tagesaktuellem Zeitstempel.
- **Export:** Strukturierter Plain-Text Export für Übergaben.
- **PDF-Druck:** Kompakter A4-PDF-Export mit intelligenter Seitenumbruch-Logik.
- **Desktop-Ready:** Gebaut für Windows als Single-File EXE via GitHub Actions.

## Projektstruktur
Das Projekt folgt einer modularen Architektur für bessere Wartbarkeit:

- `main.py`: Einstiegspunkt und App-Orchestrierung.
- `data_manager.py`: Datenmodell (Pydantic) und Persistenzschicht.
- `utils.py`: Hilfsfunktionen für PDF, Export-Formatierung und Dateipfade.
- `components/`: Wiederverwendbare UI-Komponenten (Sidebar, Dialoge).
- `views/`: Definition der Hauptansichten (Home, Patient Details, Export).
- `tests/`: Automatisierte Tests für Logik und Utilities.

## Installation & Entwicklung

Voraussetzung: [uv](https://github.com/astral-sh/uv) ist installiert.

1. Abhängigkeiten installieren:
   ```bash
   uv sync
   ```

2. App im Entwicklungsmodus starten:
   ```bash
   uv run flet run main.py
   ```

3. Tests ausführen:
   ```bash
   uv run pytest
   ```

## Build (Windows EXE)

Der Build erfolgt automatisch via GitHub Actions bei jedem neuen Tag (z.B. `v1.7`).
Um manuell zu bauen:
```bash
uv run flet pack main.py --name "PatientenTool" --icon "logo.png" --add-data "logo.png;."
```

## Lizenz
MIT
